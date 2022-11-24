import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from authentication.models import CustomUser
from .models import Product, StripeCustomer


stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(TemplateView):
    template_name = 'products/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'session_id': self.kwargs['session_id']
        })
        return context


class CancelView(TemplateView):
    template_name = 'products/cancel.html'


class ProductLandingPageView(TemplateView):
    template_name = 'products/product.html'

    def get_context_data(self):
        context = super().get_context_data()

        try:
            stripe_customer = StripeCustomer.objects.get(user=self.request.user)
            subscription = stripe.Subscription.retrieve(stripe_customer.stripeSubscriptionId)
            product = stripe.Product.retrieve(subscription.plan.product)
            context.update({
                'subscription': subscription,
                'product': product,
                'PRICE_LOOKUP_KEY': Product.objects.get(name='RecPlan Monthly Subscription').price_id
            })
        except StripeCustomer.DoesNotExist:
            context.update({
                'PRICE_LOOKUP_KEY': Product.objects.get(name='RecPlan Monthly Subscription').price_id
            })
        return context


@csrf_exempt
def WebhookView(request, *args, **kwargs):
    try:
        payload = request.body
        event = json.loads(payload)
    except ValueError as e:
        print("Webhook error while parsing basic request." + str(e))
        return JsonResponse({"success": True}, status=400)

    # Handling a new subscription
    if event and event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fetch all the required data from session
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')

        # Get the user and create a new StripeCustomer
        user = CustomUser.objects.get(id=client_reference_id)
        StripeCustomer.objects.create(
            user=user,
            stripeCustomerId=stripe_customer_id,
            stripeSubscriptionId=stripe_subscription_id,
        )
        print(user.email + ' just subscribed.')

    # Handling a subscription being cancelled on the dashboard
    if event and event["type"] == "customer.subscription.deleted":
        print("customer.subscription.deleted") # log event

        session = event['data']['object']
        stripe_subscription_id = session.get('subscription')

        # Retrieve StripeCustomer instance with said subscription id
        req_userprofile = StripeCustomer.objects.get(stripe_subscription_id=stripe_subscription_id)
        req_userprofile.delete()

    return JsonResponse({"success": True}, status=200)



class CreatePortalSessionView(View):
    def post(self, request, *args, **kwargs):
        checkout_session_id = request.POST['session_id']
        checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)

        return_url = f'http://{request.get_host()}'

        portalSession = stripe.billing_portal.Session.create(
            customer=checkout_session.customer,
            return_url=return_url,
        )
        return redirect(portalSession.url, code=303)       


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = f'http://{request.get_host()}'
        lookup_keys = [request.POST['lookup_key']]

        prices = stripe.Price.list(
            lookup_keys=lookup_keys,
            expand=['data.product']
        )

        checkout_session = stripe.checkout.Session.create(
            client_reference_id=request.user.id,
            line_items=[
                {
                    'price': prices.data[0].id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=YOUR_DOMAIN + '/success/{CHECKOUT_SESSION_ID}/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return redirect(checkout_session.url, code=303)


class CancelSubscriptionView(View):

    def post(self, request, *args, **kwargs):
        stripe.Subscription.delete(request.POST['subscription_id'])
        return redirect('add-subscription')