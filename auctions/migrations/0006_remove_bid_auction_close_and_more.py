# Generated by Django 4.1.3 on 2022-12-08 09:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_auctionlistings_highest_bid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bid',
            name='auction_close',
        ),
        migrations.AddField(
            model_name='auctionlistings',
            name='auction_close',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Highest_bidder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('highest_bidder', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
