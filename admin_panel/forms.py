from django import forms
from .models import Location, Frequency, Supplier, Product

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = '__all__'


class FrequencyForm(forms.ModelForm):
    class Meta:
        model = Frequency
        fields = '__all__'

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
