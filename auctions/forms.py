from django.forms import ModelForm
from django import forms

from .models import Listing, Bid, Comment, Category

# class CreateListingForm(forms.Form):
#     CATEGORY_CHOICES = [
#         ('Fashion', 'Fashion'),
#         ('Toys', 'Toys'),
#         ('Electronics', 'Electronics'),
#         ('Home', 'Home'),
#         ('Other', 'Other')
#     ]
#     title = forms.CharField(label="Title")
#     description = forms.CharField(widget=forms.Textarea(attrs={'rows':'5', 'cols':'50'}))
#     bid = forms.DecimalField(widget=forms.NumberInput(attrs={'step':'0.01', 'min':'0'}))
#     image_url = forms.CharField(widget=forms.URLInput(), required=False)
#     categories = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select)

class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'categories', 'image_url']
        widgets = {
            'price': forms.NumberInput(attrs={'step':'0.01', 'min':'0'}),
            'categories': forms.Select()
        }