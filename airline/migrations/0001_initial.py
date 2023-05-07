# Generated by Django 4.1.6 on 2023-05-05 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=10)),
                ('terminals', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('departure_time', models.DateTimeField()),
                ('arrival_time', models.DateTimeField()),
                ('duration', models.DurationField()),
                ('plane_type', models.CharField(max_length=100)),
                ('number_of_seats', models.IntegerField()),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arrivals', to='airline.airport')),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departures', to='airline.airport')),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat_class', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='FlightSeat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airline.flight')),
                ('seat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airline.seat')),
            ],
            options={
                'unique_together': {('flight', 'seat')},
            },
        ),
        migrations.AddField(
            model_name='flight',
            name='seats',
            field=models.ManyToManyField(through='airline.FlightSeat', to='airline.seat'),
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('surname', models.CharField(max_length=100)),
                ('luggage', models.IntegerField()),
                ('passport', models.CharField(max_length=20)),
                ('seat', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='airline.seat')),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('insurance', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=100)),
                ('start_time', models.DateTimeField()),
                ('customers', models.ManyToManyField(to='airline.customer')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airline.flight')),
            ],
        ),
    ]