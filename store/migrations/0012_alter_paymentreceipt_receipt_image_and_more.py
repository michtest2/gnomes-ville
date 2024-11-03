# Generated by Django 5.1.2 on 2024-11-03 13:03

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_alter_paymentreceipt_receipt_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentreceipt',
            name='receipt_image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]