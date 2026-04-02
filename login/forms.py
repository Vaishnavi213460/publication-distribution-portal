from django import forms
from .models import Agent, Customer


class AgentForm(forms.ModelForm):
    # Defining custom fields with Bootstrap classes
    Username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Username'})
    )
    Password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Password'})
    )
    ConfirmPassword = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = Agent
        fields = ('name', 'code', 'address', 'phone', 'photo', 'forget_question', 'forget_question_answer',
                  'total_customers', 'location')

        # Adding Bootstrap classes to the ModelForm fields automatically
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'forget_question': forms.TextInput(attrs={'class': 'form-control'}),
            'forget_question_answer': forms.TextInput(attrs={'class': 'form-control'}),
            'total_customers': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.SelectMultiple(attrs={'class': 'form-control'}),

        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('Password')
        confirm_password = cleaned_data.get('ConfirmPassword')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class CustomerForm(forms.ModelForm):
    Username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Username'})
    )
    Password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter Password'})
    )
    ConfirmPassword = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = Customer
        fields = ('name', 'address', 'phone', 'email')

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('Password')
        confirm_password = cleaned_data.get('ConfirmPassword')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data