from django.contrib.postgres.fields import ArrayField
from django.db import models


class CoordinateData(models.Model):
    lon = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        verbose_name='Долгота'
    )
    lat = models.CharField(
        max_length=20,
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


class WAP(models.Model):
    mac = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        verbose_name='ID точки доступа'
    )
    lon = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        verbose_name='Долгота'
    )
    lat = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        verbose_name='Широта'
    )


class OrganizationData(models.Model):
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name='Название организации'
    )
    address = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )
    lon = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        verbose_name='Долгота'
    )
    lat = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        verbose_name='Широта'
    )
