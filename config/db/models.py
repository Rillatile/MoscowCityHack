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


class Scope(models.Model):
    name = models.CharField(max_length=100)


class Activity(models.Model):
    name = models.CharField(max_length=100)
    scope = models.ForeignKey(to=Scope, on_delete=models.CASCADE)
    config = ArrayField(models.FloatField())


class Metric(models.Model):
    """
    Metric model - base info about analysed data.
    Fields:
     - name - name of metric
     - optim_config - array of boolean values (False - mean you should minimise that metric,
    True - mean you should maximize that metric)
    """
    name = models.CharField(max_length=100)
    optim_config = models.BooleanField(default=False)


class Layer(models.Model):
    metric = models.ForeignKey(
        to=Metric,
        on_delete=models.CASCADE,
        null=False
    )
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
    distance = models.FloatField()  # ?
    value = models.FloatField()


# *** Models of concrete activities that uses a service ***
