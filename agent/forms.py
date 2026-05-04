from django import forms
from .models import AgentSupp, DeliveryRound, DeliveryStock

class AgentSuppForm(forms.ModelForm):
    class Meta:
        model = AgentSupp
        exclude = ['status']

        widgets = {
            'from_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'to_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class DeliveryRoundForm(forms.ModelForm):
    class Meta:
        model = DeliveryRound
        exclude = ['agent']
        widgets = {
            'start_place': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter starting place',
                'maxlength': '20',
            }),
            'end_place': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ending place',
                'maxlength': '20',
            }),
        }


class DeliveryStockForm(forms.ModelForm):
    class Meta:
        model = DeliveryStock
        fields = '__all__'
        widgets = {
            'delivery_round': forms.Select(attrs={
                'class': 'form-control',
            }),
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),
            'no_of_copies': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of copies',
                'min': '1',
            }),
        }
