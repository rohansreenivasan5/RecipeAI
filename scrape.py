import requests
from bs4 import BeautifulSoup
import unicodedata
import warnings
import tqdm
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('window-size=1920x1080');

def crawl(link: str, steps: int):
    '''Look for links to recipe pages on allrecipes.com

    Args:
        link (str): Link to any page
        steps (int): Recursive calls

    Return:
        List of links to recipe pages
    '''
    # Check for available calls
    if steps == 0:
        return set()

    # Get page source html
    r = requests.get(link)
    if r.status_code != 200:
        return set()
    soup = BeautifulSoup(r.content, 'html.parser')

    # Follow links recursively
    links = set()
    for a in soup.find_all('a'):
        if 'https://www.allrecipes.com/' in a['href']:
            links.update(crawl(a['href'], steps - 1))
        if 'https://www.allrecipes.com/recipe/' in a['href']:
            links.add(a['href'])
    
    return links


def scrape(link: str):
    '''Extract a recipe page on allrecipes.com

    Args:
        link (str): Link to recipe page
    
    Returns:
        Dictionary containing title, description, overview, ingredients, nutrition-facts, reviews
    '''
    # Check if link directs to a recipe page
    if 'https://www.allrecipes.com/recipe/' not in link:
        raise ValueError('not a link to recipe page')

    # Get page source html
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@class="feedback-list__items"]')))
    except TimeoutException:
        # timeout = f'Timeout: {link}'
        # warnings.warn(timeout)
        return None
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Extract recipe id from link
    page = dict()
    page['id'] = link

    # Extract name
    page['name'] = soup.find('h1', {'class': 'article-heading type--lion'}).text

    # Extract description
    page['description'] = soup.find('p', {'class': 'article-subheading type--dog'}).text

    # Extract overview
    page['overview'] = {'prep-time': None, 'cook-time': None, 'additional-time': None, 'total-time': None, 'servings': None, 'yield': None}
    overview_list = soup.find('div', {'class': 'mm-recipes-details__content'})
    if overview_list:
        for overview_list_item in overview_list.find_all('div', {'class': 'mm-recipes-details__item'}):
            key_div, value_div = overview_list_item.find_all('div')
            key = key_div.text.replace(' ', '-').replace(':', '').lower()
            value = value_div.text
            page['overview'][key] = value

    # Extract ingredients
    page['ingredients'] = list()
    ingredients_list = soup.find('ul', {'class': 'mm-recipes-structured-ingredients__list'})
    if ingredients_list:
        for ingredient_list_item in ingredients_list.find_all('li'):
            ingredient = {'quantity': None, 'unit': None, 'name': None}
            for span in ingredient_list_item.find_all('span'):
                if 'data-ingredient-quantity' in span.attrs and span.text:
                    ingredient['quantity'] = span.text
                elif 'data-ingredient-unit' in span.attrs and span.text:
                    ingredient['unit'] = span.text
                elif 'data-ingredient-name' in span.attrs and span.text:
                    ingredient['name'] = span.text
            page['ingredients'].append(ingredient)

    # Extract directions
    page['directions'] = list()
    directions_list = soup.find('ol', {'class': 'comp mntl-sc-block mntl-sc-block-startgroup mntl-sc-block-group--OL'})
    if directions_list:
        for directions_list_items in directions_list.find_all('li'):
            for p in directions_list_items.find_all('p'):
                page['directions'].append(p.text[1:-1])

    # Extract nutrition-facts
    page['nutrition-facts'] = {'calories': None, 'fat': None, 'carbs': None, 'protein': None}
    nutrition_facts_table = soup.find('table', {'class': 'mm-recipes-nutrition-facts-summary__table'})
    if nutrition_facts_table:
        for nutrition_facts_tr in nutrition_facts_table.find_all('tr'):
            value_div, key_div = nutrition_facts_tr.find_all('td')
            value = float(value_div.text.replace('g', '').strip())
            key = key_div.text.lower()
            page['nutrition-facts'][key] = value

    # Extract review
    page['reviews'] = list()
    for reviews_div in soup.find_all('div', {'class': 'feedback__text'}):
        page['reviews'].append(reviews_div.text)

    return page

if __name__ == '__main__':

    # Crawl for links to recipe pages
    '''
    links = crawl('https://allrecipes.com/', steps=2)
    with open('data/allrecipes/links.txt', 'w') as f:
        for link in links:
            f.write(link)
            f.write('\n')
    '''
    
    # Scrape recipe pages
    def scrape_and_store(link: str):
        try:
            page = scrape(link.strip())
        except Exception as e:
            print(str(e), link)
            return
        if not page:
            return
        filename = page['id'].split('/')[4]
        with open(f'data/allrecipes/recipes/{filename}.txt', 'w') as recipe_f:
            content = str()
            content += page['name'] + '\n'
            content += page['id'] + '\n'
            content += ' '.join(page['directions']).replace('\n', '') + '\n'
            content += ' '.join(page['reviews']).replace('\n', '') + '\n'
            recipe_f.write(content)

    # Parallelize scraping
    links = list()
    with open('data/allrecipes/links.txt', 'r') as links_f:
        for link in links_f:
            links.append(link.strip())
    for link in tqdm.tqdm(links[1880:]):
        scrape_and_store(link)
    # with ThreadPoolExecutor(max_workers=16) as exe:
    #     exe.map(scrape_and_store, links)