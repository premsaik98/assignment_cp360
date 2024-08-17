from django.contrib import admin
from .models import Category, Product


class CategoryAdmin(admin.ModelAdmin):
    class Meta:
        model = Category
        list_display = ('name',)
        fields = ('name,')


class ProductAdmin(admin.ModelAdmin):
    class Meta:
        model = Product
        list_display = ['title', 'description', 'category__name' ,'price', 'status', 'created_at']
        fields = '__all__'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
