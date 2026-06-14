from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Recipe, Favorite
from .serializers import (
    RecipeListSerializer,
    RecipeDetailSerializer,
    FavoriteSerializer,
)


class RecipeListView(generics.ListAPIView):
    """
    GET /api/recipes/
    Lists all recipes. Supports:
      ?search=chicken   → search by name
      ?category=Seafood → filter by category
      ?area=Italian     → filter by cuisine
    """
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Recipe.objects.all()
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')
        area = self.request.query_params.get('area')

        if search:
            queryset = queryset.filter(name__icontains=search)
        if category:
            queryset = queryset.filter(category__iexact=category)
        if area:
            queryset = queryset.filter(area__iexact=area)

        return queryset


class RecipeDetailView(generics.RetrieveAPIView):
    """
    GET /api/recipes/<id>/
    Returns one recipe with full ingredients + steps.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    permission_classes = [permissions.AllowAny]


class FavoriteListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/favorites/   → list the logged-in user's favorites
    POST /api/favorites/   → add a favorite (send {"recipe_id": 5})
    """
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/favorites/<id>/  → remove a favorite
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    


from django.contrib.auth.models import User
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Body: {"username": "...", "email": "...", "password": "..."}
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]