from django import forms
from login.models import Agent
from .models import Complaint


class ComplaintForm(forms.ModelForm):
    agent = forms.ModelChoiceField(
        queryset=Agent.objects.filter(status='Active').order_by('name'),
        empty_label='Select Agent',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Complaint
        fields = ['agent', 'complaint']
        widgets = {
            'complaint': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your complaint (max 50 chars)',
                'maxlength': 50,
            }),
        }


class CancelOrderForm(forms.Form):
    order_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    cancel_reason = forms.CharField(
        max_length=200,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Why do you want to cancel this order? (optional)',
        }),
        required=False
    )

