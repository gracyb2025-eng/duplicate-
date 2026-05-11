from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Sale, Payment,Stock,SupplierPayment, Supplier
import datetime


# Create your views here.
def generate_receipt_number():
    today = datetime.date.today().strftime('%d%m%Y')
    last_number = Sale.objects.filter(date__date=datetime.date.today()).count() + 1
    return f"RCT-{today}-{last_number:03d}"

def sales_dashboard(request):
    sales = Sale.objects.all().order_by("-date")
    total_sales = Sale.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_deposits = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    outstanding_credit =sum(sale.balance() for sale in Sale.objects.filter(payment_method='Credit'))
    paid_sales = Sale.objects.filter(payment_method__in=['Cash', 'Mobile']).count()
    unpaid_sales = sum(1 for sale in Sale.objects.filter(payment_method='Credit') if sale.balance() > 0)

    context = {
        'sales': sales,
        'total_sales': total_sales,
        'total_deposits': total_deposits,
        'outstanding_credit': outstanding_credit,
        'paid_sales': paid_sales,
        'unpaid_sales': unpaid_sales,
    }
    return render(request, 'sales_dashboard.html', context)

def save_sale(request):
    if request.method == 'POST':
        sale = Sale.objects.create(
            item_name=request.POST['item_name'],
            specification=request.POST['specification'],
            quantity=request.POST['quantity'],
            unit_price=request.POST['unit_price'],
            total_price=request.POST['total_price'],
            payment_method=request.POST['payment_method'],
            customer_name=request.POST['customer_name'],
            contact=request.POST['contact'],
            receipt_number=generate_receipt_number()
        )
        return redirect('sales_dashboard')
    return render(request, 'sales_form.html')

def view_receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'receipt.html', {'sale': sale})

def add_payment(request,sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    if request.method == 'POST':
        Payment.objects.create(
            sale=sale,
            amount=request.POST['amount']
        )
        return redirect('sales_dashboard')
    return render(request, 'credit_payment.html', {'sale': sale})

def edit_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    if request.method == 'POST':
        sale.item_name = request.POST['item_name']
        sale.specification = request.POST['specification']
        sale.quantity = request.POST['quantity']
        sale.unit_price = request.POST['unit_price']
        sale.total_price = request.POST['total_price']
        sale.payment_method = request.POST['payment_method']
        sale.customer_name = request.POST['customer_name']
        sale.contact = request.POST['contact']
        sale.save()
        return redirect('sales_dashboard')
    return render(request, 'sales_form.html', {'sale': sale})

def delete_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    sale.delete()
    return redirect('sales_dashboard')

def reports(request):
    daily_sales = Sale.objects.values('date__date').annotate(total=Sum('total_price'))
    payment_methods = Sale.objects.values('payment_method').annotate(total=Sum('total_price'))
    return render(request, "reports.html", {
        "daily_sales": daily_sales,
        "payment_methods": payment_methods,
    })


def stock_dashboard(request):
    stocks = Stock.objects.all()
    total_value = stocks.aggregate(Sum('quantity'))['quantity__sum']
    low_stock = stocks.filter(quantity__lt=10)
    supplier_credit = Stock.objects.filter(payment_method='Credit')
    return render(request, 'stock_dashboard.html', {
        'stocks': stocks,
        'total_value': total_value,
        'low_stock': low_stock,
        'supplier_credit': supplier_credit,
    })

def add_stock(request):
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        supplier = Supplier.objects.get(id=supplier_id)
        Stock.objects.create(
            item_name=request.POST['item_name'],
             specification=request.POST["specification"],
            quantity=request.POST["quantity"],
            unit_cost=request.POST["unit_cost"],
            selling_price=request.POST["selling_price"],
            supplier=supplier,
            payment_method=request.POST["payment_method"],
            amount_paid=request.POST.get("amount_paid", 0)
        )
        return redirect("stock_dashboard")
    suppliers = Supplier.objects.all()
    return render(request, "stock_form.html", {"suppliers": suppliers})

def edit_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == "POST":
        stock.item_name = request.POST["item_name"]
        stock.specification = request.POST["specification"]
        stock.quantity = request.POST["quantity"]
        stock.unit_cost = request.POST["unit_cost"]
        stock.selling_price = request.POST["selling_price"]
        stock.save()
        return redirect("stock_dashboard")
    return render(request, "edit_stock.html", {"stock": stock})

def view_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    return render(request, "view_stock.html", {"stock": stock})

def delete_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    stock.delete()
    return redirect("stock_dashboard")

def add_supplier(request):
    if request.method == "POST":
        Supplier.objects.create(
            name=request.POST["name"],
            email=request.POST["email"],
            contact=request.POST["contact"],
            address=request.POST["address"]
        )
        return redirect("stock_dashboard")
    return render(request, "supplier_form.html")

def add_supplier_payment(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == "POST":
        SupplierPayment.objects.create(
            supplier=stock.supplier,
            stock=stock,
            amount=request.POST["amount"]
        )
        stock.amount_paid += float(request.POST["amount"])
        stock.save()
        return redirect("stock_dashboard")
    return render(request, "supplier_payment_form.html", {"stock": stock})
       
        