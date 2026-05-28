"""
URL configuration for dupproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from dupapp import views
from django.urls import path, include

urlpatterns = [

    # Django admin
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    # Landing page
    path("", views.landing_page, name="landing"),

    #  admin  
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/sales/", views.admin_sales_dashboard, name="admin_sales_dashboard"),
    path("dashboard/stock/", views.admin_stock_dashboard, name="admin_stock_dashboard"),
    path("dashboard/reports/",views.admin_reports,name="admin_reports"),
    path("dashboard/stock-reports/",views.admin_stock_reports,name="admin_stock_reports"),
    path("dashboard/stock/edit/<int:stock_id>/",views.admin_edit_stock,name="admin_edit_stock"),
    path("dashboard/stock/view/<int:stock_id>/",views.admin_view_stock,name="admin_view_stock"),
    path("dashboard/stock/payment/<int:stock_id>/",views.admin_add_supplier_payment,name="admin_add_supplier_payment"),
    #  Sales 
    path('sales/', views.sales_dashboard, name='sales_dashboard'),
    path("sales/dashboard/", views.sales_dashboard, name="sales_dashboard"),
    path("sales/form/", views.save_sale, name="save_sale"),
    path("receipt/<int:sale_id>/", views.view_receipt, name="view_receipt"),
    path("payment/<int:sale_id>/", views.add_payment, name="add_payment"),
    path("sales/edit/<int:sale_id>/", views.edit_sale, name="edit_sale"),
    path("reports/", views.reports, name="reports"),

    #  stock 
    path("stock/", views.stock_dashboard, name="stock_dashboard"),
    path("stock/add/", views.add_stock, name="add_stock"),
    path("stock/edit/<int:stock_id>/", views.edit_stock, name="edit_stock"),
    path("stock/view/<int:stock_id>/", views.view_stock, name="view_stock"),
    path("stock/payment/<int:stock_id>/", views.add_supplier_payment, name="add_supplier_payment"),
    path("stock/reports/", views.stock_reports, name="stock_reports"),

    #  suppliers
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/add/", views.add_supplier, name="add_supplier"),
    path("suppliers/edit/<int:supplier_id>/", views.edit_supplier, name="edit_supplier"),
    path("suppliers/delete/<int:supplier_id>/", views.delete_supplier, name="delete_supplier"),

    #  deposits
    path("deposits/", views.deposit_list, name="deposit_list"),
    path("deposits/add/", views.add_deposit, name="add_deposit"),
    path("deposits/<int:deposit_id>/receipt/", views.view_deposit_receipt, name="view_deposit_receipt"),
    path("deposits/<str:customer_name>/<str:item_name>/history/", views.deposit_history, name="deposit_history"),

    
]