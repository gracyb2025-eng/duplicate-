from django import forms
from .models import Sale

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            "item_name",
            "specification",
            "quantity",
            "unit_price",
            "total_price",
            "payment_method",
            "customer_name",
            "contact",
        ]
        widgets = {
            "item_name": forms.TextInput(attrs={"class": "form-control"}),
            "specification": forms.TextInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control"}),
            "total_price": forms.NumberInput(attrs={"class": "form-control"}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control"}),
        }
