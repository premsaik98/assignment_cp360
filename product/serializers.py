from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'created_at', 'updated_at', 'status']


    def update(self, instance, validated_data):


        request = self.context.get('request')
        if request and request.user.is_staff:
            status = validated_data.get('status')
            if status in ['approved', 'rejected']:
                instance.status = status
        elif request and not request.user.is_staff and not request.user.is_superuser:
            if instance.status in ['rejected', 'cancelled']:
                instance.title = validated_data.get('title', instance.title)
                instance.description = validated_data.get('description', instance.description)
                instance.price = validated_data.get('price', instance.price)
            else:
                raise serializers.ValidationError("You can only update products that are rejected or cancelled.")
        instance.save()
        return instance
