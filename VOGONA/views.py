from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from product.models import Product


def home(request):
    products = Product.objects.all().filter(is_available=True)
    data = {
        'products' : products
    }
    return render(request, 'home.html', data)