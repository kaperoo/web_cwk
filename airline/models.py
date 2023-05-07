from django.db import models

class Airport(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    terminals = models.IntegerField()

    def __str__(self):
        return self.name


class Flight(models.Model):
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
        return f"{self.origin} - {self.destination}"


class Seat(models.Model):
    seat_class = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class FlightSeat(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('flight', 'seat')

    def __str__(self):
        return f"{self.flight} - {self.seat}"


class Luggage(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    luggage_type = models.CharField(max_length=100)

    def __str__(self):
        return self.luggage_type

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    seat = models.OneToOneField(Seat, on_delete=models.SET_NULL, null=True)
    luggages = models.ManyToManyField(Luggage, through='CustomerLuggage')
    passport = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.surname}"

class CustomerLuggage(models.Model): 
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    luggage = models.ForeignKey(Luggage, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.customer} - {self.luggage} (x{self.quantity})"

class Booking(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    customers = models.ManyToManyField(Customer) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    insurance = models.BooleanField(default=False)
    status = models.CharField(max_length=100)
    start_time = models.DateTimeField()

    def __str__(self):
        return f"{self.customer} - {self.flight}"
