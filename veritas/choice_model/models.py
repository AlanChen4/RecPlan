import uuid
from django.db import models
from authentication.models import CustomUser


class Site(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    acres = models.FloatField()
    trails = models.IntegerField()
    trail_miles = models.FloatField()
    picnic_area = models.IntegerField()
    sports_facilities = models.IntegerField()
    swimming_facilities = models.IntegerField()
    boat_launch = models.IntegerField()
    waterbody = models.IntegerField()
    bathrooms = models.IntegerField()
    playgrounds = models.IntegerField()

    def __str__(self):
        return self.name


class ModifiedSitesBundle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.nickname} ({self.user.email})'


CHOICES = (
    (0, 'No'),
    (1, 'Yes')
)
class ModifiedSite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bundle = models.ForeignKey('ModifiedSitesBundle', on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    name = models.CharField(max_length=100)
    acres = models.FloatField()
    trails = models.IntegerField()
    trail_miles = models.FloatField()
    picnic_area = models.IntegerField(choices=CHOICES)
    sports_facilities = models.IntegerField(choices=CHOICES)
    swimming_facilities = models.IntegerField(choices=CHOICES)
    boat_launch = models.IntegerField(choices=CHOICES)
    waterbody = models.IntegerField(choices=CHOICES)
    bathrooms = models.IntegerField()
    playgrounds = models.IntegerField(choices=CHOICES)


class BaselineModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    selected = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} ({self.user.email})'


class BaselineSite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    baseline_model = models.ForeignKey(BaselineModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    visits = models.FloatField()

    def __str__(self):
        return f'{self.name} ({self.baseline_model.name})'
