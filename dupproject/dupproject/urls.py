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
from django.urls import path
from dupapp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.sales_dashboard, name="home"),  
    path("sales/dashboard/", views.sales_dashboard, name="sales_dashboard"),
    path("sales/form/", views.save_sale, name="save_sale"),
    path("receipt/<int:sale_id>/", views.view_receipt, name="view_receipt"),
    path("payment/<int:sale_id>/", views.add_payment, name="add_payment"),
    path("sales/edit/<int:sale_id>/", views.edit_sale, name="edit_sale"),
    path("sales/delete/<int:sale_id>/", views.delete_sale, name="delete_sale"),
    path("reports/", views.reports, name="reports"),
    path("stock/", views.stock_dashboard, name="stock_dashboard"),
    path("stock/add/", views.add_stock, name="add_stock"),
    path("stock/edit/<int:stock_id>/", views.edit_stock, name="edit_stock"),
    path("stock/view/<int:stock_id>/", views.view_stock, name="view_stock"),
    path("stock/delete/<int:stock_id>/", views.delete_stock, name="delete_stock"),
    path("supplier/add/", views.add_supplier, name="add_supplier"),
    path("supplier/payment/<int:stock_id>/", views.add_supplier_payment, name="add_supplier_payment"),
]
