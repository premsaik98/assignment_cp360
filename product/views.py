from rest_framework import permissions
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import ProductSerializer


class IsAuthenticatedAndActive(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class ProductView(generics.GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            products = Product.objects.all()
        elif request.user.is_staff:
            products = Product.objects.all()
        else:
            products = Product.objects.filter(uploaded_by=request.user)
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(uploaded_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "You do not have permission to create products."}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs.get('pk'))
        if request.user.is_superuser or (request.user.is_staff and product.status == 'pending'):
            status_update = request.data.get('status')
            if status_update in ['approved', 'rejected']:
                product.status = status_update
                product.save()
                return Response({'status': f'Product {status_update}'})
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        elif product.uploaded_by == request.user and product.status in ['rejected', 'cancelled']:
            product.title = request.data.get('title', product.title)
            product.description = request.data.get('description', product.description)
            product.price = request.data.get('price', product.price)
            product.save()
            return Response(self.get_serializer(product).data)
        return Response({"detail": "You do not have permission to update this product."}, status=status.HTTP_403_FORBIDDEN)


    def delete(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs.get('pk'))
        if request.user.is_superuser or product.uploaded_by == request.user:
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "You do not have permission to delete this product."}, status=status.HTTP_403_FORBIDDEN)
