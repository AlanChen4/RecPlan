from django.urls import path
from .views import *

urlpatterns = [
    path('', BundleList.as_view(), name='bundles'),
    path('models/', BundleList.as_view(), name='bundles'),
    path('model/<uuid:pk>/', BundleDetail.as_view(), name='bundle'),
    path('model/', BundleCreate.as_view(), name='bundle-create'),
    path('model/<uuid:pk>/update/', BundleUpdate.as_view(), name='bundle-update'),
    path('model/<uuid:pk>/delete/', BundleDelete.as_view(), name='bundle-delete'),

    path('modified-site/<uuid:pk>/<str:site_name>/', ModifiedSiteCreate.as_view(), name='modified-site-create'),
]