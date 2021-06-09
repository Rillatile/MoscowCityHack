# Generated by Django 3.2.4 on 2021-06-09 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='coordinatedata',
            name='house',
            field=models.CharField(blank=True, max_length=10, verbose_name='Номер дома'),
        ),
        migrations.AddField(
            model_name='coordinatedata',
            name='street',
            field=models.CharField(blank=True, max_length=255, verbose_name='Улица'),
        ),
    ]
