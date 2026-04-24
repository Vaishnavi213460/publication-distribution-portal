from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Prefetch
from .models import CustomerOrder, OrderCart, MonthlyPayment, ShippingDetails
from datetime import date
from dateutil.relativedelta import relativedelta

def monthly_payments_view(request):
    """
    List all monthly orders with their pending payments.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get monthly payment orders
    monthly_orders = CustomerOrder.objects.filter(
        customer=request.user,
        payment_type='monthly',
        status='payment_received'
    ).prefetch_related(
        Prefetch('items',
                 queryset=OrderCart.objects.select_related('product').prefetch_related('monthly_payments'),
                 to_attr='items_with_payments')
    ).order_by('-order_date')
    
    context = {
        'monthly_orders': monthly_orders,
    }
    return render(request, 'monthly_payments.html', context)

def pay_monthly_redirect(request, payment_id):
    """
    Redirect to payment page for specific monthly payment.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    payment = get_object_or_404(MonthlyPayment.objects.select_related('order_item__order'), id=payment_id)
    
    # Security: must belong to user's order
    if payment.order_item.order.customer != request.user:
        return redirect('monthly_payments')
    
    # Only allow pending payments
    if payment.status != 'pending':
        return redirect('monthly_payments')
    
    # Set session for single month payment
    request.session['monthly_payment_id'] = payment.id
    request.session['monthly_amount'] = float(payment.amount)
    request.session['payment_title'] = f"Month: {payment.month_year.strftime('%b %Y')}"
    
    return redirect('payment_page')
