# Generated by Django 3.2 on 2022-06-03 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_alter_order_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='order_items',
            new_name='items',
        ),
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(max_length=250, verbose_name='Адрес'),
        ),
    ]
