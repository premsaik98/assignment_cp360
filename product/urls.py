from django.urls import path
from .views import ProductView, GenerateDummyProductsView, ExportProductsExcelView

urlpatterns = [
    path('products/', ProductView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductView.as_view(), name='product-detail'),
    path('products/generate-dummy/', GenerateDummyProductsView.as_view(), name='generate-dummy-products'),
    path('products/export-excel/', ExportProductsExcelView.as_view(), name='export-products-excel'),
]

