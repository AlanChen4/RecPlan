from django.urls import path
from .views import *

urlpatterns = [
    path('', BundleList, name='bundles'),
    path('models/', BundleList, name='bundles'),
    path('models/<uuid:bundle_id>/', BundleList, name='bundles'),
    path('model/', BundleCreate.as_view(), name='bundle-create'),
    path('model/<uuid:pk>/update/', BundleUpdate.as_view(), name='bundle-update'),
    path('model/<uuid:pk>/delete/', BundleDelete.as_view(), name='bundle-delete'),

    path('site/<uuid:pk>/', SiteCreate, name='site-create'),
    path('modified-site/<uuid:pk>/delete/', ModifiedSiteDelete.as_view(), name='modified-site-delete'),
    path('modified-site/<uuid:pk>/<str:site_name>/', ModifiedSiteCreate.as_view(), name='modified-site-create'),
    path('modified-site/<uuid:pk>/<str:site_name>/update/', ModifiedSiteUpdate.as_view(), name='modified-site-update'),

    path('recalibrate/', RecalibrateBaseline, name='recalibrate-baseline'),
    path('baseline/edit/<uuid:baseline_id>/', EditBaseline, name='edit-baseline'),
    path('baseline/delete/<uuid:baseline_id>/', DeleteBaseline, name='delete-baseline'),
]