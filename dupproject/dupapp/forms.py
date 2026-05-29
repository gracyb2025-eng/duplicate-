from django import forms
from .models import Sale, Stock, Supplier, Deposit, Payment


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
            "item_name": forms.Select(attrs={"class": "form-select"}),
            "specification": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control"}),
            "total_price": forms.NumberInput(attrs={"class": "form-control"}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control"}),
        
        }

    # validations
    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get("unit_price")
        if unit_price <= 0:
            raise forms.ValidationError("Unit price must be greater than zero.")
        return unit_price

    def clean_total_price(self):
        total_price = self.cleaned_data.get("total_price")
        if total_price <= 0:
            raise forms.ValidationError("Total price must be greater than zero.")
        return total_price

    def clean_customer_name(self):
        customer_name = self.cleaned_data.get("customer_name")
        if len(customer_name) < 3:
            raise forms.ValidationError("Customer name is too short.")
        return customer_name


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            "item_name",
            "specification",
            "quantity",
            "unit_cost",
            "selling_price",
            "supplier",
            "payment_method",
            "amount_paid",
        ]

        widgets = {
            "item_name": forms.TextInput(attrs={"class": "form-control"}),
            "specification": forms.TextInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "unit_cost": forms.NumberInput(attrs={"class": "form-control"}),
            "selling_price": forms.NumberInput(attrs={"class": "form-control"}),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "amount_paid": forms.NumberInput(attrs={"class": "form-control"}),
        }

    # validations
    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_unit_cost(self):
        unit_cost = self.cleaned_data.get("unit_cost")
        if unit_cost <= 0:
            raise forms.ValidationError("Unit cost must be greater than zero.")
        return unit_cost

    def clean(self):
        cleaned_data = super().clean()
        unit_cost = cleaned_data.get("unit_cost")
        selling_price = cleaned_data.get("selling_price")
        if (
            unit_cost and
            selling_price and
            selling_price <= unit_cost
        ):
            raise forms.ValidationError("Selling price must be greater than unit cost.")
        return cleaned_data


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "name",
            "email",
            "contact",
            "address",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if len(name) < 2:
            raise forms.ValidationError("Supplier name is too short.")
        return name


class DepositForm(forms.ModelForm):

    class Meta:
        model = Deposit
        fields = [
            "customer_name",
            "item_name",
            "total_cost",
            "amount",
            "payment_method",
        ]

        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "item_name": forms.TextInput(attrs={"class": "form-control"}),
            "total_cost": forms.NumberInput(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("Deposit amount must be greater than zero.")
        return amount


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount"]
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-control"})
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount