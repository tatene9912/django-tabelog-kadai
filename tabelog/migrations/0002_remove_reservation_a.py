# Generated by Django 5.1 on 2024-09-04 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tabelog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='a',
        ),
    ]
