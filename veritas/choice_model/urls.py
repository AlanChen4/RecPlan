from django.urls import path
from .views import *

urlpatterns = [
    path('', BundleList.as_view(), name='bundles'),
    path('bundles/', BundleList.as_view(), name='bundles'),
    path('bundle/<uuid:pk>/', BundleDetail.as_view(), name='bundle'),
    path('bundle-create/', BundleCreate.as_view(), name='bundle-create'),
    path('bundle-update/<uuid:pk>/', BundleUpdate.as_view(), name='bundle-update'),
    path('bundle-delete/<uuid:pk>/', BundleDelete.as_view(), name='bundle-delete'),

    path('modified-site-create/<uuid:pk>/<str:site_name>/', ModifiedSiteCreate.as_view(), name='modified-site-create'),
]