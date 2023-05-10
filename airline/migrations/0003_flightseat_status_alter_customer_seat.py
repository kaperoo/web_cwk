# Generated by Django 4.1.6 on 2023-05-09 23:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('airline', '0002_luggage_remove_customer_luggage_airport_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='flightseat',
            name='status',
            field=models.CharField(default='Available', max_length=100),
        ),
        migrations.AlterField(
            model_name='customer',
            name='seat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airline.flightseat'),
        ),
    ]
