# Generated by Django 4.2.6 on 2023-11-12 06:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0003_order_alter_cart_options_alter_cartitem_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ("id",)},
        ),
        migrations.AlterModelOptions(
            name="orderitem",
            options={"ordering": ("id",)},
        ),
    ]
