# Generated by Django 3.2 on 2022-06-06 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0053_alter_orderproduct_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderproduct',
            old_name='price_fixed',
            new_name='fixed_price',
        ),
    ]
