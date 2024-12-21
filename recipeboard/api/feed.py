import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
import random

from .models import User, Recipe
from recipeboard.settings import SIMILARITY_FUNCTION

scores = None

def load_recipes(directory='../data/allrecipes/recipes'):
    '''
    Add .txt files to `Recipe` table. Called during startup in .apps.py
    '''

    for file_name in os.listdir(directory):
        if not file_name.endswith('.txt') or Recipe.objects.filter(file_name=file_name).exists():
            continue
        with open(os.path.join(directory, file_name), 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content.splitlines()) != 4:
                continue
            title, url, directions, reviews = content.splitlines()
            recipe = Recipe(file_name=file_name, title=title, url=url, directions=directions, reviews=reviews)
            recipe.save()

def calculate_scores():
    global scores
    recipes = [recipe.get_text() for recipe in Recipe.objects.all()]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(recipes)
    if SIMILARITY_FUNCTION == 'tf-idf':
        scores = cosine_similarity(tfidf_matrix)
    elif SIMILARITY_FUNCTION == 'dot-product':
        scores = (tfidf_matrix @ tfidf_matrix.T).toarray()

def vsm_get_docs(user: User, relevant=True, n=10) -> List[Recipe]:
    # Make sure scores are calculated
    if not isinstance(scores, np.ndarray):
        calculate_scores()

    # `user_likes` and `user_dislikes` are `Recipe` instances. See .model.py
    user_likes = [recipe for recipe in user.likes.all()]
    user_dislikes = [recipe for recipe in user.dislikes.all()]
    
    # `similarity_scores` is an 1D numpy array
    if user_likes:
        liked_doc_indices = [recipe.id - 1 for recipe in user_likes]
        disliked_doc_indices = [recipe.id - 1 for recipe in user_dislikes]
        similarity_scores = 3 * np.mean(scores[liked_doc_indices], axis=0) - np.mean(scores[disliked_doc_indices], axis=0)
    else:
        similarity_scores = np.mean(scores, axis=0)
    
    relevant_docs = [Recipe.objects.get(id=idx+1) for idx in np.argsort(similarity_scores)[::-1]]
    if relevant:
        return relevant_docs[:n]
    else:
        return relevant_docs[:n:-1]
    
def apply_feedback(user: User, doc: Recipe, like=True):
    if like:
        user.likes.add(doc)
    else:
        user.dislikes.add(doc)

def get_cuisine_docs(cuisine_type: str, n=3) -> List[Recipe]:
    # Make sure scores are loaded
    if not isinstance(scores, np.ndarray):
        calculate_scores()

    relevant_docs = []
    for recipe in Recipe.objects.all():
        if cuisine_type.lower() in recipe.title.lower():
            relevant_docs.append(recipe)
    return random.sample(relevant_docs, k=n)

'''
if not User.objects.filter(id=1).exists():
    user = User()
    user.save()
else:
    user = User.objects.get(id=1)
doc_1 = Recipe.objects.get(file_name="6687.txt")
doc_2 = Recipe.objects.get(file_name="6697.txt")
doc_3 = Recipe.objects.get(file_name="6732.txt")
apply_feedback(user, doc_1, like=True)
print("Recommended docs:", [recipe.title for recipe in vsm_get_docs(user)])
apply_feedback(user, doc_2, like=True)
print("Recommended docs:", [recipe.title for recipe in vsm_get_docs(user)])
apply_feedback(user, doc_3, like=True)
print("Recommended docs:", [recipe.title for recipe in vsm_get_docs(user)])
print("Cuisine-specific docs:", [recipe.title for recipe in get_cuisine_docs("Italian")])
'''