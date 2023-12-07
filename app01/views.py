from django.shortcuts import render, HttpResponse


# Create your views here.

def home(request):
    # request 是一个对象，封装了用户通过浏览器发送过来的所有数据
    # 获取请求方式 GET/POST
    print(request.method)
    # 在URL上传递值
    print(request.GET)
    return HttpResponse("Welcome to SHEMS!")

def user_login(request):
    if request.method == "GET":
        # 去app目录下的templates目录寻找这个html
        return render(request, "user_login.html")

    #如果是post请求，获取用户提交的数据
    # print(request.POST)
    username = request.POST.get("username")
    password = request.POST.get("password")

    if username == '1' and password == "1":
        return render(request, "user_information.html")

    return render(request, "user_login.html", {"error_msg": "Login failure caused by incorrect user name or password."})

