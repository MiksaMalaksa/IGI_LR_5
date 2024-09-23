from .models import Contact
from django import forms
from .models import Review
from agency.models import Property

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['employer', 'description', 'image']


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'price', 'location', 'floor',
                  'square_meters', 'owner', 'property_types', 'image']
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }



