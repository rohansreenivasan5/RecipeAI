from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

@receiver(post_migrate)
def add_initial_data(sender, **kwargs):
    from .feed import load_recipes
    load_recipes()