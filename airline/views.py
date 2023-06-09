from django.http import JsonResponse
from .models import Flight, Seat, Luggage, Customer, Booking, FlightSeat, Airport, CustomerLuggage, CustomerSeat
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.db import transaction
import json
import datetime
import requests

# Endpoint for getting a list of flights
def flight_list(request):
    flights = Flight.objects.all()
    flight_data = []

    # Construct response data
    for flight in flights:

        luggage_pricing = {luggage.luggage_type: float(luggage.price) for luggage in Luggage.objects.all()}

        origin = {
            'id': flight.origin.id,
            'name': flight.origin.name,
            'city': flight.origin.city,
            'country': flight.origin.country,
            'code': flight.origin.code,
            'terminals': flight.origin.terminals
        }

        destination = {
            'id': flight.destination.id,
            'name': flight.destination.name,
            'city': flight.destination.city,
            'country': flight.destination.country,
            'code': flight.destination.code,
            'terminals': flight.destination.terminals
        }

        flight_data.append({
            'flight_id': flight.id,
            'price': float(flight.price),
            'airline': 'Air Polonia',
            'origin': origin,
            'destination': destination,
            'departure_time': flight.departure_time.isoformat(),
            'arrival_time': flight.arrival_time.isoformat(),
            'duration': int(flight.duration.total_seconds() / 60),
            'luggage_pricing': luggage_pricing,
            'priority_price': 5,
            'insurance_price': 10,
            'plane_type': flight.plane_type,
        })

    return JsonResponse({'flights': flight_data})

# Endpoint for getting details of the flight based on the flight id
@csrf_exempt
def flight_details(request, flight_id):
    # Check if queried flight exists
    try:
        flight = Flight.objects.get(id=flight_id)
    except Flight.DoesNotExist:
        return JsonResponse({'error': 'Flight not found'}, status=404)

    try:
        # Construct response data
        flight_data = []
        seats = flight.seats.all()
        seat_data = []

        for seat in seats:
            seat_data.append({
                'seat_id': seat.id,
                'seat_name': seat.name,
                'class': seat.seat_class,
                'price': float(seat.price + flight.price),
                'status': flight.flightseat_set.get(seat=seat).status,
            })

        luggage_pricing = {luggage.luggage_type: float(luggage.price) for luggage in Luggage.objects.all()}

        origin = {
            'id': flight.origin.id,
            'name': flight.origin.name,
            'city': flight.origin.city,
            'country': flight.origin.country,
            'code': flight.origin.code,
            'terminals': flight.origin.terminals
        }

        destination = {
            'id': flight.destination.id,
            'name': flight.destination.name,
            'city': flight.destination.city,
            'country': flight.destination.country,
            'code': flight.destination.code,
            'terminals': flight.destination.terminals
        }

        flight_data.append({
            'flight_id': flight.id,
            'price': float(flight.price),
            'airline': 'Air Polonia',
            'origin': origin,
            'destination': destination,
            'departure_time': flight.departure_time.isoformat(),
            'arrival_time': flight.arrival_time.isoformat(),
            'duration': int(flight.duration.total_seconds() / 60),
            'seats': seat_data,
            'luggage_pricing': luggage_pricing,
            'priority_price': 5,
            'insurance_price': 10,
            'plane_type': flight.plane_type,
        })
    except:
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

    return JsonResponse({'flights': flight_data})

# Endpoint for getting details about a specific flight based on destination and origin and date
@csrf_exempt
def flight_search(request):
    if request.method == 'POST':

        try:
            # Get the data from the request
            data = json.loads(request.body)

            origin = data.get('origin')
            destination = data.get('destination')
            departure_date = data.get('departure_date')
            number_of_people = data.get('number_of_people')
        except:
            return JsonResponse({'error': 'Bad Request'}, status=400)

        # Convert the departure_date to a datetime object
        departure_datetime = datetime.datetime.fromisoformat(departure_date)

        try:
            # find flights that match the origin, destination and departure date
            flights = Flight.objects.filter(
                origin__code=origin,
                destination__code=destination,
                departure_time__date=departure_datetime.date()
            ).annotate(available_seats=Count('seats')).filter(available_seats__gte=number_of_people)
        except:
            return JsonResponse({'error': 'Flight not found'}, status=404)

        flight_data = []

        try:
            # Construct response data
            for flight in flights:
                seats = flight.seats.all()
                seat_data = []

                for seat in seats:
                    seat_data.append({
                        'seat_id': seat.id,
                        'seat_name': seat.name,
                        'class': seat.seat_class,
                        'price': float(seat.price + flight.price),
                        'status': flight.flightseat_set.get(seat=seat).status,
                    })

                origin = {
                    'id': flight.origin.id,
                    'name': flight.origin.name,
                    'city': flight.origin.city,
                    'country': flight.origin.country,
                    'code': flight.origin.code,
                    'terminals': flight.origin.terminals
                }

                destination = {
                    'id': flight.destination.id,
                    'name': flight.destination.name,
                    'city': flight.destination.city,
                    'country': flight.destination.country,
                    'code': flight.destination.code,
                    'terminals': flight.destination.terminals
                }

                luggage_pricing = {luggage.luggage_type: float(luggage.price) for luggage in Luggage.objects.all()}

                flight_data.append({
                    'flight_id': flight.id,
                    'price': float(flight.price),
                    'airline': 'Air Polonia',
                    'origin': origin,
                    'destination': destination,
                    'departure_time': flight.departure_time.isoformat(),
                    'arrival_time': flight.arrival_time.isoformat(),
                    'duration': int(flight.duration.total_seconds() / 60),
                    'seats': seat_data,
                    'luggage_pricing': luggage_pricing,
                    'priority_price': 5,
                    'insurance_price': 10,
                    'plane_type': flight.plane_type,
                })
        except:
            return JsonResponse({'error': 'Internal Server Error'}, status=500)

        return JsonResponse({'flights': flight_data})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)    

# Endpoint for booking a flight
@csrf_exempt
def book_flight(request, flight_id):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Check if the flight exists
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return JsonResponse({'error': 'Flight not found'}, status=404)

        # Initiate the total price
        total_price = 0


        try:
            passengers_data = data.get('passengers')
            priority = data.get('priority')
            insurance = data.get('insurance')
        except:
            return JsonResponse({'error': 'Bad Request'}, status=400)

        # Use the atomic transaction to ensure that all database operations are rolled back if any of them fail
        with transaction.atomic():
            booking = Booking(
                flight=flight,
                price=flight.price,
                insurance=insurance,
                priority=priority,
                status="Waiting for payment",
                start_time=datetime.datetime.now()
            )
            booking.save()

            total_price += booking.price * len(passengers_data)
            passengers = []
            for passenger_data in passengers_data:
                try:
                    seat = Seat.objects.select_for_update().get(name=passenger_data['seat'])
                    flight_seat = FlightSeat.objects.select_for_update().get(flight=flight, seat=seat)
                except (Seat.DoesNotExist, FlightSeat.DoesNotExist):
                    transaction.set_rollback(True)
                    return JsonResponse({'error': 'Seat not found or already reserved'}, status=404)

                flight_seat.delete()

                total_price += seat.price

                luggage_list = [{"luggage": Luggage.objects.get(luggage_type=l['type']), "quantity": l['quantity']} for l in passenger_data['luggage']]

                passenger = Customer(
                    first_name=passenger_data['first_name'],
                    surname=passenger_data['last_name'],
                    passport=passenger_data['passport_id'],
                )
                passenger.save()

                # Add this after saving the passenger
                customer_seat = CustomerSeat(customer=passenger, seat=seat, flight=flight)
                customer_seat.save()

                # Calculate the price from luggage and add it to the total price
                for luggage_entry in luggage_list:
                    luggage = luggage_entry['luggage']
                    quantity = luggage_entry['quantity']
                    total_price += luggage.price * quantity
                    customer_luggage = CustomerLuggage(customer=passenger, luggage=luggage, quantity=quantity)
                    customer_luggage.save()

                booking.customers.add(passenger)
                passengers.append(passenger)

            booking.price = total_price
            booking.save()

        try:
            # Construct response data
            response_data = {
                'flight_id': flight_id,
                'booking_id': booking.id,
                'combined_price': float(booking.price),
                'passengers': [
                    {
                        'customer_id': passenger.id,
                        'first_name': passenger.first_name,
                        'last_name': passenger.surname,
                        'passport_id': passenger.passport,
                        'seat': CustomerSeat.objects.get(customer=passenger, flight=flight).seat.id,
                        'luggage': [{'type': cl.luggage.luggage_type, 'quantity': cl.quantity} for cl in passenger.customerluggage_set.all()]
                    }
                    for passenger in passengers
                ],
                'priority': priority,
                'insurance': insurance,
                'status': booking.status
            }
        except:
            return JsonResponse({'error': 'Internal Server Error'}, status=500)

        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# Function which requests a payment confirmation from the PSP API
def confirm_payment_with_psp(psp_provider, psp_checkout_id, amount_paid):

    # PSP API details
    PSP_APIS = {
        0: {
            "link": "http://sc20cah.pythonanywhere.com",
            "key": "1d79b10b-bb8b-4f84-9d57-49a183c6dd9e"
        },
        1: {
            "link": "http://sc20ap.pythonanywhere.com",
            "key": "1d79b10b-bb8b-4f84-9d57-49a183c6dd9e"
        },
        2: {
            "link": "http://sc20sh.pythonanywhere.com",
            "key": "1d79b10b-bb8b-4f84-9d57-49a183c6dd9e"
        }
    }

    # Send a GET request to the PSP API
    headers = {'Authorization': PSP_APIS[psp_provider]["key"]}
    url = f"{PSP_APIS[psp_provider]['link']}/api/checkout/{psp_checkout_id}/status"

    response = requests.get(url, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        response_data = response.json()

        # Check if the transaction status and amount match the booking details
        if ((response_data['status'] == "SUCCESSFUL" or response_data['status'] == "INPROGRESS") and
            float(response_data['amount']) == float(amount_paid)):
            return True
        else:
            return False
    else:
        return False

# Endpoint for confirming a payment
@csrf_exempt
def confirm_payment(request, booking_id):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Check if the booking exists
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)

        try:
            # Get the details from the request
            psp_provider = data.get('psp_provider')
            psp_checkout_id = data.get('psp_checkout_id')
            amount_paid = data.get('amount')
        except:
            return JsonResponse({'error': 'Bad Request'}, status=400)

        # If confirmed, update the booking status to PAID and return the booking details
        if confirm_payment_with_psp(psp_provider, psp_checkout_id, amount_paid):
            booking.status = 'PAID'
            booking.save()
            passengers = booking.customers.all()
            passenger_list = []
            for passenger in passengers:
                passenger_list.append({
                    'customer_id': passenger.id,
                    'first_name': passenger.first_name,
                    'last_name': passenger.surname,
                    'passport': passenger.passport,
                    'seat': CustomerSeat.objects.get(customer=passenger, flight=booking.flight).seat.id,
                    'luggage': [{'type': cl.luggage.luggage_type, 'quantity': cl.quantity} for cl in passenger.customerluggage_set.all()]
                })

            booking_data = {
                'booking_id': booking.id,
                'flight_id': booking.flight.id,
                'price': float(booking.price),
                'insurance': booking.insurance,
                'status': booking.status,
                'passengers': passenger_list,
            }
            return JsonResponse(booking_data)
        else:
            return JsonResponse({'error': 'Payment not confirmed'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# Endpoint for getting details of a booking
def booking_details(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)

    try:
        passengers = booking.customers.all()
        passenger_list = []
        for passenger in passengers:
            luggage_list = []
            customer_luggage = CustomerLuggage.objects.filter(customer=passenger)
            for cl in customer_luggage:
                luggage_list.append({
                    'type': cl.luggage.luggage_type,
                    'quantity': cl.quantity
                })

            # Get the seat for the current passenger
            customer_seat = CustomerSeat.objects.get(customer=passenger, flight=booking.flight)

            passenger_list.append({
                'customer_id': passenger.id,
                'first_name': passenger.first_name,
                'last_name': passenger.surname,
                'passport': passenger.passport,
                'seat': customer_seat.seat.name,  # Use the seat from CustomerSeat relationship
                'luggage': luggage_list
            })

        booking_data = {
            'booking_id': booking.id,
            'flight_id': booking.flight.id,
            'price': float(booking.price),
            'insurance': booking.insurance,
            'priority': booking.priority,
            'status': booking.status,
            'passengers': passenger_list,
        }
    except:
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

    return JsonResponse(booking_data)

# Endpoint for cancelling a booking
@csrf_exempt
def delete_booking(request, booking_id):
    if request.method == 'DELETE':
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)

        # Get all passengers in the booking
        passengers = booking.customers.all()

        # Remove all passenger-seat relationships for the booking and add the seats back to the FlightSeat relationship
        for passenger in passengers:
            customer_seat = CustomerSeat.objects.filter(customer=passenger, flight=booking.flight)
            for cs in customer_seat:
                FlightSeat.objects.create(flight=booking.flight, seat=cs.seat)
            customer_seat.delete()

            # Remove all customer-luggage relationships for the passenger
            customer_luggage = CustomerLuggage.objects.filter(customer=passenger)
            customer_luggage.delete()

        # Remove all passengers in the booking
        passengers.delete()

        # Remove the booking from the database
        booking.delete()

        return JsonResponse({'result': 'Deleted'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# Endpoint for getting a list of airports
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