from django.urls import path
from . import views

urlpatterns = [
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer_shop/', views.customer_shop, name='customer_shop'),
    path('agent/<int:agent_id>/', views.customer_agent_products, name='customer_agent_products'),
    path('product/<int:product_id>/<int:agent_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/data/', views.cart_data_api, name='cart_data_api'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/', views.payment_page, name='payment_page'),
    path('payment/confirm/', views.confirm_payment, name='confirm_payment'),
    path('order-success/', views.order_success, name='order_success'),
]