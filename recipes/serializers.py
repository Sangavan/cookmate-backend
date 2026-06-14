from rest_framework import serializers
from .models import Recipe, Ingredient, Step, Favorite


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measure', 'order']


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['id', 'order', 'instruction']


class RecipeListSerializer(serializers.ModelSerializer):
    """Lightweight version for the recipe list screen (no ingredients/steps)."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'category', 'area', 'thumbnail']


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Full version for the recipe detail + cooking screen."""

    ingredients = IngredientSerializer(many=True, read_only=True)
    steps = StepSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'category', 'area', 'thumbnail',
            'youtube_url', 'tags', 'ingredients', 'steps',
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeListSerializer(read_only=True)
    recipe_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'recipe', 'recipe_id', 'created_at']
        


from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user