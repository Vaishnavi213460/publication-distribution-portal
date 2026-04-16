import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from admin_panel.models import Location, Supplier, Product, Frequency
from agent.models import AgentSupp
from login.models import Agent
from django.db.models import Sum
from .models import CustomerOrder, OrderCart, ShippingDetails
from .frequency_utils import frequencies_for_product, label_to_months
from datetime import date, timedelta
import traceback


# ────────────────────────────────────────────────────────────
# Dashboard
# ────────────────────────────────────────────────────────────
def customer_dashboard(request):
    return render(request, 'customerheader.html')


# ────────────────────────────────────────────────────────────
# Shop — location → agents
# ────────────────────────────────────────────────────────────
def customer_shop(request):
    context = {'list': Location.objects.all()}
    if request.method == 'POST':
        location_id = request.POST.get('location_id')
        if location_id:
            try:
                loc = Location.objects.get(id=location_id)
                agents = Agent.objects.prefetch_related('location').filter(location=loc)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'agents': [
                        {
                            'id': a.id, 'name': a.name, 'phone': a.phone,
                            'photo': a.photo.url if a.photo else None,
                            'location': a.location.first().location if a.location.exists() else '',
                        }
                        for a in agents
                    ]})
                context['agent'] = agents
            except Location.DoesNotExist:
                context['agent'] = []
    return render(request, 'customer_shop.html', context)


# ────────────────────────────────────────────────────────────
# Agent → products
# ────────────────────────────────────────────────────────────
def customer_agent_products(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    supplier_ids = AgentSupp.objects.filter(agent_id=agent_id).values_list('supplier_id', flat=True)
    products = Product.objects.filter(supplier__id__in=supplier_ids)
    return render(request, 'customer_agent_products.html', {
        'products': products, 'agent': agent, 'agent_id': agent_id,
    })


# ────────────────────────────────────────────────────────────
# Product detail  ← key change: builds frequencies_json from DB
# ────────────────────────────────────────────────────────────
def product_detail(request, product_id, agent_id):
    product = get_object_or_404(
        Product.objects.prefetch_related('frequency'),
        id=product_id
    )

    # Build frequency list from this product's linked Frequency objects
    freq_list = frequencies_for_product(product)   # [{id, label, months}, ...]

    return render(request, 'product_detail.html', {
        'product': product,
        'agent_id': agent_id,
        # Pass as JSON-safe string so the template can use |json_script
        'frequencies_json': freq_list,
    })


# ────────────────────────────────────────────────────────────
# Supplier list
# ────────────────────────────────────────────────────────────
def supplier_list(request, agent_id):
    suppliers = Supplier.objects.filter(agentsupp__agent_id=agent_id)
    return render(request, 'supplier_list.html', {'suppliers': suppliers})


# ────────────────────────────────────────────────────────────
# Add to cart  — accepts frequency_id (FK) + frequency_months
# ────────────────────────────────────────────────────────────
def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=400)

    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'status': 'error', 'message': 'Product ID missing'}, status=400)

    try:
        qty = max(1, int(request.POST.get('qty', 1)))
    except (ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid quantity'}, status=400)

    # Resolve the Frequency FK
    frequency_id = request.POST.get('frequency_id')
    frequency_obj = None
    frequency_months = 1

    if frequency_id:
        try:
            frequency_obj = Frequency.objects.get(id=int(frequency_id))
            frequency_months = label_to_months(frequency_obj.frequency)
        except (Frequency.DoesNotExist, ValueError):
            pass

    # If no FK given, fall back to plain months integer (backward-compat)
    if frequency_obj is None:
        try:
            frequency_months = max(1, int(request.POST.get('frequency_months', 1)))
        except (ValueError, TypeError):
            frequency_months = 1

    # Parse start date
    delivery_start = None
    delivery_end   = None
    start_str = request.POST.get('delivery_start_date', '')
    if start_str:
        try:
            delivery_start = date.fromisoformat(start_str)
            delivery_end   = delivery_start + timedelta(days=30 * frequency_months)
        except ValueError:
            pass

    try:
        product = get_object_or_404(Product, id=product_id)
        order, _ = CustomerOrder.objects.get_or_create(customer=request.user, status='cart')

        cart_item, created = OrderCart.objects.get_or_create(
            order=order,
            product=product,
            defaults={
                'qty': qty,
                'frequency': frequency_obj,
                'frequency_months': frequency_months,
                'delivery_start_date': delivery_start,
                'delivery_end_date': delivery_end,
            }
        )
        if not created:
            cart_item.qty = qty
            cart_item.frequency = frequency_obj
            cart_item.frequency_months = frequency_months
            cart_item.delivery_start_date = delivery_start
            cart_item.delivery_end_date   = delivery_end
            cart_item.save()

        total_items = order.items.aggregate(total=Sum('qty'))['total'] or 0
        return JsonResponse({'status': 'success', 'total_items': total_items})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ────────────────────────────────────────────────────────────
# Cart view
# ────────────────────────────────────────────────────────────
def cart_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        order = CustomerOrder.objects.get(customer=request.user, status='cart')
        cart_items = [
            {
                'id': item.id,
                'product': item.product,
                'qty': item.qty,
                'frequency_label': item.frequency.frequency if item.frequency else f"{item.frequency_months} month(s)",
                'frequency_months': item.frequency_months,
                'delivery_start_date': item.delivery_start_date,
                'delivery_end_date': item.delivery_end_date,
                'unit_price': float(item.product.price),
                'subtotal': item.total_amount(),
            }
            for item in order.items.select_related('product', 'frequency').all()
        ]
        total = sum(i['subtotal'] for i in cart_items)
    except CustomerOrder.DoesNotExist:
        cart_items, total = [], 0.0

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})


# ────────────────────────────────────────────────────────────
# Cart data API  (JSON for sidebar badge)
# ────────────────────────────────────────────────────────────
def cart_data_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'total_items': 0, 'items': [], 'total': 0})
    try:
        order = CustomerOrder.objects.get(customer=request.user, status='cart')
        items, total = [], 0.0
        for item in order.items.select_related('product', 'frequency').all():
            sub = item.total_amount()
            total += sub
            items.append({
                'id': item.id,
                'product_id': item.product.id,
                'name': item.product.name,
                'price': float(item.product.price),
                'qty': item.qty,
                'frequency_label': item.frequency.frequency if item.frequency else f"{item.frequency_months}mo",
                'frequency_months': item.frequency_months,
                'subtotal': sub,
            })
        total_items = order.items.aggregate(total=Sum('qty'))['total'] or 0
        return JsonResponse({'total_items': total_items, 'items': items, 'total': total})
    except CustomerOrder.DoesNotExist:
        return JsonResponse({'total_items': 0, 'items': [], 'total': 0})


# ────────────────────────────────────────────────────────────
# Remove from cart
# ────────────────────────────────────────────────────────────
def remove_from_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=400)
    try:
        item = OrderCart.objects.get(
            id=request.POST.get('item_id'),
            order__customer=request.user,
            order__status='cart'
        )
        item.delete()
        return JsonResponse({'status': 'success'})
    except OrderCart.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)


# ────────────────────────────────────────────────────────────
# Checkout
# ────────────────────────────────────────────────────────────
def checkout_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        order = CustomerOrder.objects.get(customer=request.user, status='cart')
        cart_items = [
            {
                'id': item.id,
                'product': item.product,
                'qty': item.qty,
                'frequency_label': item.frequency.frequency if item.frequency else f"{item.frequency_months} month(s)",
                'frequency_months': item.frequency_months,
                'delivery_start_date': item.delivery_start_date,
                'unit_price': float(item.product.price),
                'subtotal': item.total_amount(),
            }
            for item in order.items.select_related('product', 'frequency').all()
        ]
        total = sum(i['subtotal'] for i in cart_items)
        monthly_total = sum(float(i['product'].price) * i['qty'] for i in cart_items)
    except CustomerOrder.DoesNotExist:
        order, cart_items, total, monthly_total = None, [], 0.0, 0.0

    saved_addresses = ShippingDetails.objects.filter(customer=request.user)

    if request.method == 'POST' and order:
        payment_type = request.POST.get('payment_type', 'one_time')
        use_saved = request.POST.get('use_saved_address')
        if use_saved:
            shipping = get_object_or_404(ShippingDetails, id=use_saved, customer=request.user)
        else:
            shipping = ShippingDetails.objects.create(
                customer=request.user,
                name=request.POST.get('name', ''),
                phone=request.POST.get('phone', ''),
                email=request.POST.get('email', ''),
                shipping_address=request.POST.get('shipping_address', ''),
                landmark=request.POST.get('landmark', ''),
                city=request.POST.get('city', ''),
                district=request.POST.get('district', ''),
                state=request.POST.get('state', 'Kerala'),
                pincode=request.POST.get('pincode', ''),
                is_default=request.POST.get('save_address') == 'on',
            )
        request.session['pending_order_id'] = order.id
        request.session['shipping_id'] = shipping.id
        request.session['payment_type'] = payment_type
        request.session['order_total'] = total
        request.session['monthly_total'] = monthly_total
        return redirect('payment_page')

    return render(request, 'checkout.html', {
        'order': order, 'cart_items': cart_items,
        'total': total, 'monthly_total': monthly_total,
        'saved_addresses': saved_addresses,
    })


# ────────────────────────────────────────────────────────────
# Payment page
# ────────────────────────────────────────────────────────────
def payment_page(request):
    if not request.user.is_authenticated:
        return redirect('login')
    order_id = request.session.get('pending_order_id')
    if not order_id:
        return redirect('cart')
    order = get_object_or_404(CustomerOrder, id=order_id, customer=request.user)
    shipping_id = request.session.get('shipping_id')
    shipping = get_object_or_404(ShippingDetails, id=shipping_id) if shipping_id else None
    return render(request, 'payment.html', {
        'order': order,
        'total': request.session.get('order_total', 0),
        'monthly_total': request.session.get('monthly_total', 0),
        'payment_type': request.session.get('payment_type', 'one_time'),
        'shipping': shipping,
    })


# ────────────────────────────────────────────────────────────
# Confirm payment (POST from payment page)
# ────────────────────────────────────────────────────────────
def confirm_payment(request):
    if not request.user.is_authenticated or request.method != 'POST':
        return redirect('login')
    order_id = request.session.get('pending_order_id')
    if not order_id:
        return redirect('cart')
    order = get_object_or_404(CustomerOrder, id=order_id, customer=request.user)
    order.status = 'payment_received'
    order.save()
    order.items.all().update(status='order_confirmed')
    for key in ('pending_order_id', 'shipping_id', 'payment_type', 'order_total', 'monthly_total'):
        request.session.pop(key, None)
    return redirect('order_success')


# ────────────────────────────────────────────────────────────
# Order success
# ────────────────────────────────────────────────────────────
def order_success(request):
    return render(request, 'order_success.html')