from django import forms
from .models import Order

class OrderAssignForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_person', 'status']  