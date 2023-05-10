import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'air_polonia.settings')
django.setup()

from airline.models import Booking, FlightSeat, CustomerSeat
from django.utils import timezone
from django.db.models import Q

# Retrieve bookings with "waiting for payment" status
bookings_to_check = Booking.objects.filter(
    Q(status="Waiting for payment") & (Q(start_time__lte=timezone.now() - datetime.timedelta(hours=1)) | Q(flight__arrival_time__lt=timezone.now()))
)

# Iterate through the bookings
for booking in bookings_to_check:
    # Add the seats back to the FlightSeat relationship
    flight = booking.flight
    passengers = booking.customers.all()
    for passenger in passengers:
        customer_seat = CustomerSeat.objects.filter(customer=passenger, flight=booking.flight)
        for cs in customer_seat:
            FlightSeat.objects.create(flight=booking.flight, seat=cs.seat)
        customer_seat.delete()

    # Remove all passengers in the booking
    booking.customers.all().delete()

    print(f"Deleted booking with ID {booking.id}")
    # Remove the booking from the database
    booking.delete()