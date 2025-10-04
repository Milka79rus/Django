from rest_framework import serializers
from .models import Product, Stock, StockProduct

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']


    def create(self, validated_data):
        positions_data = validated_data.pop('positions', [])
        stock = super().create(validated_data)

        for item in positions_data:
            product_data = item.pop('product')
            product, _ = Product.objects.get_or_create(**product_data)
            StockProduct.objects.create(stock=stock, product=product, **item)

        return stock

    def update(self, instance, validated_data):
        positions_data = validated_data.pop('positions', [])
        stock = super().update(instance, validated_data)

        for item in positions_data:
            product_data = item.pop('product')
            product, _ = Product.objects.get_or_create(**product_data)
            StockProduct.objects.update_or_create(
                stock=stock,
                product=product,
                defaults={'quantity': item['quantity'], 'price': item['price']}
            )

        return stock