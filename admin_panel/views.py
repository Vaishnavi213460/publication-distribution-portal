from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Location, Frequency, Product, Supplier
from .forms import LocationForm, FrequencyForm, ProductForm, SupplierForm


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

    form = ProductForm(request.POST or None, instance=obj)

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

    form = SupplierForm(request.POST or None, instance=obj)

    if request.method == "POST" and form.is_valid():
        supplier = form.save(commit=False)
        supplier.save()
        form.save_m2m() 
        
        return redirect('supplier_list')

    data = Supplier.objects.all()

    return render(request, 'supplier_list_form.html', {
        'form': form,
        'data': data
    })


def supplier_delete(request, id):
    obj = get_object_or_404(Supplier, id=id)
    obj.delete()
    return redirect('supplier_list')
