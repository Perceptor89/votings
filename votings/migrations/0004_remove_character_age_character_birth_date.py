# Generated by Django 4.2.3 on 2023-07-18 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votings', '0003_alter_exporttask_task_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='character',
            name='age',
        ),
        migrations.AddField(
            model_name='character',
            name='birth_date',
            field=models.DateField(default=None),
            preserve_default=False,
        ),
    ]
