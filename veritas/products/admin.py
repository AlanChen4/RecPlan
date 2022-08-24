from django.contrib import admin
from .models import Product, StripeCustomer


admin.site.register(Product)
admin.site.register(StripeCustomer)
