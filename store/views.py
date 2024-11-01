from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from .models import Order, Shipping, PaymentReceipt,PaymentTag
import datetime

from ctypes import addressof
import datetime
import re
from django.http import JsonResponse
from django.shortcuts import redirect, render
#from numpy import product
from django.shortcuts import render, get_object_or_404 
from .models import *
import json
from .utils import cartData, cookieCart, guestOrder

# for userCreation
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages

# authenticate user
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def registerUser(request):
    form = CreateUserForm()

    if request.method=="POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            Customer.objects.create(user=User.objects.get(username=user), email=email)
            #Customer.objects.create(user=admin_user, email=admin_user.email)
            return redirect('login')

    context={'form':form}
    return render(request, 'store/register.html',context)

def loginUser(request):
    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, 'Incorrect username or password')
    context={}
    return render(request, 'store/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('store')

def store(request):

    admin_user=User.objects.get(username="admin")
    customer, created = Customer.objects.get_or_create(
        user=admin_user,
        defaults={'email': admin_user.email}
    )

    products = Product.objects.all()
    context = {'products':products}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    order_products = data['order_products']
    order =  data['order']

    context = {'order_products':order_products, 'order':order}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    order_products = data['order_products']
    order =  data['order']
    try:
        payment_tags=PaymentTag.objects.all()
        for tag in payment_tags:
            payment_tag=tag
    except:
        messages.error(request, f'No tag has been set')
    print(payment_tag.paypal)
    context = {'order_products':order_products, 'order':order, "payment_tag":payment_tag}
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    # print(action, productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, cart_complete=False)
    # order_products = order.order_product_set.all()
    order_product, created = Order_Product.objects.get_or_create(order=order, product=product)

    if action=="add":
        order_product.quantity +=1
    elif action =="remove":
        order_product.quantity -=1
    order_product.save()
    cart_total = order.get_total_quantity
    cart_totalPrice = order.get_total_price
    
    if order_product.quantity<=0:
        order_product.delete()
    # print(order_product.quantity, order_product.product.name)

    return JsonResponse({'cart_total':cart_total,'cart_totalPrice':cart_totalPrice,'quantity':order_product.quantity, 'unitprice':order_product.product.price}, safe=False)

"""
def process_order(request):
    data = json.loads(request.body)
    transaction_id = datetime.datetime.now().timestamp()
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, cart_complete=False)

    else:
        order = guestOrder(request, data)
        

    total = float(data['userFormData']['total'])
    order.transaction_id = transaction_id
    # print(total, order.get_total_price)
    # check the total from the front end is it same as from the backend
    if total==order.get_total_price:
        order.cart_complete = True
    order.save()

    if order.shipping == True:
        Shipping.objects.create(
            order= order,
            address= data['shippingInfo']['address'],
            city= data['shippingInfo']['city'],
            state= data['shippingInfo']['state'],
            zipcode= data['shippingInfo']['zipcode'],
        )   
    return JsonResponse('Payment submitted', safe=False)

"""
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product
    }
    return render(request, 'store/product_detail.html', context)


from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
import datetime
from uuid import uuid4

@require_http_methods(["POST"])
def process_order(request):
    try:
        # Get or create order based on user authentication status
        order = get_or_create_order(request)
        if not order:
            messages.error(request, 'No active order found')
            return redirect('checkout')

        # Validate form data
        if not validate_form_data(request):
            return redirect('checkout')

        # Process the order
        process_order_details(request, order)

        messages.success(request, 'Order submitted successfully! We will process your payment shortly.')
        return redirect('order_confirmation', order_id=order.id)

    except ValidationError as e:
        messages.error(request, str(e))
        return redirect('checkout')
    except Exception as e:
        messages.error(request, f'An error occurred while processing your order: {str(e)}')
        return redirect('checkout')

def get_or_create_order(request):
    """Get or create order for both authenticated and guest users."""
    if request.user.is_authenticated:
        customer = request.user.customer
        # Try to get order by ID from session
        order_id = request.session.get('order_id')
        if order_id:
            try:
                return Order.objects.get(id=order_id, customer=customer)
            except Order.DoesNotExist:
                pass
        
        # Look for incomplete cart
        try:
            return Order.objects.get(customer=customer, cart_complete=False)
        except Order.DoesNotExist:
            return None
    else:
        # Handle guest user
        order_id = request.session.get('order_id')
        if order_id:
            try:
                return Order.objects.get(id=order_id, guest_email=request.session.get('guest_email'))
            except Order.DoesNotExist:
                pass
        
        # Create new guest order if none exists
        guest_email = request.POST.get('email')
        if not guest_email:
            messages.error(request, 'Email is required for guest checkout')
            return None
            
        order = Order.objects.create(
            guest_email=guest_email,
            guest_token=str(uuid4())  # Generate unique token for guest orders
        )
        request.session['order_id'] = order.id
        request.session['guest_email'] = guest_email
        return order

def validate_form_data(request):
    """Validate all required form fields."""
    required_fields = ['name', 'email', 'address', 'city', 'state', 'zipcode']
    for field in required_fields:
        if not request.POST.get(field):
            messages.error(request, f'{field.title()} is required')
            return False

    # Validate payment method
    payment_method = request.POST.get('payment_method')
    if payment_method not in ['paypal', 'venmo']:
        messages.error(request, 'Invalid payment method')
        return False

    # Validate receipt upload
    if 'receipt' not in request.FILES:
        messages.error(request, 'Payment receipt is required')
        return False

    return True

def process_order_details(request, order):
    """Process and save order details."""
    # Update order details
    order.transaction_id = datetime.datetime.now().timestamp()
    order.payment_method = request.POST.get('payment_method')
    order.payment_status = 'processing'
    order.cart_complete = True
    order.customer_name = request.POST.get('name')
    order.customer_email = request.POST.get('email')
    order.save()

    # Create payment receipt
    PaymentReceipt.objects.create(
        order=order,
        payment_method=request.POST.get('payment_method'),
        receipt_image=request.FILES['receipt']
    )

    # Create or update shipping information
    shipping_data = {
        'order': order,
        'address': request.POST.get('address'),
        'city': request.POST.get('city'),
        'state': request.POST.get('state'),
        'zipcode': request.POST.get('zipcode'),
        'country': request.POST.get('country', '')
    }
    
    Shipping.objects.update_or_create(
        order=order,
        defaults=shipping_data
    )

    # Clear session data for guest users
    if not request.user.is_authenticated:
        request.session.pop('order_id', None)
        request.session.pop('guest_email', None)

# You'll also need an order confirmation view
def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        if request.user.is_authenticated and order.customer != request.user.customer:
            messages.error(request, 'Unauthorized access')
            return redirect('home')
            
        context = {
            'order': order,
            'shipping': order.shipping_set.first() if order.shipping else None,
            'payment_receipt': order.payment_receipt
        }
        return render(request, 'store/order_confirmation.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('home')
    


def shipping_policy(request):
    return render(request, 'store/shipping_policy.html')

def return_policy(request):
    return render(request, 'store/return_policy.html')

def terms(request):
    return render(request, 'store/terms.html')