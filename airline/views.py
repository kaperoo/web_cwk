from django.http import JsonResponse
from .models import Flight, Seat, Luggage, Customer, Booking, FlightSeat, Airport
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
import json
import datetime
import requests

def flight_list(request):
    flights = Flight.objects.all()
    flight_data = []

    for flight in flights:
        seats = flight.seats.all()
        seat_data = []

        for seat in seats:
            seat_data.append({
                'seat_id': seat.id,
                'seat_name': seat.name,
                'class': seat.seat_class,
                'price': float(seat.price + flight.price),
                'status': 'Available',  # Assuming all seats are available
            })

        luggage_pricing = {luggage.luggage_type: float(luggage.price) for luggage in Luggage.objects.all()}

        flight_data.append({
            'flight_id': flight.id,
            'price': flight.price,
            'airline': 'Air Polonia',
            'origin': flight.origin.code,
            'destination': flight.destination.code,
            'departure_time': flight.departure_time.isoformat(),
            'arrival_time': flight.arrival_time.isoformat(),
            'duration': int(flight.duration.total_seconds() / 60),
            'seats': seat_data,
            'luggage_pricing': luggage_pricing,
            'priority_price': 5,
            'insurance_price': 10,
            'plane_type': flight.plane_type,
        })

    return JsonResponse({'flights': flight_data})

@csrf_exempt
def flight_search(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        origin = data.get('origin')
        destination = data.get('destination')
        departure_date = datetime.datetime.strptime(data.get('departure_date'), '%Y-%m-%d').date()
        number_of_people = data.get('number_of_people')

        flights = Flight.objects.filter(
            origin__code=origin,
            destination__code=destination,
            departure_time__date=departure_date
        ).annotate(available_seats=Count('seats')).filter(available_seats__gte=number_of_people)

        flight_data = []

        for flight in flights:
            seats = flight.seats.all()
            seat_data = []

            for seat in seats:
                seat_data.append({
                    'seat_id': seat.id,
                    'seat_name': seat.name,
                    'class': seat.seat_class,
                    'price': float(seat.price + flight.price),
                    'status': 'Available',  # Assuming all seats are available
                })

            luggage_pricing = {luggage.luggage_type: float(luggage.price) for luggage in Luggage.objects.all()}

            flight_data.append({
                'flight_id': flight.id,
                'price': flight.price,
                'airline': 'Air Polonia',
                'origin': flight.origin.code,
                'destination': flight.destination.code,
                'departure_time': flight.departure_time.isoformat(),
                'arrival_time': flight.arrival_time.isoformat(),
                'duration': int(flight.duration.total_seconds() / 60),
                'seats': seat_data,
                'luggage_pricing': luggage_pricing,
                'priority_price': 5,
                'insurance_price': 10,
                'plane_type': flight.plane_type,
            })

        return JsonResponse({'flights': flight_data})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)    

@csrf_exempt
def book_flight(request, flight_id):
    if request.method == 'POST':
        data = json.loads(request.body)

        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return JsonResponse({'error': 'Flight not found'}, status=404)
        
        total_price = 0

        passengers_data = data.get('passengers')
        priority = data.get('priority')
        insurance = data.get('insurance')

        booking = Booking(
            flight=flight,
            price=flight.price,  # Replace with your logic to calculate the combined price
            insurance=insurance,
            status="Waiting for payment",
            start_time=datetime.datetime.now()
        )
        booking.save()

        total_price += booking.price * len(passengers_data)
        passengers = []
        for passenger_data in passengers_data:
            seat = Seat.objects.get(id=passenger_data['seat'])

            # Remove the seat from the FlightSeat relationship
            flight_seat = FlightSeat.objects.get(flight=flight, seat=seat)
            flight_seat.delete()

            total_price += seat.price

            luggage_list = [Luggage.objects.get(luggage_type=l) for l in passenger_data['luggage']]

            for luggage in luggage_list:
                total_price += luggage.price

            passenger = Customer(
                first_name=passenger_data['first_name'],
                surname=passenger_data['surname'],
                passport=passenger_data['passportID'],
                seat=seat,
                luggage=luggage_list
            )
            passenger.save()
            passenger.luggage_set.set(luggage_list)
            booking.customers.add(passenger)
            passengers.append(passenger)

        booking.price = total_price
        booking.save()

        response_data = {
            'flight_id': flight_id,
            'booking_id': booking.id,
            'combined_price': float(booking.price),
            'passengers': [
                {
                    'customer_id': passenger.id,
                    'first_name': passenger.first_name,
                    'surname': passenger.surname,
                    'passportID': passenger.passport,
                    'seat': passenger.seat.id,
                    'luggage': [l.luggage_type for l in passenger.luggage_set.all()]
                }
                for passenger in passengers
            ],
            'priority': priority,
            'insurance': insurance,
            'status': booking.status
        }

        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def confirm_payment_with_psp(psp_provider, psp_checkout_id, amount_paid):
    # Replace 'your-api-key' with the actual API key for the PSP
    headers = {'Authorization': 'Bearer your-api-key'}
    url = f"https://{psp_provider}/api/checkout/{psp_checkout_id}/status"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()

        # Check if the transaction status and amount match the booking details
        if ((response_data['status'] == "SUCCESSFUL" or response_data['status'] == "INPROGRESS") and
            float(response_data['amount']) == float(amount_paid)):
            return True
        else:
            return False
    else:
        # Handle error response from the PSP API
        return False

@csrf_exempt
def confirm_payment(request, booking_id):
    if request.method == 'POST':
        data = json.loads(request.body)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)

        psp_provider = data.get('psp_provider')
        psp_checkout_id = data.get('psp_checkout_id')
        amount_paid = data.get('amount_paid')

        if confirm_payment_with_psp(psp_provider, psp_checkout_id, amount_paid):
            booking.status = 'PAID'
            booking.save()
            passengers = booking.customers.all()
            passenger_list = []
            for passenger in passengers:
                passenger_list.append({
                    'customer_id': passenger.id,
                    'first_name': passenger.first_name,
                    'surname': passenger.surname,
                    'passport': passenger.passport,
                    'seat': passenger.seat.name,
                    'luggage': passenger.luggage
                })

            booking_data = {
                'booking_id': booking.id,
                'flight_id': booking.flight.id,
                'price': booking.price,
                'insurance': booking.insurance,
                'status': booking.status,
                'passengers': passenger_list,
            }
            return JsonResponse(booking_data)
        else:
            return JsonResponse({'error': 'Payment not confirmed'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def booking_details(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)

    passengers = booking.customers.all()
    passenger_list = []
    for passenger in passengers:
        passenger_list.append({
            'customer_id': passenger.id,
            'first_name': passenger.first_name,
            'surname': passenger.surname,
            'passport': passenger.passport,
            'seat': passenger.seat.name,
            'luggage': passenger.luggage
        })

    booking_data = {
        'booking_id': booking.id,
        'flight_id': booking.flight.id,
        'price': booking.price,
        'insurance': booking.insurance,
        'status': booking.status,
        'passengers': passenger_list,
    }

    return JsonResponse(booking_data)

@csrf_exempt
def delete_booking(request, booking_id):
    if request.method == 'DELETE':
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)

        # Remove all passengers in the booking
        booking.customers.all().delete()

        # Add the seats back to the FlightSeat relationship
        flight = booking.flight
        seats = flight.seats.all()
        for seat in seats:
            flight_seat, created = FlightSeat.objects.get_or_create(flight=flight, seat=seat)
            if created:
                flight_seat.save()

        # Remove the booking from the database
        booking.delete()

        return JsonResponse({'result': 'Deleted'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def airports(request):
    airports = Airport.objects.all()

    airport_list = []
    for airport in airports:
        airport_list.append({
            'id': airport.id,
            'name': airport.name,
            'country': airport.country,
            'city': airport.city,
            'code': airport.code,
            'terminals': airport.terminals
        })

    return JsonResponse({'airports': airport_list})