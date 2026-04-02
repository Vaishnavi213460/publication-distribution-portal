from django.urls import path
from . import views

urlpatterns = [
        path('agent_dashboard/', views.agent_dashboard, name='agent_dashboard'),
        path('agent_freq_view/', views.agent_freq_view, name='agent_freq_view'),
        path('agent_pdt_view/', views.agent_pdt_view, name='agent_pdt_view'),
        path('agent_supp_view/', views.agent_supp_view, name='agent_supp_view'),
        path('add_agent_supplier/', views.add_agent_supplier, name='add_agent_supplier'),
    ]