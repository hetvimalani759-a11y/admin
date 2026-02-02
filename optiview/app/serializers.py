from rest_framework import serializers
from orders_admin.models import Order, OrderItem, Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['user', 'status', 'total_amount', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=product.price
            )
        order.calculate_total()
        return order
