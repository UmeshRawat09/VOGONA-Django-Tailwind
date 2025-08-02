from django.shortcuts import render,get_object_or_404
from .models import Product,Variation
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse

# Create your views here.

# Products details

def all_products(request, category_slug=None):
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        page = Paginator(products, 6)
        page_number = request.GET.get('page')
        page_products = page.get_page(page_number)
        products_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        page = Paginator(products, 6)
        page_number = request.GET.get('page')
        page_products = page.get_page(page_number)
        products_count = products.count()

    
    
    data = {
        'products' : page_products,
        'products_count' : products_count,
    }
    return render(request, 'products/all_products.html', data)


# Single Product details

def product_detail(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        cart_item = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()

    except Exception as e:
        raise e
    
    data = {
        'product' : product,
        'cart_item' : cart_item,
    }
    return render(request, 'products/product_detail.html', data)


def search(request):
    if 'product_search' in request.GET:
        name = request.GET.get('product_search')
        if name:
            products = Product.objects.filter(Q(company_name__icontains=name) | Q(product_name__icontains=name) | Q(discription__icontains=name) | Q(price__icontains=name))
            page = Paginator(products, 6)
            page_number = request.GET.get('page')
            page_products = page.get_page(page_number)
            products_count = products.count()

    data ={
        'products' : page_products,
        'products_count' : products_count,
    }
    return render(request, 'products/all_products.html', data)