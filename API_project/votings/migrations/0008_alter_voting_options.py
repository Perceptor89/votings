# Generated by Django 4.2.3 on 2023-07-09 07:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("votings", "0007_alter_character_photo"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="voting",
            options={"ordering": ["id"]},
        ),
    ]
