from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from admin_panel.models import Location, Supplier, Product
from agent.models import AgentSupp
from login.models import Agent
from django.db.models import Sum
from .models import CustomerOrder, OrderCart
import traceback


def customer_dashboard(request):
    return render(request, 'customerheader.html')

def customer_shop(request):
    context = {}
    if request.method == 'POST':
        loc = Location.objects.get(id=request.POST['location_id'])
        context['agent'] = Agent.objects.prefetch_related('location').filter(location=loc)
    context['list'] = Location.objects.all()
    return render(request, "customer_shop.html", context)

def supplier_list(request, agent_id):
    context = {}

    suppliers = Supplier.objects.filter(
        agentsupp__agent_id=agent_id,
    )

    context["suppliers"] = suppliers

    return render(request, "supplier_list.html", context)


def customer_agent_products(request, agent_id):
    
    supplier_ids = AgentSupp.objects.filter(
        agent_id=agent_id
    ).values_list('supplier_id', flat=True)

    products = Product.objects.filter(
        supplier__id__in=supplier_ids
    )

    return render(request, 'customer_agent_products.html', {
        'products': products,
        'agent_id': agent_id
    })

    
def product_detail(request, product_id, agent_id):
    product = get_object_or_404(Product.objects.prefetch_related('frequency'), id=product_id)
    context = {'product': product, 'agent_id': agent_id}
    return render(request, 'product_detail.html', context)


def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=400)

    product_id = request.POST.get('product_id')

    if not product_id:
        return JsonResponse({'status': 'error', 'message': 'Product ID missing'}, status=400)

    try:
        qty = int(request.POST.get('qty', 1))
        if qty < 1:
            raise ValueError
    except:
        return JsonResponse({'status': 'error', 'message': 'Invalid quantity'}, status=400)

    try:
        product = Product.objects.get(id=product_id)

        # get or create cart
        order, _ = CustomerOrder.objects.get_or_create(
            customer=request.user,
            status='cart'
        )

        cart_item, created = OrderCart.objects.get_or_create(
            order=order,
            product=product,
            defaults={'qty': qty}
        )

        if not created:
            cart_item.qty += qty
            cart_item.save()

        total_items = order.items.aggregate(total=Sum('qty'))['total'] or 0

        return JsonResponse({
            'status': 'success',
            'total_items': total_items
        })

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def cart_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  # or however you handle this

    try:
        order = CustomerOrder.objects.get(customer=request.user, status='cart')
        cart_items = []
        total = 0.0

        for item in order.items.select_related('product').all():
            subtotal = float(item.product.price) * item.qty
            cart_items.append({
                'product': item.product,
                'qty': item.qty,
                'subtotal': subtotal
            })
            total += subtotal

    except CustomerOrder.DoesNotExist:
        cart_items = []
        total = 0.0

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def cart_data_api(request):
    """Returns cart data as JSON for the header dropdown."""
    if not request.user.is_authenticated:
        return JsonResponse({'total_items': 0, 'items': [], 'total': 0})
    
    try:
        order = CustomerOrder.objects.get(customer=request.user, status='cart')
        items = []
        total = 0.0
        for item in order.items.select_related('product').all():
            subtotal = float(item.product.price) * item.qty
            total += subtotal
            items.append({
                'id': item.id,
                'product_id': item.product.id,
                'name': item.product.name,
                'price': float(item.product.price),
                'qty': item.qty,
                'subtotal': subtotal,
            })
        total_items = order.items.aggregate(total=Sum('qty'))['total'] or 0
        return JsonResponse({
            'total_items': total_items,
            'items': items,
            'total': total
        })
    except CustomerOrder.DoesNotExist:
        return JsonResponse({'total_items': 0, 'items': [], 'total': 0})


def remove_from_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=400)
    
    item_id = request.POST.get('item_id')
    try:
        item = OrderCart.objects.get(id=item_id, order__customer=request.user, order__status='cart')
        item.delete()
        return JsonResponse({'status': 'success'})
    except OrderCart.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)


def checkout_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        order = CustomerOrder.objects.get(customer=request.user, status='cart')
        cart_items = []
        total = 0.0
        for item in order.items.select_related('product').all():
            subtotal = float(item.product.price) * item.qty
            cart_items.append({'product': item.product, 'qty': item.qty, 'subtotal': subtotal})
            total += subtotal
    except CustomerOrder.DoesNotExist:
        order = None
        cart_items = []
        total = 0.0

    if request.method == 'POST' and order:
        from datetime import date, timedelta
        order.status = 'placed'
        order.delivery_start_date = date.today() + timedelta(days=3)
        order.delivery_end_date = date.today() + timedelta(days=7)
        order.save()
        return redirect('order_success')

    return render(request, 'checkout.html', {
        'order': order,
        'cart_items': cart_items,
        'total': total
    })


def order_success(request):
    return render(request, 'order_success.html')