from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib import messages
from .models import Sale, Payment,Stock,SupplierPayment, Supplier, Deposit
from .forms import SaleForm  # assuming you have a ModelForm

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
        total_price = float(request.POST['total_price'])
        distance_km = int(request.POST.get('distance_km', 0))

        if total_price >= 500000 and distance_km <= 10:
            transport_cost = 0
        else:
            transport_cost = 30000
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

    if request.method == "POST":
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect("sales_dashboard")
    else:
        form = SaleForm(instance=sale)  # pre-fill with current values

    return render(request, "edit_sale.html", {"form": form, "sale": sale})

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
       




def stock_reports(request):
    inflow = Stock.objects.values('date_received__date').annotate(total=Sum('quantity'))
    outflow = []  # later link to your Sale model if you have one
    current_stock = Stock.objects.all()
    supplier_credit = Stock.objects.filter(payment_method="Credit")
    low_stock = Stock.objects.filter(quantity__lt=10)

    return render(request, "reports.html", {
        "inflow": inflow,
        "outflow": outflow,
        "current_stock": current_stock,
        "supplier_credit": supplier_credit,
        "low_stock": low_stock,
    })





def admin_dashboard(request):
    stocks = Stock.objects.all()
    suppliers = Supplier.objects.all()
    low_stock = stocks.filter(quantity__lt=10)
    supplier_credit = Sale.objects.filter(payment_method="Credit")
    total_stock_value = sum([s.stock_value() for s in stocks]) if stocks else 0

    # Transport calculations
    transport_revenue = Sale.objects.aggregate(Sum('transport_cost'))['transport_cost__sum'] or 0
    free_deliveries = Sale.objects.filter(transport_cost=0).count()

    context = {
        "stocks": stocks,
        "suppliers": suppliers,
        "low_stock": low_stock,
        "supplier_credit": supplier_credit,
        "total_stock_value": total_stock_value,
        "transport_revenue": transport_revenue,
        "free_deliveries": free_deliveries,
    }
    return render(request, "admin_dashboard.html", context)


def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, "supplier_list.html", {"suppliers": suppliers})




# Show all deposits
def deposit_list(request):
    deposits = Deposit.objects.all().order_by("-date")
    return render(request, "deposit_list.html", {"deposits": deposits})

# Add a new deposit
def add_deposit(request):
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        item_name = request.POST.get("item_name")
        total_cost = request.POST.get("total_cost")
        amount = request.POST.get("amount")
        payment_method = request.POST.get("payment_method")

        if payment_method not in ["Cash", "Mobile Money"]:
            messages.error(request, "Deposits can only be made via Cash or Mobile Money.")
            return redirect("add_deposit")

        # Generate a simple receipt number
        receipt_number = f"DPT{Deposit.objects.count() + 1:04d}"

        Deposit.objects.create(
            customer_name=customer_name,
            item_name=item_name,
            total_cost=total_cost,
            amount=amount,
            payment_method=payment_method,
            receipt_number=receipt_number,
        )
        messages.success(request, "Deposit recorded successfully.")
        return redirect("deposit_list")

    return render(request, "deposit_form.html")

# View a temporary receipt for a deposit
def view_deposit_receipt(request, deposit_id):
    deposit = get_object_or_404(Deposit, id=deposit_id)
    return render(request, "deposit_receipt.html", {"deposit": deposit})

# Track deposit history for a customer + item
def deposit_history(request, customer_name, item_name):
    deposits = Deposit.objects.filter(customer_name=customer_name, item_name=item_name).order_by("date")
    total_paid = sum(d.amount for d in deposits)
    total_cost = deposits.first().total_cost if deposits.exists() else 0
    balance = total_cost - total_paid

    return render(request, "deposit_history.html", {
        "customer_name": customer_name,
        "item_name": item_name,
        "deposits": deposits,
        "total_paid": total_paid,
        "total_cost": total_cost,
        "balance": balance,
    })





def edit_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)

    if request.method == "POST":
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            return redirect("stock_table")  # back to dashboard
    else:
        form = StockForm(instance=stock)  # pre-fill with current values

    return render(request, "edit_stock.html", {"form": form, "stock": stock})

