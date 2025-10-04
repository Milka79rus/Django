from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from logistic.models import Product, Stock
from logistic.serializers import ProductSerializer, StockSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']  # поиск продуктов по названию и описанию


class StockViewSet(ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['positions__product__title', 'positions__product__description']
    # поиск складов по продуктам (название или описание)
