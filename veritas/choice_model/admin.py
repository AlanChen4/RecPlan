from django.contrib import admin
from .models import Site, ModifiedSite, ModifiedSitesBundle


admin.site.register(Site)
admin.site.register(ModifiedSite)
admin.site.register(ModifiedSitesBundle)
