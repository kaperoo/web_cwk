from django.contrib import admin

# Register your models here.
from .models import Airport, Flight, Seat, FlightSeat, Customer, Luggage, CustomerLuggage, Booking, CustomerSeat

admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(Seat)
admin.site.register(FlightSeat)
admin.site.register(Customer)
admin.site.register(Luggage)
admin.site.register(CustomerLuggage)
admin.site.register(Booking)
admin.site.register(CustomerSeat)