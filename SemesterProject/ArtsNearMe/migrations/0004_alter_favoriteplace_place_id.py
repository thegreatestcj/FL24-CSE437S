# Generated by Django 5.1.1 on 2024-10-30 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ArtsNearMe', '0003_alter_favoriteevent_event_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favoriteplace',
            name='place_id',
            field=models.CharField(max_length=100),
        ),
    ]
