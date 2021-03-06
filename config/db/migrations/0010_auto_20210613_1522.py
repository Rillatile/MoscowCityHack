# Generated by Django 3.2.4 on 2021-06-13 12:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0009_auto_20210613_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barlayers',
            name='activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='db.activity'),
        ),
        migrations.AlterField(
            model_name='cafelayers',
            name='activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='db.activity'),
        ),
        migrations.AlterField(
            model_name='housechemiclayers',
            name='activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='db.activity'),
        ),
        migrations.AlterField(
            model_name='сosmeticsstorelayers',
            name='activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='db.activity'),
        ),
    ]
