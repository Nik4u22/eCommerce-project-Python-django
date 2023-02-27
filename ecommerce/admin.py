from django.contrib import admin
from ecommerce.models import Product, Category, SizeVariant, ColorVariant
# Register your models here.

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(SizeVariant)
admin.site.register(ColorVariant)