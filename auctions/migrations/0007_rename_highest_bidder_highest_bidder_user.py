# Generated by Django 4.1.3 on 2022-12-08 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_remove_bid_auction_close_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='highest_bidder',
            old_name='highest_bidder',
            new_name='user',
        ),
    ]
