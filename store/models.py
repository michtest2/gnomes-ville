from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return self.email
    

class Product(models.Model):
    name =models.CharField(max_length=30)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=True)
    image = CloudinaryField('image', null=True, blank=True)
    #models.ImageField(upload_to='images/',null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    # OOP programming, making it as an attribute of the object
    # It also allows getter setter and deleters method
    # https://www.youtube.com/watch?v=jCzT9XFZ5bw
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Order(models.Model):
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    cart_complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=30, null=True)
    guest_email = models.EmailField(null=True, blank=True)
    guest_token = models.CharField(max_length=100, null=True, blank=True)

    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    payment_method = models.CharField(max_length=10, null=True, blank=True)
    payment_verified = models.BooleanField(default=False)
    def __str__(self):
        return str(self.id)

    @property
    def get_total_price(self):
        order_products = self.order_product_set.all()
        total_price = sum([order_product.get_total for order_product in order_products])
        return total_price

    @property
    def get_total_quantity(self):
        order_products = self.order_product_set.all()
        total_quantity = sum([order_product.quantity for order_product in order_products])
        return total_quantity

    @property
    def shipping(self):
        shipping = False
        order_products = self.order_product_set.all()
        for order_product in order_products:
            if order_product.product.digital==False:
                shipping = True
                break
        return shipping


class Order_Product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    date_ordered = models.TimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total 

class Shipping(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address =models.CharField(max_length=30)
    city =models.CharField(max_length=30)
    country =models.CharField(default="USA",max_length=30)
    state =models.CharField(max_length=30)
    zipcode =models.CharField(max_length=30)

    def __str__(self):
        return self.address
    



class PaymentReceipt(models.Model):
    PAYMENT_METHODS = [
        ('paypal', 'PayPal'),
        ('venmo', 'Venmo'),
    ]
    
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='payment_receipt')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    receipt_image = CloudinaryField('image', null=True, blank=True)
    #models.ImageField(upload_to='images/payment_receipts/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Payment Receipt for Order #{self.order.id}"
    
class PaymentTag(models.Model):
    paypal=models.CharField(max_length=30,null=True, blank=True)
    venmo=models.CharField(max_length=50,null=True, blank=True)

    def __str__(self):
        return self.paypal
    