# Generated by Django 4.2.16 on 2024-10-16 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0017_remove_listing_winner"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="picture",
            field=models.URLField(default=1),
            preserve_default=False,
        ),
    ]
