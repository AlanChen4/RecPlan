from django.db import models
from authentication.models import CustomUser


class Product(models.Model):
    name = models.CharField(max_length=100)
    price_id = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class StripeCustomer(models.Model):
    user = models.OneToOneField(to=CustomUser, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)
    stripeSubscriptionId = models.CharField(max_length=255)

    def __str__(self):
        return self.user.email