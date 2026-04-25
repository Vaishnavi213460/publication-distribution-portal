from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from datetime import date

from admin_panel.models import Frequency, Product, Supplier
from login.models import Agent
from .forms import AgentSuppForm
from .models import AgentSupp

# Import customer models for delivery tracking
from customer.models import CustomerOrder, OrderCart, DailyDeliveryLog, MonthlyPayment


# ─────────────────────────────────────────────────────────────
# Internal helper — get Agent from logged-in user
# ─────────────────────────────────────────────────────────────
def _get_agent(user):
    try:
        return Agent.objects.get(login=user)
    except Agent.DoesNotExist:
        return None


def _get_agent_supplier_ids(agent):
    """Return supplier IDs linked to this agent."""
    if not agent:
        return []
    return list(AgentSupp.objects.filter(agent=agent).values_list('supplier_id', flat=True))


def _get_all_agent_items(agent):
    """All confirmed OrderCart items for products supplied by this agent."""
    if not agent:
        return OrderCart.objects.none()
    return OrderCart.objects.filter(
        product__supplier__agentsupp__agent=agent,
        order__status='payment_received',
    ).select_related('product', 'order', 'order__customer', 'frequency')


def _get_delivery_items_for_date(agent, for_date, queryset=None):
    """
    Items this agent should deliver on for_date.

    Rules:
    - Delivery window must include for_date
    - payment_type == one_time  → deliver for entire window
    - payment_type == monthly   → only if that month has a paid MonthlyPayment
    """
    qs = queryset if queryset is not None else _get_all_agent_items(agent)

    qs = qs.filter(
        delivery_start_date__lte=for_date,
        delivery_end_date__gte=for_date,
    )

    one_time_ids = qs.filter(
        order__payment_type='one_time'
    ).values_list('id', flat=True)

    monthly_paid_ids = qs.filter(
        order__payment_type='monthly',
        monthly_payments__status='paid',
        monthly_payments__month_year__year=for_date.year,
        monthly_payments__month_year__month=for_date.month,
    ).values_list('id', flat=True)

    return qs.filter(
        id__in=list(one_time_ids) + list(monthly_paid_ids)
    ).distinct()


def _item_belongs_to_agent(item, agent):
    if not agent:
        return False
    supplier_ids = _get_agent_supplier_ids(agent)
    return item.product.supplier_set.filter(id__in=supplier_ids).exists()


# ─────────────────────────────────────────────────────────────
# EXISTING VIEWS (unchanged logic, kept as-is)
# ─────────────────────────────────────────────────────────────

def agent_dashboard(request):
    return render(request, 'agentheader.html')


def agent_freq_view(request):
    return render(request, 'agent_freq_view.html', {
        'list': Frequency.objects.all()
    })


def agent_pdt_view(request):
    return render(request, 'agent_pdt_view.html', {
        'list': Product.objects.all()
    })


def agent_supp_view(request):
    return render(request, 'agent_supp_view.html', {
        'list': Supplier.objects.all()
    })


def add_agent_supplier(request):
    form = AgentSuppForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        agent = Agent.objects.get(login=request.user)
        obj.agent = agent
        obj.save()
        return redirect('agent_dashboard')
    return render(request, 'add_agent_supp_form.html', {'form': form})


# ─────────────────────────────────────────────────────────────
# NEW: Delivery list — payment-aware
# ─────────────────────────────────────────────────────────────
@login_required
def agent_delivery_list(request):
    agent = _get_agent(request.user)
    today = date.today()

    filter_type = request.GET.get('filter', 'today')
    search = request.GET.get('q', '').strip()

    all_items = _get_all_agent_items(agent)

    if search:
        all_items = all_items.filter(
            Q(order__customer__first_name__icontains=search) |
            Q(order__customer__last_name__icontains=search) |
            Q(order__customer__username__icontains=search) |
            Q(product__name__icontains=search)
        )

    if filter_type == 'today':
        items_qs = _get_delivery_items_for_date(agent, today, queryset=all_items)
    elif filter_type == 'paused':
        # All active items where current month is NOT paid
        all_in_window = all_items.filter(
            delivery_start_date__lte=today,
            delivery_end_date__gte=today,
        )
        active_ids = _get_delivery_items_for_date(agent, today, queryset=all_in_window).values_list('id', flat=True)
        items_qs = all_in_window.exclude(id__in=active_ids)
    elif filter_type == 'all':
        items_qs = all_items.exclude(delivery_status='cancelled')
    else:
        items_qs = _get_delivery_items_for_date(agent, today, queryset=all_items)

    # Annotate each item with today's log and payment info
    items_annotated = []
    for item in items_qs:
        try:
            log = DailyDeliveryLog.objects.get(order_item=item, delivery_date=today)
            today_status = log.status
        except DailyDeliveryLog.DoesNotExist:
            today_status = None

        months_paid = item.monthly_payments.filter(status='paid').count()
        is_active = item.is_active_this_month()
        payments = item.monthly_payments.all().order_by('month_year')

        items_annotated.append({
            'item': item,
            'today_status': today_status,
            'is_active': is_active,
            'months_paid': months_paid,
            'total_months': item.frequency_months,
            'payments': payments,
            'customer_name': (
                item.order.customer.get_full_name() or item.order.customer.username
            ),
        })

    # Stats for the top bar
    total_today = _get_delivery_items_for_date(agent, today).count()
    done_today = DailyDeliveryLog.objects.filter(
        order_item__in=_get_all_agent_items(agent),
        delivery_date=today,
        status='delivered',
    ).count()

    return render(request, 'agent_delivery_list.html', {
        'items': items_annotated,
        'filter_type': filter_type,
        'search': search,
        'today': today,
        'total_today': total_today,
        'done_today': done_today,
        'agent': agent,
    })


# ─────────────────────────────────────────────────────────────
# NEW: Mark delivery status (AJAX POST)
# ─────────────────────────────────────────────────────────────
@login_required
def mark_delivery(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=400)

    item_id = request.POST.get('item_id')
    delivery_status = request.POST.get('delivery_status')
    note = request.POST.get('note', '')
    today = date.today()

    if delivery_status not in ('delivered', 'missed', 'holiday'):
        return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)

    item = get_object_or_404(OrderCart, id=item_id)
    agent = _get_agent(request.user)

    if not _item_belongs_to_agent(item, agent):
        return JsonResponse({'status': 'error', 'message': 'Not authorised'}, status=403)

    DailyDeliveryLog.objects.update_or_create(
        order_item=item,
        delivery_date=today,
        defaults={
            'status': delivery_status,
            'note': note,
            'marked_by': request.user,
        }
    )

    if delivery_status == 'delivered':
        item.delivery_status = 'delivering'
        item.save(update_fields=['delivery_status'])

    return JsonResponse({
        'status': 'success',
        'delivery_status': delivery_status,
        'item_id': item_id,
    })


# ─────────────────────────────────────────────────────────────
# NEW: Order detail — full payment + delivery log
# ─────────────────────────────────────────────────────────────
@login_required
def agent_order_detail(request, item_id):
    agent = _get_agent(request.user)
    item = get_object_or_404(OrderCart, id=item_id)

    if not _item_belongs_to_agent(item, agent):
        return redirect('agent_delivery_list')

    today = date.today()
    logs = item.delivery_logs.all().order_by('-delivery_date')[:30]
    payments = item.monthly_payments.all().order_by('month_year')
    months_paid = item.monthly_payments.filter(status='paid').count()
    is_active = item.is_active_this_month()

    try:
        today_log = DailyDeliveryLog.objects.get(order_item=item, delivery_date=today)
    except DailyDeliveryLog.DoesNotExist:
        today_log = None

    return render(request, 'agent_order_detail.html', {
        'item': item,
        'customer': item.order.customer,
        'logs': logs,
        'payments': payments,
        'months_paid': months_paid,
        'is_active': is_active,
        'today': today,
        'today_log': today_log,
        'agent': agent,
    })

def toggle_agent_status(request, id):
    agent = get_object_or_404(Agent, id=id)

    if agent.status == 'Active':
        agent.status = 'Inactive'
    else:
        agent.status = 'Active'

    agent.save()
    return redirect(request.META.get('HTTP_REFERER', 'agent_list'))


# ─────────────────────────────────────────────────────────────
# NEW: Agent Payment Report — current month earnings only
# ─────────────────────────────────────────────────────────────
@login_required
def agent_payment_report(request):
    """
    Show how much this agent earned in the CURRENT MONTH only.

    One-time orders:
        If current month falls inside the delivery window,
        count monthly_amount() for this month.

    Monthly orders:
        Only count MonthlyPayment rows with status='paid'
        for the current month.
    """
    agent = _get_agent(request.user)
    items = _get_all_agent_items(agent)
    today = date.today()
    current_month = date(today.year, today.month, 1)

    one_time_total = 0.0
    monthly_total = 0.0
    item_breakdown = []

    for item in items:
        if item.order.payment_type == 'one_time':
            start = item.delivery_start_date
            end = item.delivery_end_date
            if start and end:
                start_month = date(start.year, start.month, 1)
                end_month = date(end.year, end.month, 1)
                if start_month <= current_month <= end_month:
                    amt = float(item.monthly_amount())
                    one_time_total += amt
                    item_breakdown.append({
                        'customer': item.order.customer.get_full_name() or item.order.customer.username,
                        'product': item.product.name,
                        'type': 'one_time',
                        'amount': amt,
                    })
        else:
            payment = item.monthly_payments.filter(
                status='paid',
                month_year__year=today.year,
                month_year__month=today.month,
            ).first()
            if payment:
                amt = float(payment.amount)
                monthly_total += amt
                item_breakdown.append({
                    'customer': item.order.customer.get_full_name() or item.order.customer.username,
                    'product': item.product.name,
                    'type': 'monthly',
                    'amount': amt,
                })

    total_earnings = one_time_total + monthly_total

    return render(request, 'agent_payment_report.html', {
        'month_label': today.strftime('%B %Y'),
        'one_time_total': one_time_total,
        'monthly_total': monthly_total,
        'total_earnings': total_earnings,
        'item_breakdown': item_breakdown,
        'agent': agent,
    })
