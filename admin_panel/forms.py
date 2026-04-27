from django import forms
from .models import Location, Frequency, Supplier, Product, Notification
from agent.models import AgentSupp

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
        exclude = ['status']  

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class AgentSuppForm(forms.ModelForm):
    class Meta:
        model = AgentSupp
        exclude = ['status']  


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = '__all__'
        widgets = {
            'message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter notification message (max 50 chars)'}),
            'agent': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
        }
