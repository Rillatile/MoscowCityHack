from django.contrib.postgres.fields import ArrayField
from django.db import models


class CoordinateData(models.Model):
    lon = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        verbose_name='Долгота'
    )
    lat = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        verbose_name='Широта'
    )
    street = models.CharField(
        max_length=255,
        null=False,
        blank=True,
        verbose_name='Улица'
    )
    house = models.CharField(
        max_length=10,
        null=False,
        blank=True,
        verbose_name='Номер дома'
    )
    raw_values = ArrayField(
        models.FloatField(),
        verbose_name='Необработанные значения'
    )
    processed_value = models.FloatField()
