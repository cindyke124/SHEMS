from django.shortcuts import render, HttpResponse
# Create your views here.

def home(request):
    # request 是一个对象，封装了用户通过浏览器发送过来的所有数据
    # 获取请求方式 GET/POST
    # print(request.method)
    # 在URL上传递值
    # print(request.GET)

    return render(request,"home.html")

def customer_login(request):
    if request.method == "GET":
        # 去app目录下的templates目录寻找这个html
        return render(request, "customer_login.html")

    #如果是post请求，获取用户提交的数据
    # print(request.POST)
    id = request.POST.get("id")
    password = request.POST.get("password")
    submit_type = request.POST.get("submit_type")

    if submit_type == "Login":
        if id == '1' and password == "1":
            # return render(request, "home.html")
            return home(request)
        return render(request, "customer_login.html", {"error_msg": "Login failure caused by incorrect user name or password."})

    return register_page(request)

def energy_consumption(request):
    return render(request,"energy_consumption.html")

def register_page(request):
    return render(request, "register_page.html")
