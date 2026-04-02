from django.urls import path
from . import views

urlpatterns = [
        path('home/', views.home, name='home'),
        path('agent_registration/', views.agent_registration, name='agent_registration'),
        path('customer_registration/', views.customer_registration, name='customer_registration'),
        path('login/', views.login_user, name='login'),
        path('customer_home/', views.customer_home, name='customer_home'),
    ]