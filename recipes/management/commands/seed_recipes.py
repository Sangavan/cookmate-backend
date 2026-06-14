import requests
import re
from django.core.management.base import BaseCommand
from recipes.models import Recipe, Ingredient, Step

API_BASE = "https://www.themealdb.com/api/json/v1/1"


class Command(BaseCommand):
    help = "Seed the database with recipes from TheMealDB"

    def add_arguments(self, parser):
        parser.add_argument(
            '--letters',
            type=str,
            default='abcdef',
            help='Which first-letters to fetch (default: abcdef)',
        )

    def handle(self, *args, **options):
        letters = options['letters']
        total_created = 0

        for letter in letters:
            self.stdout.write(f"Fetching meals starting with '{letter}'...")
            url = f"{API_BASE}/search.php?f={letter}"

            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
            except requests.RequestException as e:
                self.stderr.write(f"  Failed for '{letter}': {e}")
                continue

            meals = response.json().get('meals')
            if not meals:
                self.stdout.write(f"  No meals for '{letter}'")
                continue

            for meal in meals:
                created = self._save_meal(meal)
                if created:
                    total_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! {total_created} new recipes added."
        ))

    def _save_meal(self, meal):
        external_id = meal['idMeal']

        # Skip if we already imported this recipe
        if Recipe.objects.filter(external_id=external_id).exists():
            return False

        recipe = Recipe.objects.create(
            external_id=external_id,
            name=meal['strMeal'] or '',
            category=meal.get('strCategory') or '',
            area=meal.get('strArea') or '',
            thumbnail=meal.get('strMealThumb') or '',
            youtube_url=meal.get('strYoutube') or '',
            tags=meal.get('strTags') or '',
        )

        # ── Ingredients: TheMealDB stores them as strIngredient1..20 ──
        for i in range(1, 21):
            name = (meal.get(f'strIngredient{i}') or '').strip()
            measure = (meal.get(f'strMeasure{i}') or '').strip()
            if name:
                Ingredient.objects.create(
                    recipe=recipe,
                    name=name,
                    measure=measure,
                    order=i,
                )

        # ── Steps: split the instructions blob into individual steps ──
        instructions = meal.get('strInstructions') or ''
        steps = self._split_into_steps(instructions)
        for idx, step_text in enumerate(steps, start=1):
            Step.objects.create(
                recipe=recipe,
                order=idx,
                instruction=step_text,
            )

        self.stdout.write(f"  + {recipe.name} ({len(steps)} steps)")
        return True

    def _split_into_steps(self, text):
        """
        TheMealDB gives instructions as one big block.
        For our voice feature we split it into individual steps.
        Strategy: split on newlines first; if that gives too few,
        fall back to splitting on sentences.
        """
        text = text.strip()
        if not text:
            return []

        # Try splitting on line breaks (many recipes use them per step)
        parts = [p.strip() for p in re.split(r'[\r\n]+', text) if p.strip()]

        # If we only got 1 chunk, split into sentences instead
        if len(parts) <= 1:
            parts = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

        # Remove leading "STEP 1", "1.", numbering that some recipes include
        cleaned = []
        for p in parts:
            p = re.sub(r'^(step\s*\d+[:.\)]?\s*)', '', p, flags=re.IGNORECASE)
            p = re.sub(r'^\d+[:.\)]\s*', '', p)
            if p:
                cleaned.append(p)

        return cleaned