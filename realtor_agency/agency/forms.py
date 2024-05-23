# agency/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from datetime import date

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    birthdate = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'birthdate', 'password1', 'password2']

    def clean_birthdate(self):
        birthdate = self.cleaned_data.get('birthdate')
        age = date.today().year - birthdate.year - ((date.today().month, date.today().day) < (birthdate.month, birthdate.day))
        if age < 18:
            raise forms.ValidationError("You must be at least 18 years old to register.")
        return birthdate
