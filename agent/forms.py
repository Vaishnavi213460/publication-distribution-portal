from django import forms
from .models import AgentSupp

class AgentSuppForm(forms.ModelForm):
    class Meta:
        model = AgentSupp
        exclude = ('agent',)