from django.contrib import admin
from .models import *


admin.site.register(BaselineModel)
admin.site.register(BaselineSite)
admin.site.register(Site)
admin.site.register(ModifiedSite)
admin.site.register(ModifiedSitesBundle)
