import uuid
from django.contrib.auth.models import User
from django.db import models


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
    bundle_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    history_id = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100)


class ModifiedSite(models.Model):
    _id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bundle_id = models.ForeignKey('ModifiedSitesBundle', on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    name = models.CharField(max_length=100)
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
