# Generated by Django 3.2.4 on 2021-06-14 04:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0010_auto_20210613_1522'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='barbershoplayers',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='barbershoplayers',
            name='layer_ptr',
        ),
        migrations.RemoveField(
            model_name='barlayers',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='barlayers',
            name='layer_ptr',
        ),
        migrations.RemoveField(
            model_name='beautysaloonlayers',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='beautysaloonlayers',
            name='layer_ptr',
        ),
        migrations.RemoveField(
            model_name='cafelayers',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='cafelayers',
            name='layer_ptr',
        ),
        migrations.RemoveField(
            model_name='cliniclayers',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='cliniclayers',
            name='layer_ptr',
        ),
        migrations.RemoveField(
            model_name='dentistrylayers',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='dentistrylayers',
            name='layer_ptr',
        ),
        migrations.RemoveField(
            model_name='housechemiclayers',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='housechemiclayers',
            name='layer_ptr',
        ),
        migrations.RemoveField(
            model_name='supermarketlayers',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='supermarketlayers',
            name='layer_ptr',
        ),
        migrations.RemoveField(
            model_name='сosmeticsstorelayers',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='сosmeticsstorelayers',
            name='layer_ptr',
        ),
        migrations.DeleteModel(
            name='BakeryLayers',
        ),
        migrations.DeleteModel(
            name='BarbershopLayers',
        ),
        migrations.DeleteModel(
            name='BarLayers',
        ),
        migrations.DeleteModel(
            name='BeautySaloonLayers',
        ),
        migrations.DeleteModel(
            name='CafeLayers',
        ),
        migrations.DeleteModel(
            name='ClinicLayers',
        ),
        migrations.DeleteModel(
            name='DentistryLayers',
        ),
        migrations.DeleteModel(
            name='HouseChemicLayers',
        ),
        migrations.DeleteModel(
            name='SupermarketLayers',
        ),
        migrations.DeleteModel(
            name='СosmeticsStoreLayers',
        ),
    ]