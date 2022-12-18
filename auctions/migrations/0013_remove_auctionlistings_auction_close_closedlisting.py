# Generated by Django 4.1.3 on 2022-12-17 13:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_alter_auctionlistings_highest_bid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auctionlistings',
            name='auction_close',
        ),
        migrations.CreateModel(
            name='ClosedListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(default='')),
                ('highest_bid', models.PositiveIntegerField(default=0)),
                ('image', models.ImageField(upload_to='items')),
                ('closed_at', models.DateTimeField(auto_now_add=True)),
                ('lister', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
