from .models import Contact
from django import forms
from .models import Review
from agency.models import Property


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'text']


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['employer', 'description', 'image']


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'price', 'location', 'floor',
                  'square_meters', 'owner', 'property_types', 'image']


