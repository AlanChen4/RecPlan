from django.urls import path
from .views import *

urlpatterns = [
    path('', BundleList.as_view(), name='bundles'),
    path('bundles/', BundleList.as_view(), name='bundles'),
    path('bundle/<uuid:pk>/', BundleDetail.as_view(), name='bundle'),
    path('bundle/', BundleCreate.as_view(), name='bundle-create'),
    path('bundle/<uuid:pk>/update/', BundleUpdate.as_view(), name='bundle-update'),
    path('bundle/<uuid:pk>/delete/', BundleDelete.as_view(), name='bundle-delete'),

    path('modified-site/<uuid:pk>/<str:site_name>/', ModifiedSiteCreate.as_view(), name='modified-site-create'),
]