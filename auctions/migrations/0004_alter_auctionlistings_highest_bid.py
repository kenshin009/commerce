# Generated by Django 4.1.3 on 2022-12-05 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auctionlistings_highest_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlistings',
            name='highest_bid',
            field=models.PositiveIntegerField(default=models.PositiveIntegerField()),
        ),
    ]
