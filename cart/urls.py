from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart , name='cart'),
    path('add_item/<int:product_id>/', views.add_item, name='add_item'),
    path('remove_item/<int:product_id>/<int:cart_item_id>/', views.remove_item, name='remove_item'),
    path('delete_item/<int:product_id>/<int:cart_item_id>/', views.delete_item, name='delete_item'),
    path('buy/', views.buy, name='buy'),
]
