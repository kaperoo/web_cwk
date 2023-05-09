import os
import sys
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'air_polonia.settings')
django.setup()

from airline.models import Booking, Flight, FlightSeat
from django.utils import timezone

# Retrieve bookings with "waiting for payment" status
bookings_to_check = Booking.objects.filter(status="Waiting for payment")

# Iterate through the bookings
for booking in bookings_to_check:
    # Check if the start_time of the booking was more than 1 hour ago
    time_difference = timezone.now() - booking.start_time
    if time_difference.total_seconds() >= 3600:

        # Add the seats back to the FlightSeat relationship
        flight = booking.flight
        passengers = booking.customers.all()
        for passenger in passengers:
            seat = passenger.seat
            flight_seat, created = FlightSeat.objects.get_or_create(flight=flight, seat=seat)
            if created:
                flight_seat.save()

        # Remove all passengers in the booking
        booking.customers.all().delete()

        print(f"Deleted booking with ID {booking.id}")
        # Remove the booking from the database
        booking.delete()