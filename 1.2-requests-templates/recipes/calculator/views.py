from django.shortcuts import render
from django.http import HttpResponse

DATA = {
    'omlet': {
        'яйца, шт': 2,
        'молоко, л': 0.1,
        'соль, ч.л.': 0.5,
    },
    'pasta': {
        'макароны, г': 0.3,
        'сыр, г': 0.05,
    },
    'buter': {
        'хлеб, ломтик': 1,
        'колбаса, ломтик': 1,
        'сыр, ломтик': 1,
        'помидор, ломтик': 1,
    },
}


def recipe_view(request, dish):
    recipe = DATA.get(dish)  # ищем рецепт по ключу
    if recipe is None:
        context = {'recipe': {}}  # пустой словарь => сработает {% empty %}
    else:
        servings = int(request.GET.get('servings', 1))  # по умолчанию 1
        context = {
            'recipe': {
                ingredient: amount * servings
                for ingredient, amount in recipe.items()
            }
        }
    return render(request, 'calculator/index.html', context)