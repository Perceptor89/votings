# Generated by Django 4.2.3 on 2023-07-17 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("votings", "0002_alter_exporttask_e_mail"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exporttask",
            name="task_id",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
