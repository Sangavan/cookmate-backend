from django.db import models


class Recipe(models.Model):
    """A single recipe, e.g. 'Chicken Curry'."""

    # Source tracking (so we know which came from TheMealDB)
    external_id = models.CharField(
        max_length=50, unique=True, null=True, blank=True,
        help_text="ID from TheMealDB, if imported"
    )

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)   # e.g. Seafood, Dessert
    area = models.CharField(max_length=100, blank=True)       # cuisine, e.g. Italian
    thumbnail = models.URLField(blank=True)                   # image URL
    youtube_url = models.URLField(blank=True)
    tags = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """An ingredient line for a recipe, e.g. '200g Chicken'."""

    recipe = models.ForeignKey(
        Recipe, related_name='ingredients', on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    measure = models.CharField(max_length=100, blank=True)   # e.g. "2 tbsp"
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.measure} {self.name}".strip()


class Step(models.Model):
    """One cooking step, used for the voice 'next step' feature."""

    recipe = models.ForeignKey(
        Recipe, related_name='steps', on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField(default=0)
    instruction = models.TextField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Step {self.order}: {self.instruction[:40]}..."


class Favorite(models.Model):
    """Links a user to a recipe they favorited."""

    user = models.ForeignKey(
        'auth.User', related_name='favorites', on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, related_name='favorited_by', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')   # can't favorite the same recipe twice

    def __str__(self):
        return f"{self.user.username} ♥ {self.recipe.name}"