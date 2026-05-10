from django.db import models
import datetime
# Create your models here.
class Sale(models.Model):
    ITEM_NAME_CHOICES = [
        ('Cement', 'Cement'),
        ('Iron Bar', 'Iron Bar'),
        ('Nails', 'Nails'),
        ('Roofing Nails (5kg)', 'Roofing Nails (5kg)'),
        ('Wheelbarrow', 'Wheelbarrow'),
        ('Wire Mesh', 'Wire Mesh'),
        ('Barbed Wire', 'Barbed Wire'),
        ('Iron Sheets', 'Iron Sheets'),
    ]

    SPECIFICATION_CHOICES = [
        ('CEM II/N', 'CEM II/N'),
        ('CEM III/N', 'CEM III/N'),
        ('10mm', '10mm'),
        ('12mm', '12mm'),
        ('16mm', '16mm'),
        ('1 inch', '1 inch'),
        ('3 inch', '3 inch'),
        ('4 inch', '4 inch'),
        ('5 inch', '5 inch'),
        ('Roofing Nails 5kg', 'Roofing Nails 5kg'),
        ('Wheelbarrow', 'Wheelbarrow'),
        ('Wire Mesh', 'Wire Mesh'),
        ('High Tensile', 'High Tensile'),
        ('Low Tensile', 'Low Tensile'),
        ('Gauge 28', 'Gauge 28'),
        ('Gauge 30', 'Gauge 30'),
        ('Gauge 32', 'Gauge 32'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Credit', 'Credit'),
        ('Mobile', 'Mobile Money'),
    ]
    item_name = models.CharField(max_length=50, choices=ITEM_NAME_CHOICES)
    specification = models.CharField(max_length=100, blank=True, choices=SPECIFICATION_CHOICES)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    customer_name = models.CharField(max_length=100)
    contact =  models.CharField(max_length=15)
    receipt_number = models.CharField(max_length=20, unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def amount_paid(self):
        return sum(payment.amount for payment in self.payments.all())
    
    def balance(self):
        return self.total_price - self.amount_paid()
    
    def status(self):
        if self.payment_method in ['Cash', 'Mobile']:
            return 'Paid'
        return 'Paid' if self.balance() == 0 else 'Unpaid'
    
    def __str__(self):
        return f"{self.receipt_number} - {self.customer_name}" 
    
class Payment(models.Model):
    sale = models.ForeignKey(Sale, related_name="payments", on_delete=models.CASCADE) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.sale.receipt_number} - {self.amount}"

                             