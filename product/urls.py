from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='all_products'),
    path('category/<slug:category_slug>/', views.all_products, name='product_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>', views.product_review, name='product_review')
]
