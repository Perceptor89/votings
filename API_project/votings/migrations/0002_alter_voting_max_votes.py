# Generated by Django 4.2.3 on 2023-07-09 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("votings", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="voting",
            name="max_votes",
            field=models.IntegerField(),
        ),
    ]
