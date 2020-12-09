# Generated by Django 3.1.1 on 2020-12-04 16:42

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20201204_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_image',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='profile_picture'),
        ),
    ]