from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.show_catalog, name='catalog'),
    path('catalog/<slug:slug>/', views.show_product, name='phone_detail'),
]
