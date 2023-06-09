# Generated by Django 4.1.6 on 2023-05-10 00:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('airline', '0003_flightseat_status_alter_customer_seat'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='seat',
        ),
        migrations.CreateModel(
            name='CustomerSeat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airline.customer')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airline.flight')),
                ('seat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airline.seat')),
            ],
        ),
    ]
