from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm
from .models import Account, UserProfile
from .forms import UserForm, UserProfileForm
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from cart.views import _cart_id
from cart.models import Cart, CartItem
import requests

from orders.models import Order, OrderProduct

# Create your views here.

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            current_site = get_current_site(request)
            subject = 'Verify Your Email Address'
            message = render_to_string('accounts/verification_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()           
            return redirect('/account/sign_up/?command=verification&email='+email)

    else:
        form = SignUpForm()
    data = {
        'form' : form
    }
    return render(request, 'accounts/sign_up.html', data)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            session_cart_id = _cart_id(request)
            auth.login(request, user)
            try:
                cart = Cart.objects.get(cart_id=session_cart_id)
                
                if CartItem.objects.filter(cart=cart).exists():
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variation = []
                    for item in cart_item:
                        variation = item.variation.all()
                        product_variation.append(list(variation))
                    
                    cart_item = CartItem.objects.filter(user=user)
                    existing_variation_list = []
                    ids=[]
                    for item in cart_item:
                        existing_variation = item.variation.all()
                        existing_variation_list.append(list(existing_variation))
                        ids.append(item.id)
                    
                    for p_variation in product_variation:
                        if p_variation in existing_variation_list:
                            index = existing_variation_list.index(p_variation)
                            item_id = ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()


            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER', '/')
            try:
                query = requests.utils.urlparse(url).query
                param = dict(x.split('=') for x in query.split('&'))
                if 'next' in param:
                    next = param['next']
                    return redirect(next)
            except:
                return redirect('home')
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')
        
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You'r logged out")
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated.")
        return redirect('login')
    else:
        messages.error(request, "Invalid activation link")
        return redirect('sign_up')
    
@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    context = {
        'orders_count': orders_count,
    }
    return render(request, 'accounts/dashboard.html', context)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            subject = 'Reset Password'
            message = render_to_string('accounts/reset_password_message.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgot_password')
    
    return render(request, 'accounts/forgot_password.html')

def reset_password_message(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        return redirect('reset_password')
    else:
        messages.error(request, 'Link has been expired!')
        return redirect('login')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfuly')
            return redirect('login')
        else:
            messages.error(request, 'password do not match!')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')
    

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }

    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        'user_form' : user_form,
        'profile_form' : profile_form,
        'user_profile' : user_profile,
    }
    
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        if new_password == confirm_password:
            succes = user.check_password(current_password)
            if succes:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Confirm Password does not match!')
            return redirect('change_password')
        
    return render(request, 'accounts/change_password.html')


login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)

    sub_total = 0
    for i in order_detail:
        sub_total += i.product_price * i.quantity

    context = {
        'order_detail' : order_detail,
        'order' : order,
        'sub_total' : sub_total,
    }

    return render(request, 'accounts/order_detail.html', context)
