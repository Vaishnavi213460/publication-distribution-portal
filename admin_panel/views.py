from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from datetime import date
from .models import Location, Frequency, Product, Supplier, Notification
from .forms import LocationForm, FrequencyForm, ProductForm, SupplierForm, AgentSuppForm, NotificationForm
from login.models import Agent, Customer
from agent.models import AgentSupp
from customer.models import CustomerOrder, OrderCart, MonthlyPayment, Complaint

def dashboard(request):
    # return HttpResponse("Welcome to Admin Panel")
    return render(request, 'adminheader.html')

# Locations CRUD

def location_list_create_update(request, id=None):

    obj = get_object_or_404(Location, id=id) if id else None

    form = LocationForm(request.POST or None, instance=obj)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('location_list')

    data = Location.objects.all()

    return render(request, 'loc_list_form.html', {
        'form': form,
        'data': data
    })


def location_delete(request, id):
    obj = get_object_or_404(Location, id=id)
    obj.delete()
    return redirect('location_list')

# Frequency CRUD
def frequency_list_create_update(request, id=None):

    obj = get_object_or_404(Frequency, id=id) if id else None

    form = FrequencyForm(request.POST or None, instance=obj)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('frequency_list')

    data = Frequency.objects.all()

    return render(request, 'freq_list_form.html', {
        'form': form,
        'data': data
    })


def frequency_delete(request, id):
    obj = get_object_or_404(Frequency, id=id)
    obj.delete()
    return redirect('frequency_list')

# PRODUCT CRUD

def product_list_create_update(request, id=None):

    obj = get_object_or_404(Product, id=id) if id else None

    form = ProductForm(request.POST or None, request.FILES or None, instance=obj)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('product_list')

    data = Product.objects.all()

    return render(request, 'product_list_form.html', {
        'form': form,
        'data': data
    })


def product_delete(request, id):
    obj = get_object_or_404(Product, id=id)
    obj.delete()
    return redirect('product_list')

#  Supplier CRUD
def supplier_list_create_update(request, id=None):

    obj = get_object_or_404(Supplier, id=id) if id else None

    form = SupplierForm(request.POST or None, request.FILES or None, instance=obj)

    if request.method == "POST":
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.save()
            form.save_m2m()
            return redirect('supplier_list')
        else:
            print(form.errors)  # 👈 ADD THIS

    data = Supplier.objects.all()

    return render(request, 'supplier_list_form.html', {
        'form': form,
        'data': data
    })


def supplier_delete(request, id):
    obj = get_object_or_404(Supplier, id=id)
    obj.delete()
    return redirect('supplier_list')


def agent_list(request):
    data = Agent.objects.all()
    return render(request, 'admin_agent_list.html', {'data': data})

def agent_supp_list_create_update(request, id=None):

    obj = get_object_or_404(AgentSupp, id=id) if id else None

    form = AgentSuppForm(request.POST or None, instance=obj)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('agent_supplier_mapping')

    data = AgentSupp.objects.select_related('agent', 'supplier')

    return render(request, 'admin_agent_supp_form.html', {
        'form': form,
        'data': data
    })

def customer_list(request):
    data = Customer.objects.all()
    return render(request, 'admin_customer_list.html', {'data': data})

def customer_order_list(request):
    data = CustomerOrder.objects.all().select_related('customer')
    return render(request, 'admin_customer_orders.html', {'data': data})


def agent_supp_delete(request, id):
    obj = get_object_or_404(AgentSupp, id=id)
    obj.delete()
    return redirect('agent_supplier_mapping')


# ─────────────────────────────────────────────────────────────
# NEW: Admin Payment Report — current month earnings per agent
# ─────────────────────────────────────────────────────────────
def _agent_items(agent):
    """All confirmed OrderCart items for products supplied by this agent."""
    if not agent:
        return OrderCart.objects.none()
    return OrderCart.objects.filter(
        product__supplier__agentsupp__agent=agent,
        order__status='payment_received',
    ).select_related('product', 'order', 'order__customer', 'frequency')


def admin_payment_report(request):
    """
    Show how much EACH agent earned in the CURRENT MONTH.
    """
    today = date.today()
    current_month = date(today.year, today.month, 1)
    agents = Agent.objects.all()

    agent_rows = []
    grand_one_time = 0.0
    grand_monthly = 0.0
    grand_total = 0.0

    for agent in agents:
        items = _agent_items(agent)
        one_time_total = 0.0
        monthly_total = 0.0

        for item in items:
            if item.order.payment_type == 'one_time':
                start = item.delivery_start_date
                end = item.delivery_end_date
                if start and end:
                    start_month = date(start.year, start.month, 1)
                    end_month = date(end.year, end.month, 1)
                    if start_month <= current_month <= end_month:
                        one_time_total += float(item.monthly_amount())
            else:
                payment = item.monthly_payments.filter(
                    status='paid',
                    month_year__year=today.year,
                    month_year__month=today.month,
                ).first()
                if payment:
                    monthly_total += float(payment.amount)

        total = one_time_total + monthly_total
        grand_one_time += one_time_total
        grand_monthly += monthly_total
        grand_total += total

        agent_rows.append({
            'agent': agent,
            'one_time_total': one_time_total,
            'monthly_total': monthly_total,
            'total': total,
        })

    # Sort by total earnings descending
    agent_rows.sort(key=lambda x: x['total'], reverse=True)

    return render(request, 'admin_payment_report.html', {
        'month_label': today.strftime('%B %Y'),
        'agent_rows': agent_rows,
        'grand_one_time': grand_one_time,
        'grand_monthly': grand_monthly,
        'grand_total': grand_total,
    })


# ─────────────────────────────────────────────────────────────
# NEW: Admin Complaints — view all complaints + reply
# ─────────────────────────────────────────────────────────────
def admin_complaints(request):
    complaints = Complaint.objects.all().select_related(
        'customer', 'agent'
    ).order_by('-comp_date')
    return render(request, 'admin_complaints.html', {
        'complaints': complaints
    })


def admin_complaint_reply(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        complaint.comp_reply = request.POST.get('comp_reply', '')[:50]
        complaint.comp_status = request.POST.get('comp_status', 'Pending')
        complaint.save()
    return redirect('admin_complaints')


# ─────────────────────────────────────────────────────────────
# NEW: Admin Notifications — CRUD
# ─────────────────────────────────────────────────────────────
def notification_list_create_update(request, id=None):
    obj = get_object_or_404(Notification, id=id) if id else None
    form = NotificationForm(request.POST or None, instance=obj)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('notification_list')

    data = Notification.objects.all().select_related('agent')

    return render(request, 'notification_list_form.html', {
        'form': form,
        'data': data
    })


def notification_delete(request, id):
    obj = get_object_or_404(Notification, id=id)
    obj.delete()
    return redirect('notification_list')
