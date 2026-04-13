from django.urls import path
from . import views

urlpatterns = [

    path('', views.dashboard, name='admin_dashboard'),
    # Location
    path('location/', views.location_list_create_update, name='location_list'),
    path('location/edit/<int:id>/', views.location_list_create_update, name='location_edit'),
    path('location/delete/<int:id>/', views.location_delete, name='location_delete'),

    # Frequency
    path('frequency/', views.frequency_list_create_update, name='frequency_list'),
    path('frequency/edit/<int:id>/', views.frequency_list_create_update, name='frequency_edit'),
    path('frequency/delete/<int:id>/', views.frequency_delete, name='frequency_delete'),

    # Product
    path('product/', views.product_list_create_update, name='product_list'),
    path('product/edit/<int:id>/', views.product_list_create_update, name='product_edit'),
    path('product/delete/<int:id>/', views.product_delete, name='product_delete'),

    # Supplier
    path('supplier/', views.supplier_list_create_update, name='supplier_list'),
    path('supplier/edit/<int:id>/', views.supplier_list_create_update, name='supplier_edit'),
    path('supplier/delete/<int:id>/', views.supplier_delete, name='supplier_delete'),

    # Agent 
    path('agent/', views.agent_list, name='agent_list'),
    path('agent-supplier/', views.agent_supp_list_create_update, name='agent_supplier_mapping'),
    path('agent-supplier/edit/<int:id>/', views.agent_supp_list_create_update, name='agent_supp_edit'),
    path('agent-supplier/delete/<int:id>/', views.agent_supp_delete, name='agent_supp_delete'),

    # Customer
    path('customer/', views.customer_list, name='customer_list'),
    path('orders/', views.customer_order_list, name='customer_order_list'),

]

