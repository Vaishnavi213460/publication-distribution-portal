from django.urls import path
from . import views

urlpatterns = [
    # ── Existing routes (unchanged) ──────────────────────────
    path('agent_dashboard/',    views.agent_dashboard,     name='agent_dashboard'),
    path('agent_freq_view/',    views.agent_freq_view,     name='agent_freq_view'),
    path('agent_pdt_view/',     views.agent_pdt_view,      name='agent_pdt_view'),
    path('agent_supp_view/',    views.agent_supp_view,     name='agent_supp_view'),
    path('add_agent_supplier/', views.add_agent_supplier,  name='add_agent_supplier'),

    # ── New delivery routes ──────────────────────────────────
    path('deliveries/',              views.agent_delivery_list, name='agent_delivery_list'),
    path('deliveries/mark/',         views.mark_delivery,       name='mark_delivery'),
    path('deliveries/<int:item_id>/', views.agent_order_detail, name='agent_order_detail'),
    path('agent-toggle-status/<int:id>/', views.toggle_agent_status, name='toggle_agent_status'),

    # ── Payment report ───────────────────────────────────────
    path('payment-report/', views.agent_payment_report, name='agent_payment_report'),

    # ── Complaints ───────────────────────────────────────────
    path('complaints/', views.agent_complaints, name='agent_complaints'),

    # ── Delivery Rounds & Stock ──────────────────────────────
    path('delivery-rounds/', views.agent_delivery_rounds, name='agent_delivery_rounds'),
    path('delivery-rounds/<int:id>/delete/', views.delivery_round_delete, name='delivery_round_delete'),
    path('delivery-stocks/<int:id>/delete/', views.delivery_stock_delete, name='delivery_stock_delete'),

    path('invoices/', views.agent_invoices, name='agent_invoices'),
    path('invoices/<int:order_id>/', views.agent_invoice_detail, name='agent_invoice_detail'),
]
