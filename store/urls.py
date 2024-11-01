from . import views
from django.urls import path

urlpatterns = [
    path('register/', views.registerUser, name="register"),
    path('login/', views.loginUser, name="login"),
    path('logout/', views.logoutUser, name="logout"),

 
    path('', views.store, name="store"),
    path('cart/',views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),

    path('update_item/', views.update_item, name="update_item"),
    #path('process_order/',views.process_order, name="process_order"),
    path('process-order/', views.process_order, name='process_order'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('terms/', views.terms, name='terms'),
    path('return_policy/', views.return_policy, name='return_policy'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)