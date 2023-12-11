"""
URL configuration for SHEMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from app01 import views

urlpatterns = [
    # path('admin/', admin.site.urls),

    # www.xxx.com/index/
    path('home/<int:customer_id>/', views.home, name="home"),
    path('customer_login/', views.customer_login),
    path('register_page/', views.register_page),
    path('register_success/', views.register_success),
    path('energy_consumption/<int:customer_id>/', views.energy_consumption, name="energy_consumption"),
    path('account_management/<int:customer_id>/', views.account_management, name="account_management"),
    path('list_locations/', views.list_locations, name="service_locations")

]
