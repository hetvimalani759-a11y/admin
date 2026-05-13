from django import forms
from django.contrib.auth.models import User
from .models import DeliveryPerson

class DeliveryPersonForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = DeliveryPerson
        fields = ['phone', 'is_active']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        delivery_person = super().save(commit=False)
        delivery_person.user = user
        if commit:
            delivery_person.save()
        return delivery_person
