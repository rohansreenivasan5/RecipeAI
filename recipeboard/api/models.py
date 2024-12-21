from django.db import models

# Create your models here.

class Recipe(models.Model):
    file_name = models.CharField(max_length=64, default='')
    title = models.CharField(max_length=64, default='')
    url = models.URLField()
    directions = models.TextField()
    reviews = models.TextField()

    def get_text(self):
        return self.title + '\n' + self.directions + '\n' + self.reviews
    
    def get_dict(self, keys: list):
        recipe_dict = {}
        recipe_dict['id'] = self.id
        recipe_dict['file_name'] = self.file_name
        recipe_dict['title'] = self.title
        recipe_dict['url']=self.url
        recipe_dict['directions'] = self.directions
        recipe_dict['reviews']=self.reviews
        return {key: recipe_dict[key] for key in keys}

class User(models.Model):
    name = models.CharField(max_length=64, default='')
    likes = models.ManyToManyField(Recipe, related_name='liked_users')
    dislikes = models.ManyToManyField(Recipe, related_name='disliked_users')