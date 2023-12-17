from django.urls import reverse

from django.shortcuts import render, HttpResponse, redirect
from django.db import connection
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
from io import BytesIO


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
            SELECT ed.device_id, sl.location_id, sl.service_address, dt.type_name, dm.model_number, ed.enrollment_date
            FROM EnrolledDevices ed
            INNER JOIN DeviceModels dm ON ed.model_id = dm.model_id
            INNER JOIN DeviceTypes dt ON dm.type_id = dt.type_id
            INNER JOIN ServiceLocations sl ON ed.location_id = sl.location_id
            INNER JOIN CustomerServices cs ON sl.location_id = cs.location_id
            WHERE cs.customer_id = %s
        """, [customer_id])
        devices = cursor.fetchall()

        cursor.execute("SELECT type_id, type_name FROM DeviceTypes")
        device_types = cursor.fetchall()

        cursor.execute("SELECT model_id, model_number FROM DeviceModels")
        device_models = cursor.fetchall()

    return render(request, "list_devices.html", {
        "customer_id": customer_id,
        "devices": devices,
        "device_types": device_types,
        "device_models": device_models
    })

def delete_devices(request):
    customer_id = request.POST.get("customer_id")
    device_id = request.POST.get("device_id")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM DeviceEvents WHERE device_id = %s", [device_id])
        cursor.execute("DELETE FROM EnergyUsage WHERE device_id = %s", [device_id])
        cursor.execute("DELETE FROM EnrolledDevices WHERE device_id = %s", [device_id])
    redirect_url = '/list_devices/' + f'?customer_id={customer_id}'
    return redirect(redirect_url)
    # return render(request, "list_devices.html", {"customer_id": customer_id})


def add_devices(request):

    customer_id = request.POST.get("customer_id")
    if request.method == 'POST':

        location_id = request.POST.get("location_id")
        existing_model_id = request.POST.get("existing_model_id")
        new_model_number = request.POST.get("new_model_number")
        enrollment_date = request.POST.get("enrollment_date")
        existing_type_id = request.POST.get("existing_type_id")
        new_type_name = request.POST.get("new_type_name")

        with connection.cursor() as cursor:
            if new_type_name:
                cursor.execute("SELECT MAX(type_id) FROM DeviceTypes")
                row = cursor.fetchone()
                max_type_id = row[0] if row[0] else 0
                type_id = max_type_id + 1
                cursor.execute("INSERT INTO DeviceTypes (type_id, type_name) VALUES (%s,%s)", [type_id, new_type_name])
            else:
                type_id = existing_type_id
            if new_model_number:
                cursor.execute("SELECT MAX(model_id) FROM DeviceModels")
                row = cursor.fetchone()
                max_model_id = row[0] if row[0] else 0
                new_model_id = max_model_id + 1
                cursor.execute("INSERT INTO DeviceModels (model_id, type_id,model_number) VALUES (%s,%s,%s)", [new_model_id,type_id,new_model_number])
            else:
                new_model_id = existing_model_id

            cursor.execute("SELECT MAX(device_id) FROM EnrolledDevices")
            row = cursor.fetchone()
            max_device_id = row[0] if row[0] else 0
            new_device_id = max_device_id + 1
            sql = "INSERT INTO EnrolledDevices (device_id, location_id, model_id, enrollment_date) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, [new_device_id, location_id, new_model_id, enrollment_date])

    redirect_url = '/list_devices/' + f'?customer_id={customer_id}'
    return redirect(redirect_url)


def energy_consumption(request, customer_id):
    if request.method == "GET":
        # location_ids = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT sl.location_id, sl.service_address FROM CustomerServices cs JOIN ServiceLocations sl ON cs.location_id = sl.location_id WHERE customer_id = %s ORDER BY location_id ASC",[customer_id])
            location_ids = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT DISTINCT device_id, model_number, type_name
            FROM CustomerServices cs JOIN EnrolledDevices ed ON cs.location_id = ed.location_id
            JOIN DeviceModels dm ON ed.model_id = dm.model_id
            JOIN DeviceTypes dt ON dm.type_id = dt.type_id
            WHERE customer_id = %s
            ORDER BY device_id ASC
            """, [customer_id])

            device_ids = cursor.fetchall()

        return render(request, "energy_consumption.html", {"customer_id": customer_id, "location_ids": location_ids, "device_ids": device_ids})

    if request.POST.get("choice") == "Daily Consumption Check":
        location_id = request.POST.get("location_id")
        start_time_str = request.POST.get("start_time")
        end_time_str = request.POST.get("end_time")
        all_consumption = daily_consumption_check(location_id,start_time_str,end_time_str)
        dates = []
        kwh_totals = []
        for row in all_consumption:
            dates.append(row[0])
            kwh_totals.append(row[1])
            # print(row[0]," ", row[1])
        graphic1 = daily_consumption_graphic(dates,kwh_totals)
        return render(request, "energy_consumption.html", {"customer_id": customer_id, 'graphic1': graphic1})

    elif request.POST.get("choice") == "Device Consumption Check":
        device_id = request.POST.get("device_id")
        start_time_str = request.POST.get("start_time")
        end_time_str = request.POST.get("end_time")
        device_consumption = device_daily_consumption(device_id, start_time_str, end_time_str)
        dates = []
        kwh_totals = []
        for row in device_consumption:
            dates.append(row[0])
            kwh_totals.append(row[1])
            # print(row[0], " ", row[1])
        graphic2 = daily_consumption_graphic(dates, kwh_totals)
        return render(request, "energy_consumption.html", {"customer_id": customer_id, 'graphic2': graphic2})

    elif request.POST.get("choice") == "Location Total Price":
        location_id = request.POST.get("location_id")
        month = request.POST.get("month")
        my_price = my_monthly_price(location_id, month)
        avg_price = avg_monthly_price(month)
        my = my_price[0]
        if my is None:
            my = 0
        graphic3 = compare_total_price_graph(my, avg_price, month)
        return render(request, "energy_consumption.html", {"customer_id": customer_id, 'graphic3': graphic3})
def daily_consumption_check(location_id, start_time_str, end_time_str):
    start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
    formatted_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
    formatted_end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT DATE(time_stamp) AS date, SUM(kWh) AS total_kWh
                FROM EnergyUsage eu 
                JOIN EnrolledDevices ed ON eu.device_id = ed.device_id
                WHERE location_id = %s AND time_stamp BETWEEN %s AND %s
                GROUP BY DATE(time_stamp)
                ORDER BY DATE(time_stamp) ASC
            """, [location_id, formatted_start_time, formatted_end_time])
        return cursor.fetchall()

def device_daily_consumption(device_id,start_time_str, end_time_str):
    start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
    formatted_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
    formatted_end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT DATE(time_stamp) AS date, SUM(kWh) AS total_kWh
                FROM EnergyUsage
                WHERE device_id = %s AND time_stamp BETWEEN %s AND %s
                GROUP BY DATE(time_stamp)
                ORDER BY DATE(time_stamp) ASC
            """, [device_id, formatted_start_time, formatted_end_time])
        return cursor.fetchall()

def daily_consumption_graphic(dates, kwh_totals):
    plt.figure(figsize=(10, 6))
    plt.plot(dates, kwh_totals, marker='o')

    for date, kwh_total in zip(dates, kwh_totals):
        plt.text(date, kwh_total, f"{kwh_total}", ha='center', va='bottom')

    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Date')
    plt.ylabel('Total kWh')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic1 = base64.b64encode(image_png).decode('utf-8')

    return graphic1

def my_monthly_price(location_id, month):
    month_start = month + "-01 00:00:00"
    month_end = month + "-31 23:59:59"
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT SUM(eu.kWh * p.price_per_kwh) AS total_energy_cost
                FROM ServiceLocations sl
                JOIN EnrolledDevices ed ON sl.location_id = ed.location_id
                JOIN EnergyUsage eu ON ed.device_id = eu.device_id
                JOIN Price p ON sl.zip_code = p.zip_code AND DATE_FORMAT(eu.time_stamp, '%%Y-%%m-%%d %%H') = DATE_FORMAT(p.time_stamp, '%%Y-%%m-%%d %%H')
                WHERE sl.location_id = %s AND eu.time_stamp BETWEEN %s AND %s
            """, [location_id, month_start, month_end])

        return cursor.fetchone()

def avg_monthly_price(month):
    month_start = month + "-01 00:00:00"
    month_end = month + "-31 23:59:59"
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT SUM(eu.kWh * p.price_per_kwh) AS avg_total_energy_cost
                FROM ServiceLocations sl
                JOIN EnrolledDevices ed ON sl.location_id = ed.location_id
                JOIN EnergyUsage eu ON ed.device_id = eu.device_id
                JOIN Price p ON sl.zip_code = p.zip_code AND DATE_FORMAT(eu.time_stamp, '%%Y-%%m-%%d %%H') = DATE_FORMAT(p.time_stamp, '%%Y-%%m-%%d %%H')
                WHERE eu.time_stamp BETWEEN %s AND %s
            """, [month_start, month_end]
            )
        total = cursor.fetchone()

        cursor.execute("""
            SELECT COUNT(DISTINCT location_id)
            FROM ServiceLocations
        """)


        num_loc = cursor.fetchone()
        if total[0] is None:
            return 0
        return total[0] / num_loc[0]

def compare_total_price_graph(my, average, month):
    my_total_price = my
    average_price = average
    x_label = month
    y_label = "Total Price (USD)"

    bar_positions = [0, 1]
    bar_width = 0.4

    plt.figure(figsize=(10, 5))
    bar1 = plt.bar(bar_positions[0], my_total_price, width=bar_width, color='blue', label='My Total Price')
    bar2 = plt.bar(bar_positions[1], average_price, width=bar_width, color='orange', label='Average Price')

    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height}', ha='center', va='bottom')

    add_labels(bar1)
    add_labels(bar2)

    plt.legend(loc='upper right')

    plt.title(f'Electricity Cost Comparison for {x_label}')
    plt.ylabel(y_label)
    plt.xticks(bar_positions, ['My Total Price', 'Average Price'])

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic3 = base64.b64encode(image_png).decode('utf-8')
    return graphic3