# Generated by Django 3.2.4 on 2022-03-12 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_auto_20220310_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartproduct',
            name='price',
            field=models.DecimalField(decimal_places=1, max_digits=9),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=1, max_digits=9),
        ),
    ]
