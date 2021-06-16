from django.contrib.postgres.fields import ArrayField
from django.conf import settings

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
    metric = models.ForeignKey(
        to='Metric', on_delete=models.CASCADE, null=True)
    processed_value = models.FloatField()
    activity = models.ForeignKey(to='Activity', null=True, default=None, on_delete=models.CASCADE)


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
    table_name = models.CharField(max_length=50, null=True)

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


# *** Models of concrete activities that uses a service ***
class LayerAbstract(models.Model):
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
    activity = models.ForeignKey(to='Activity', on_delete=models.CASCADE, null=True, default=None)

    class Meta:
        abstract = True


class Layer(LayerAbstract):
    ...


# Food retail Scope
class SupermarketLayers(LayerAbstract):
    ...


class BakeryLayers(LayerAbstract):
    ...


# Beauty Scope
class BarbershopLayers(LayerAbstract):
    ...


class BeautySaloonLayers(LayerAbstract):
    ...


# Public catering Scope
class CafeLayers(LayerAbstract):
    ...


class BarLayers(LayerAbstract):
    ...


# Household chemicals Scope
class СosmeticsStoreLayers(LayerAbstract):
    ...


class HouseChemicLayers(LayerAbstract):
    ...


# Health Scope
class DentistryLayers(LayerAbstract):
    ...


class ClinicLayers(LayerAbstract):
    ...


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