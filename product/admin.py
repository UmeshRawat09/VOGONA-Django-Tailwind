from django.contrib import admin
from .models import Product, Variation, ReviewRating

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    list_display_links = ('company_name', 'product_name')
    prepopulated_fields = {'slug' : ('product_name', 'company_name')}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'created_date', 'is_active')
    list_editable = ('is_active',)
    # list_filter = ('product', 'variation_category', 'variation_value')

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
