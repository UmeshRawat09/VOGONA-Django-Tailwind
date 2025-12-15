from django.shortcuts import render, redirect
from cart.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from product.models import Product
import datetime
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.
def place_order(request, total=0, quantity=0):
    current_user = request.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('all_products')
    
    grand_total = 0
    tax =0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2*total)/100
    grand_total = total+tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.name = form.cleaned_data['name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            today = datetime.date.today()
            yr = int(today.strftime('%Y'))
            mt = int(today.strftime('%m'))
            dt = int(today.strftime('%d'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax': tax,
                'grand_total' : grand_total,
            }

            return render(request, 'orders/payments.html', context)
    else:
        return redirect('buy')



def payments(request):
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        payment_method = request.POST.get('payment_method')
        status = 'completed'

        try:
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
        except Order.DoesNotExist:
            return redirect('place_order')

        # Store transaction details inside Payment model
        payment = Payment.objects.create(
            user = request.user,
            payment_method = payment_method,
            amount_paid = order.order_total,
            status = status,
        )

        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variation.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variation.set(product_variation)
            orderproduct.save()

            # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # Clear cart
        cart_items.delete()


        subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html',{
            'user' : request.user,
            'order' : order,
        })
        to_email = request.user.email
        send_email = EmailMessage(subject, message, to=[to_email])
        send_email.send()

        return redirect('order_complete', order_number=order.order_number, payment_method=payment.payment_method)
    else:
        return redirect('buy')
    

def order_complete(request, order_number, payment_method):

    try:
        order = Order.objects.get(order_number=order_number)
        order_products = OrderProduct.objects.filter(order_id=order.id)

        sub_total = 0
        for i in order_products:
            sub_total += i.product_price * i.quantity

        data = {
            'order' : order,
            'order_products' : order_products,
            'payment_method' : payment_method,
            'sub_total' : sub_total,
        }

        return render(request, 'orders/order_complete.html', data)
    
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

