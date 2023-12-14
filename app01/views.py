from django.urls import reverse

from django.shortcuts import render, HttpResponse, redirect
from django.db import connection


# Create your views here.

def home(request, customer_id):
    return render(request, "home.html", {"customer_id": customer_id})


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


def register_success(request, new_id):
    return render(request, "register_success.html", {"customer_id": new_id})


def energy_consumption(request, customer_id):
    return render(request, "energy_consumption.html", {"customer_id": customer_id})


def account_management(request, customer_id):
    return render(request, "account_management.html", {"customer_id": customer_id})


def list_locations(request):
    customer_id = request.POST.get("customer_id") or request.GET.get("customer_id")
    with connection.cursor() as cursor:
        cursor.execute("""
                    SELECT sl.* FROM ServiceLocations sl
                    INNER JOIN CustomerServices cs ON sl.location_id = cs.location_id
                    WHERE cs.customer_id = %s
                """, [customer_id])
        locations = cursor.fetchall()
    return render(request, "list_locations.html", {"customer_id": customer_id, "locations": locations})


def delete_locations(request):
    customer_id = request.POST.get("customer_id")
    location_id = request.POST.get("location_id")
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM CustomerServices WHERE location_id = %s AND customer_id = %s",
                       [location_id, customer_id])
        cursor.execute("SELECT COUNT(*) FROM CustomerServices WHERE location_id = %s", [location_id])
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("DELETE FROM ServiceLocations WHERE location_id = %s", [location_id])

    return redirect('/list_locations/' + f'?customer_id={customer_id}')


def add_locations(request):
    customer_id = request.POST.get("customer_id")
    if request.method == 'POST':

        service_address = request.POST.get("service_address")
        zip_code = request.POST.get("zip_code")
        unit_number = request.POST.get("unit_number")
        square_footage = request.POST.get("square_footage")
        num_bedrooms = request.POST.get("num_bedrooms")
        num_occupants = request.POST.get("num_occupants")
        date_took_over = request.POST.get("date_took_over")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT location_id FROM ServiceLocations WHERE service_address = %s AND unit_number = %s AND zip_code = %s",
                [service_address, unit_number, zip_code])
            existing_location = cursor.fetchone()
            if existing_location:

                location_id = existing_location[0]
                cursor.execute("INSERT INTO CustomerServices (customer_id, location_id) VALUES (%s, %s)",
                               [customer_id, location_id])
            else:
                cursor.execute("SELECT MAX(location_id) FROM ServiceLocations")
                row = cursor.fetchone()
                max_id = row[0] if row[0] else 0
                new_id = max_id + 1
                sql = "INSERT INTO ServiceLocations (location_id, service_address, zip_code, unit_number, " \
                      "square_footage, num_bedrooms, num_occupants, date_took_over) VALUES (%s, %s, %s, %s, " \
                      "%s, %s, %s, %s)"
                cursor.execute(sql,
                               [new_id, service_address, zip_code, unit_number, square_footage, num_bedrooms,
                                num_occupants,
                                date_took_over])
                cursor.execute("INSERT INTO CustomerServices (customer_id, location_id) VALUES (%s, %s)",
                               [customer_id, new_id])

    return redirect('/list_locations/' + f'?customer_id={customer_id}')


def list_devices(request):
    customer_id = request.POST.get("customer_id") or request.GET.get("customer_id")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ed.device_id, dt.type_name, dm.model_number, ed.enrollment_date
            FROM EnrolledDevices ed
            INNER JOIN DeviceModels dm ON ed.model_id = dm.model_id
            INNER JOIN DeviceTypes dt ON dm.type_id = dt.type_id
            INNER JOIN ServiceLocations sl ON ed.location_id = sl.location_id
            INNER JOIN CustomerServices cs ON sl.location_id = cs.location_id
            WHERE cs.customer_id = %s
        """, [customer_id])
        devices = cursor.fetchall()
    return render(request, "list_devices.html", {"customer_id": customer_id, "devices": devices})


def delete_devices(request):
    customer_id = request.POST.get("customer_id")
    device_id = request.POST.get("device_id")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM DeviceEvents WHERE device_id = %s", [device_id])
        cursor.execute("DELETE FROM EnergyUsage WHERE device_id = %s", [device_id])
        cursor.execute("DELETE FROM EnrolledDevices WHERE device_id = %s", [device_id])
    redirect_url = '/list_devices/' + f'?customer_id={customer_id}'
    return redirect(redirect_url)


def add_devices(request):
    customer_id = request.POST.get("customer_id")
    if request.method == 'POST':
        device_id = request.POST.get("device_id")
        location_id = request.POST.get("location_id")
        model_id = request.POST.get("model_id")
        enrollment_date = request.POST.get("enrollment_date")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT device_id FROM EnrolledDevices WHERE device_id = %s", [device_id])
            existing_device = cursor.fetchone()

            if existing_device:
                pass
            else:
                sql = "INSERT INTO EnrolledDevices (device_id, location_id, model_id, enrollment_date) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, [device_id, location_id, model_id, enrollment_date])

    redirect_url = '/list_devices/' + f'?customer_id={customer_id}'
    return redirect(redirect_url)
