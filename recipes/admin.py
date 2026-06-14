from django.contrib import admin
from .models import Recipe, Ingredient, Step, Favorite


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1


class StepInline(admin.TabularInline):
    model = Step
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'area', 'external_id')
    list_filter = ('category', 'area')
    search_fields = ('name',)
    inlines = [IngredientInline, StepInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created_at')