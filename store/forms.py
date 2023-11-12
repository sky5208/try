from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
# from .models import Product

class signUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100 , required=True)
    last_name = forms.CharField(max_length=100 , required=True)
    email = forms.EmailField(max_length=250,help_text='example@gmail.com')

    class Meta:
        model = User
        fields = ('first_name','last_name','username','email','password1','password2')


# class StockUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['stock']

    