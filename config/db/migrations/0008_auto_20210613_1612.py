# Generated by Django 3.2.4 on 2021-06-13 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0007_subway'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coordinatedata',
            name='house',
        ),
        migrations.RemoveField(
            model_name='coordinatedata',
            name='raw_values',
        ),
        migrations.RemoveField(
            model_name='coordinatedata',
            name='street',
        ),
    ]