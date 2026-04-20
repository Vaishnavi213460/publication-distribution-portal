from django import forms
from .models import AgentSupp

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