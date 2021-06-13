from os import access
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

from django.db import models
from django.db.models.expressions import F


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
    metric = models.ForeignKey(
        to='Metric', on_delete=models.CASCADE, null=True)
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


class Device(models.Model):
    device_hash = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name='Hash идентификатора wi-fi клиента'
    )


class User(models.Model):
    user_hash = models.CharField(
        max_length=50,
        null=True,
        blank=False,
        verbose_name='Hash идентификатора пользователя'
    )


class Connection(models.Model):
    datetime = models.DateTimeField(
        null=False,
        verbose_name='Дата и время подключения к wi-fi'
    )
    access_point = models.ForeignKey(
        to=WAP,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Точка доступа'
    )
    device = models.ForeignKey(
        to=Device,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Устройство'
    )
    user = models.ForeignKey(
        to=User,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )


class Scope(models.Model):
    name = models.CharField(max_length=100)

    def __repr__(self):
        return self.name


class Activity(models.Model):
    name = models.CharField(max_length=100)
    scope = models.ForeignKey(to=Scope, on_delete=models.CASCADE)
    config = ArrayField(models.FloatField())

    def __repr__(self):
        return self.name


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
    type = models.ForeignKey(
        to=Activity,
        on_delete=models.CASCADE,
        verbose_name='Вид деятельности'
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


class RentalData(models.Model):
    price = models.IntegerField(
        verbose_name='Цена аренды'
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
    
class FlatsData(models.Model):
    flats = models.IntegerField(
        verbose_name='Количество квартир'
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
    
class OfficesData(models.Model):
    price = models.IntegerField(
        verbose_name='Цена аренды'
    )
    area = models.FloatField(
       verbose_name='Площадь'
    )
    address = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )
    link = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name='Ссылка на объявление'
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

class Metric(models.Model):
    """
    Metric model - base info about analysed data.
    Fields:
     - name - name of metric (Проходимость, Стоимость площади, Заселенность, Похожие организации)
     - optim_config - boolean value (False - mean you should minimise that metric,
    True - mean you should maximize that metric)
    """
    OPERATION_CHOICES = (
        ('sum', 'Sum'),
        ('ave', 'Average'),
    )
    name = models.CharField(max_length=100)
    optim_config = models.BooleanField(default=False)
    generalizing_oper = models.CharField(max_length=3, choices=OPERATION_CHOICES, default='ave')

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False


# *** Models of concrete activities that uses a service ***
class Layer(models.Model):
    metric = models.ForeignKey(
        to='Metric',
        on_delete=models.CASCADE,
        null=False
    )
    lon = models.FloatField(verbose_name='Долгота')
    lat = models.FloatField(verbose_name='Широта')
    lon_distance = models.FloatField(default=settings.LON_DISTANCE)
    lat_distance = models.FloatField(default=settings.LAT_DISTANCE)
    value = models.FloatField()


# Food retail Scope
# todo: add two or more activity types to Food retail Scope

# Beauty Scope
class BarbershopLayers(Layer):
    activity = models.ForeignKey(to='Activity', on_delete=models.CASCADE, null=True)
# todo: add one activity type to Beauty Scope


# Public catering Scope
class CafeLayers(Layer):
    activity = models.ForeignKey(to='Activity', on_delete=models.CASCADE, null=True)


class BarLayers(Layer):
    activity = models.ForeignKey(to='Activity', on_delete=models.CASCADE, null=True)


# Household chemicals Scope
class СosmeticsStoreLayers(Layer):
    activity = models.ForeignKey(to='Activity', on_delete=models.CASCADE, null=True)


class HouseChemicLayers(Layer):
    activity = models.ForeignKey(to='Activity', on_delete=models.CASCADE, null=True)


# Health Scope
class DentistryLayers(Layer):
    activity = models.ForeignKey(to='Activity', on_delete=models.CASCADE, null=True)


class ClinicLayers(Layer):
    activity = models.ForeignKey(to='Activity', on_delete=models.CASCADE, null=True)


class Subway(models.Model):
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


# Services Scope
# todo: come up with at least two types of activities for this Scope
# e.g.:
# class SomeServiceLayers(Layer):
#     ...
#
# class AnotherServiceLayers(Layer):
#     ...
