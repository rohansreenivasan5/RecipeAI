from django.urls import path
from .views import RecipeListView, UserListView, UserDetailView

urlpatterns = [
    path('recipe/', RecipeListView.as_view()),
    path('user/', UserListView.as_view()),
    path('user/<int:user_id>/', UserDetailView.as_view()),
]