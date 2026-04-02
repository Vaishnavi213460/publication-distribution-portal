from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from admin_panel.models import Location, Supplier, Product
from agent.models import AgentSupp
from login.models import Agent


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
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        qty = int(request.POST.get('qty', 1))
        cart = request.session.setdefault('cart', {})
        if product_id:
            cart[product_id] = cart.get(product_id, 0) + qty
        request.session.modified = True
        return JsonResponse({'status': 'success', 'total_items': sum(cart.values())})
    return JsonResponse({'status': 'error'}, status=400)


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0.0
    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = float(product.price) * qty
            cart_items.append({
                'product': product,
                'qty': qty,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            del cart[product_id]
            request.session.modified = True
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'cart.html', context)
