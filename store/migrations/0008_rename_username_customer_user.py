# Generated by Django 5.1.2 on 2024-10-29 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_shipping_country'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='username',
            new_name='user',
        ),
    ]