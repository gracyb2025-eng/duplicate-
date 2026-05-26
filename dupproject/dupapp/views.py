from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum,F
from django.contrib import messages
from .models import Sale, Payment,Stock,SupplierPayment, Supplier, Deposit
from .forms import SaleForm, StockForm  # assuming you have a ModelForm
from django.core.exceptions import ValidationError
import datetime
from decimal import Decimal


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

        try:
            total_price = float(
                request.POST['total_price']
            )

            distance_km = int(
                request.POST.get('distance_km', 0)
            )

            quantity_sold = int(
                request.POST['quantity']
            )

            item_name = request.POST['item_name']
            specification = request.POST['specification']

            # FIND STOCK ITEM
            stock = Stock.objects.filter(
                item_name=item_name,
                specification=specification
            ).first()

            # CHECK IF ITEM EXISTS
            if not stock:
                return render(request, 'sales_form.html', {
                    'errors': [
                        'Item does not exist in stock.'
                    ]
                })

            # CHECK AVAILABLE QUANTITY
            if stock.quantity < quantity_sold:
                return render(request, 'sales_form.html', {
                    'errors': [
                        f'Only {stock.quantity} items left in stock.'
                    ]
                })

            # TRANSPORT LOGIC
            if total_price >= 500000 and distance_km <= 10:
                transport_cost = 0
            else:
                transport_cost = 30000

            sale = Sale(

                item_name=item_name,
                specification=specification,
                quantity=quantity_sold,
                unit_price=request.POST['unit_price'],
                total_price=request.POST['total_price'],
                payment_method=request.POST['payment_method'],
                customer_name=request.POST['customer_name'],
                contact=request.POST['contact'],
                nin=request.POST['nin'],
                receipt_number=generate_receipt_number(),
                distance_km=distance_km,
                transport_cost=transport_cost,
            )

            # VALIDATE
            sale.full_clean()

            # SAVE SALE
            sale.save()

            # REDUCE STOCK
            stock.quantity -= quantity_sold
            stock.save()

            return redirect('sales_dashboard')

        except ValidationError as e:

            return render(request, 'sales_form.html', {
                'errors': e.messages
            })

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



def reports(request):
    daily_sales = Sale.objects.values('date__date').annotate(total=Sum('total_price'))
    payment_methods = Sale.objects.values('payment_method').annotate(total=Sum('total_price'))
    return render(request, "reports.html", {
        "daily_sales": daily_sales,
        "payment_methods": payment_methods,
    })

def stock_dashboard(request):
    stocks = Stock.objects.all()
    total_value = sum([s.stock_value() for s in stocks]) if stocks else 0
    low_stock = stocks.filter(quantity__lt=10)
    supplier_credit = Stock.objects.filter(payment_method='Credit')
    return render(request, 'stock_dashboard.html', {
        'stocks': stocks,
        'total_value': total_value,
        'low_stock': low_stock,
        'supplier_credit': supplier_credit,
    })

def add_stock(request):

    if request.method == "POST":

        form = StockForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, "Stock added successfully.")

            return redirect("stock_dashboard")

    else:

        form = StockForm()

        return render(request, "stock_form.html", {
    "form": form,
    "suppliers": Supplier.objects.all()
})

   



def view_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    return render(request, "view_stock.html", {"stock": stock})



def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, "supplier_list.html", {"suppliers": suppliers})

def add_supplier(request):
    if request.method == "POST":
        Supplier.objects.create(
            name=request.POST["name"],
            email=request.POST["email"],
            contact=request.POST["contact"],
            address=request.POST["address"]
        )
        return redirect("add_stock")  # redirect back to stock form
    return render(request, "supplier_form.html")

def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == "POST":
        supplier.name = request.POST["name"]
        supplier.email = request.POST["email"]
        supplier.contact = request.POST["contact"]
        supplier.address = request.POST["address"]
        supplier.save()
        return redirect("supplier_list")
    return render(request, "edit_supplier.html", {"supplier": supplier})

# Delete supplier
def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.delete()
    return redirect("supplier_list")

def add_supplier_payment(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == "POST":
        SupplierPayment.objects.create(
            supplier=stock.supplier,
            stock=stock,
            amount=request.POST["amount"]
        )
        stock.amount_paid += Decimal(request.POST["amount"])
        stock.save()
        return redirect("stock_dashboard")
    return render(request, "supplier_payment_form.html", {"stock": stock})
       

def stock_reports(request):
    inflow = Stock.objects.values('date_received__date').annotate(total=Sum('quantity'))
    outflow = []  # later link to your Sale model if you have one
    current_stock = Stock.objects.all()
    supplier_credit = Stock.objects.filter(payment_method="Credit")
    low_stock = Stock.objects.filter(quantity__lt=10)

    return render(request, "reports_stock.html", {
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
            return redirect("stock_dashboard")  # back to dashboard
    else:
        form = StockForm(instance=stock)  # pre-fill with current values

    return render(request, "edit_stock.html", {"form": form, "stock": stock})

def landing_page(request):
    return render(request, 'landing.html')



def admin_sales_dashboard(request):

    sales = Sale.objects.all().order_by("-date")

    total_sales = Sale.objects.aggregate(
        Sum('total_price')
    )['total_price__sum'] or 0

    total_deposits = Payment.objects.aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    outstanding_credit = sum(
        sale.balance()
        for sale in Sale.objects.filter(
            payment_method='Credit'
        )
    )

    paid_sales = Sale.objects.filter(
        payment_method__in=['Cash', 'Mobile']
    ).count()

    unpaid_sales = sum(
        1
        for sale in Sale.objects.filter(
            payment_method='Credit'
        )
        if sale.balance() > 0
    )

    context = {
        'sales': sales,
        'total_sales': total_sales,
        'total_deposits': total_deposits,
        'outstanding_credit': outstanding_credit,
        'paid_sales': paid_sales,
        'unpaid_sales': unpaid_sales,
    }

    return render(
        request,
        'admin_sales_dashboard.html',
        context
    )



def admin_stock_dashboard(request):

    stocks = Stock.objects.all()

    total_value = sum(
        [s.stock_value() for s in stocks]
    ) if stocks else 0

    low_stock = stocks.filter(quantity__lt=10)

    supplier_credit = Stock.objects.filter(
        payment_method='Credit'
    )

    context = {
        'stocks': stocks,
        'total_value': total_value,
        'low_stock': low_stock,
        'supplier_credit': supplier_credit,
    }

    return render(
        request,
        'admin_stock_dashboard.html',
        context
    )


def admin_sales_dashboard(request):
    sales = Sale.objects.all().order_by("-date")
    total_sales = Sale.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_deposits = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    outstanding_credit = sum(
        sale.balance() for sale in Sale.objects.filter(payment_method='Credit')
    )
    unpaid_sales = sum(
        1 for sale in Sale.objects.filter(payment_method='Credit')
        if sale.balance() > 0
    )

    context = {
        'sales': sales,
        'total_sales': total_sales,
        'total_deposits': total_deposits,
        'outstanding_credit': outstanding_credit,
        'unpaid_sales': unpaid_sales,
    }

    return render(request, "admin_sales_dashboard.html", context)


def admin_stock_dashboard(request):
    stocks = Stock.objects.all()
    total_value = sum([s.stock_value() for s in stocks]) if stocks else 0
    low_stock = stocks.filter(quantity__lt=10)

    context = {
        'stocks': stocks,
        'total_value': total_value,
        'low_stock': low_stock,
    }

    return render(request, "admin_stock_dashboard.html", context)



def admin_reports(request):
    daily_sales = Sale.objects.values(
        'date__date'
    ).annotate(total=Sum('total_price'))

    payment_methods = Sale.objects.values(
        'payment_method'
    ).annotate(total=Sum('total_price'))

    return render(request, "reports.html", {
        "daily_sales": daily_sales,
        "payment_methods": payment_methods,
    })



def admin_stock_reports(request):
    inflow = Stock.objects.values(
        'date_received__date'
    ).annotate(total=Sum('quantity'))

    current_stock = Stock.objects.all()

    supplier_credit = Stock.objects.filter(
        payment_method="Credit"
    )

    low_stock = Stock.objects.filter(
        quantity__lt=10
    )

    return render(request, "reports_stock.html", {
        "inflow": inflow,
        "current_stock": current_stock,
        "supplier_credit": supplier_credit,
        "low_stock": low_stock,
    })

def admin_edit_stock(request, stock_id):

    stock = get_object_or_404(Stock, id=stock_id)

    if request.method == "POST":

        form = StockForm(request.POST, instance=stock)

        if form.is_valid():

            form.save()

            return redirect("admin_stock_dashboard")

    else:

        form = StockForm(instance=stock)

    return render(
        request,
        "admin_edit_stock.html",
        {
            "form": form,
            "stock": stock
        }
    )

def admin_view_stock(request, stock_id):

    stock = get_object_or_404(Stock, id=stock_id)

    return render(
        request,
        "admin_view_stock.html",
        {
            "stock": stock
        }
    )

def admin_add_supplier_payment(request, stock_id):

    stock = get_object_or_404(Stock, id=stock_id)

    if request.method == "POST":

        amount = Decimal(request.POST["amount"])

        SupplierPayment.objects.create(
            supplier=stock.supplier,
            stock=stock,
            amount=amount
        )

        stock.amount_paid += amount
        stock.save()

        return redirect("admin_stock_dashboard")

    return render(
        request,
        "admin_supplier_payment.html",
        {
            "stock": stock
        }
    )
