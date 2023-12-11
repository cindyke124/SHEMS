from django.shortcuts import render, HttpResponse
from django.db import connection
# Create your views here.

def home(request):
    return render(request,"home.html")

def customer_login(request):
    if request.method == "GET":
        # 去app目录下的templates目录寻找这个html
        return render(request, "customer_login.html")

    #如果是post请求，获取用户提交的数据
    # print(request.POST)
    # submit_type = request.POST.get("submit_type")
    id = request.POST.get("id")
    password = request.POST.get("password")
    if id == '1' and password == "1":
        # return render(request, "home.html")
        return home(request)
    return render(request, "customer_login.html", {"error_msg": "Login failure caused by incorrect user name or password."})


def register_page(request):
    print("method:", request.method)
    if request.method == "GET":
        return render(request, "register_page.html")

    name = request.POST.get("name")
    password = request.POST.get("password")
    billing_address = request.POST.get("billing_address")

    return render(request, "register_success.html")

def register_success(request):
    return render(request,"register_success.html")

def energy_consumption(request):
    return render(request,"energy_consumption.html")



def service_locations(request):
    # 获取数据库中的所有service location信息
    data_list = [1,2,3]
    return render(request,"service_locations.html", {"data_list":data_list})


