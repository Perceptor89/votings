# Generated by Django 4.2.3 on 2023-07-17 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("votings", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exporttask",
            name="e_mail",
            field=models.EmailField(default=None, max_length=254),
            preserve_default=False,
        ),
    ]