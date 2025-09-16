from django.urls import path
from .views import recipe_view

urlpatterns = [
    path('<str:dish>/', recipe_view, name='recipe'),
]