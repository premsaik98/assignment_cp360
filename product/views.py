import csv
import xlsxwriter

from io import BytesIO

from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from product.permissions import IsAdminUser

from .models import Product
from .serializers import ProductSerializer


from .tasks import generate_dummy_products

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



class GenerateDummyProductsView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        count = request.data.get('count', 1000)
        generate_dummy_products.delay(count)
        return JsonResponse({'status': 'Task initiated', 'message': f'{count} products will be generated.'})


class ExportProductsExcelView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        headers = ['ID', 'Title', 'Description', 'Price', 'Status', 'Uploaded By', 'Created At', 'Updated At']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)


        products = Product.objects.all().values_list(
            'id', 'title', 'description', 'price', 'status', 'uploaded_by__username', 'created_at', 'updated_at'
        )


        for row_num, row_data in enumerate(products, 1):
            for col_num, cell_data in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_data)

        workbook.close()
        output.seek(0)

        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="products.xlsx"'

        return response
