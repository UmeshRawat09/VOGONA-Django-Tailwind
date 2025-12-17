from django.shortcuts import render,get_object_or_404, redirect
from .models import Product,Variation, ReviewRating
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ReviewRatingForm
from django.contrib import messages
from orders.models import OrderProduct


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
    
    if request.user.is_authenticated:
        try:
            order_product = OrderProduct.objects.filter(user=request.user, product_id=product.id).exists()

        except OrderProduct.DoesNotExist:
            order_product = None
    else:
        order_product = None

    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
    
    data = {
        'product' : product,
        'cart_item' : cart_item,
        'order_product': order_product,
        'reviews' : reviews,
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

def product_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewRatingForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewRatingForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            else:
                messages.error(request, 'Invalid form data.')
    return redirect(url)

