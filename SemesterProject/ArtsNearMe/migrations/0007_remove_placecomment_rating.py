# Generated by Django 5.1.1 on 2024-11-21 06:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ArtsNearMe', '0006_placecomment_updated_at_alter_placecomment_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='placecomment',
            name='rating',
        ),
    ]
