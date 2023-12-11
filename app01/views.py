from django.shortcuts import render, HttpResponse
from django.db import connection
# Create your views here.

def home(request, customer_id):
    return render(request,"home.html", {"customer_id": customer_id})

def customer_login(request):
    if request.method == "GET":
        return render(request, "customer_login.html")

    customer_id = request.POST.get("id")
    password = request.POST.get("password")

    with connection.cursor() as cursor:
        cursor.execute("SELECT password FROM Customers WHERE customer_id = %s", [customer_id])
        row = cursor.fetchone()
        db_password = row[0]
        if db_password == password:
            return home(request, customer_id)
        else:
            return render(request, "customer_login.html",
                          {"error_msg": "Login failure caused by incorrect user name or password."})

def register_page(request):
    print("method:", request.method)
    if request.method == "GET":
        return render(request, "register_page.html")

    name = request.POST.get("name")
    password = request.POST.get("password")
    billing_address = request.POST.get("billing_address")
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(customer_id) FROM Customers")
        row = cursor.fetchone()
        max_id = row[0] if row[0] else 0
        new_id = max_id + 1
        sql = "INSERT INTO Customers (customer_id, name, billing_address, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, [new_id, name, billing_address, password])
    # return render(request, "register_success.html", {"ids": ids})
    return register_success(request, new_id)

def register_success(request,new_id):
    return render(request,"register_success.html", {"customer_id": new_id})

def energy_consumption(request,customer_id):
    return render(request,"energy_consumption.html",{"customer_id": customer_id})

def account_management(request, customer_id):
    return render(request, "account_management.html", {"customer_id": customer_id})

def list_locations(request):
    customer_id = request.POST.get("customer_id")
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM ServiceLocations WHERE customer_id = %s", [customer_id])
        locations = cursor.fetchall()
    return render(request, "list_locations.html", {"customer_id": customer_id, "locations": locations})


