# Generated by Django 4.1.6 on 2023-05-10 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airline', '0004_remove_customer_seat_customerseat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='airport',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='booking',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='customer',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='flight',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
