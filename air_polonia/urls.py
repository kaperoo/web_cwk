"""air_polonia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
import airline.views as views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/flight_list', views.flight_list, name='flight_list'),
    path('api/flight', views.flight_search, name='flight'),
    path('api/flight/<int:flight_id>', views.flight_details, name='flight_details'),
    path('api/book/<int:flight_id>', views.book_flight, name='book_flight'),
    path('api/pay/<int:booking_id>', views.confirm_payment, name='confirm_payment'),
    path('api/delete/<int:booking_id>', views.delete_booking, name='delete_booking'),
    path('api/booking_details/<int:booking_id>', views.booking_details, name='booking_details'),
    path('api/airports', views.airports, name='airports'),
]
