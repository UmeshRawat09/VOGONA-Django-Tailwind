from django.http import HttpResponse
from django.shortcuts import render
from product.models import Product


def home(request):
    products = Product.objects.filter(price__gt=1000)
    data = {
        'products' : products
    }
    return render(request, 'home.html', data)