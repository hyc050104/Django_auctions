# Generated by Django 5.0.3 on 2024-04-10 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_alter_bid_bid_item_alter_bid_bidder'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='wathlist',
            new_name='watchlist',
        ),
    ]
