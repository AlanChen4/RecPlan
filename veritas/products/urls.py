from django.urls import path
from .views import *


urlpatterns = [
    path('success/<str:session_id>/', SuccessView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('webhook', WebhookView, name='webhook'),
    path('subscription/', ProductLandingPageView.as_view(), name='add-subscription'),
    path('create-portal-session/', CreatePortalSessionView.as_view(), name='create-portal-session'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('cancel-subscription/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
]