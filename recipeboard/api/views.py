from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .feed import vsm_get_docs, apply_feedback, get_cuisine_docs
from .models import User, Recipe

class RecipeListView(APIView):
    def get(self, request, *args, **kwargs):
        '''Get user's feed
        '''
        if 'userId' not in request.GET:
            return Response({'error': "user_id not specified"}, status=status.HTTP_400_BAD_REQUEST)
        if 'n' not in request.GET:
            return Response({'error': "n not specified"}, status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(id=int(request.GET['userId'])).exists():
            return Response({'error': f"User with userId={int(request.GET['userId'])} not found"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id=int(request.GET['userId']))
        response_data = [recipe.get_dict(keys=['id', 'title', 'url', 'directions']) for recipe in vsm_get_docs(user, n=int(request.GET['n']))]
        
        return Response({'data':response_data}, status=status.HTTP_200_OK)

class UserDetailView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        '''Get user name, likes, dislikes
        '''
        if not User.objects.filter(id=user_id).exists():
            return Response({'error': f"User with userId={user_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(id=user_id)

        response_data = {}
        response_data['userId'] = user.id
        response_data['name'] = user.name
        response_data['likes'] = [recipe.get_dict(keys=['id', 'title']) for recipe in user.likes.all()]
        response_data['dislikes'] = [recipe.get_dict(keys=['id', 'title']) for recipe in user.dislikes.all()]

        return Response({'data': response_data}, status=status.HTTP_200_OK)
    
    def post(self, request, user_id, *args, **kwargs):
        '''Apply feedback
        '''
        if 'recipeId' not in request.data:
            return Response({'error': "recipeId not specified"}, status=status.HTTP_400_BAD_REQUEST)
        if 'like' not in request.data:
            return Response({'error': "like not specified"}, status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(id=user_id).exists():
            return Response({'error': f"User with userId={user_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        if not Recipe.objects.filter(id=request.data['recipeId']).exists():
            return Response({'error': f"Recipe with recipeId={request.data['recipeId']} not found"}, status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(id=user_id)
        recipe = Recipe.objects.get(id=request.data['recipeId'])
        apply_feedback(user, recipe, request.data['like']==1)

        return Response({}, status=status.HTTP_200_OK)

class UserListView(APIView):
    
    def post(self, request, *args, **kwargs):
        '''Create user and initalize likes
        '''
        if 'cuisine' not in request.data:
            return Response({'error': "cuisine not specified"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User(name=request.data.get('name', ''))
        user.save()
        cuisine_recipes = get_cuisine_docs(request.data['cuisine'])
        for cuisine_recipe in cuisine_recipes:
            apply_feedback(user, cuisine_recipe)

        return Response({'data':{'userId': user.id}}, status=status.HTTP_200_OK)