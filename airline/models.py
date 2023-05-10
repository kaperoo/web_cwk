from django.db import models

# Airport table to store information about airports
class Airport(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    terminals = models.IntegerField()

    def __str__(self):
        return self.name

# Flight table to store information about flights
class Flight(models.Model):
    id = models.AutoField(primary_key=True)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    duration = models.DurationField()
    plane_type = models.CharField(max_length=100)
    number_of_seats = models.IntegerField()
    seats = models.ManyToManyField('Seat', through='FlightSeat')

    def __str__(self):
        return f"#{self.id} {self.origin.code} - {self.destination.code} ({self.departure_time.date()})"

# Seat table to store information about seats
class Seat(models.Model):
    seat_class = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

# Intermediate table to store information about seats on flights
class FlightSeat(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default='Available')

    class Meta:
        unique_together = ('flight', 'seat')

    def __str__(self):
        return f"{self.flight} - {self.seat}"

# Luggage table to store information about types of luggage
class Luggage(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    luggage_type = models.CharField(max_length=100)

    def __str__(self):
        return self.luggage_type

# Customer table to store information about customers
class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    luggages = models.ManyToManyField(Luggage, through='CustomerLuggage')
    passport = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.surname} #{self.id}"

# Intermediate table to store information about seats booked by customers
class CustomerSeat(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.customer.surname} {self.customer.id}# - Seat: {self.seat.name} on Flight {self.flight.id}#"

# Intermediate table to store information about luggage booked by customers
class CustomerLuggage(models.Model): 
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    luggage = models.ForeignKey(Luggage, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.customer} - {self.luggage} (x{self.quantity})"

# Booking table to store information about bookings
class Booking(models.Model):
    id = models.AutoField(primary_key=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    customers = models.ManyToManyField(Customer) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    insurance = models.BooleanField(default=False)
    status = models.CharField(max_length=100)
    start_time = models.DateTimeField()

    def __str__(self):
        return f"Booking #{self.id} - Flight {self.flight}"
