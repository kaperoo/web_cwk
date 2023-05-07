from django.contrib import admin

# Register your models here.
from .models import Airport, Flight, Seat, FlightSeat, Customer, Luggage, CustomerLuggage

admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(Seat)
admin.site.register(FlightSeat)
admin.site.register(Customer)
admin.site.register(Luggage)
admin.site.register(CustomerLuggage)