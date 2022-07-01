from django.test import TestCase
from authentication.models import *
from choice_model.choicemodel import *
from choice_model.models import *


class ChoiceModelTestCase(TestCase):
    def setUp(self):
        # create fake user for linking the choice model to
        self.dummy_user = CustomUser.objects.create_user('dummy_user@email.com', 'dummy_password')

        # create fake bundle/model for testing purposes
        self.dummy_bundle = ModifiedSitesBundle.objects.create(user=self.dummy_user, nickname='dummy_bundle')

        # add fake modified site to the new bundle
        self.dummy_modified_site = ModifiedSite.objects.create(
            bundle=self.dummy_bundle,
            latitude=35,
            longitude=78,
            name="dummy_site",
            acres=100,
            trails=3,
            trail_miles=10,
            picnic_area=1,
            sports_facilities=0,
            swimming_facilities=0,
            boat_launch=0,
            waterbody=0,
            bathrooms=1,
            playgrounds=0,
        )

    def test_baseline(self):
        baseline = ChoiceModel(self.dummy_user, bundle=None)

    def test_counterfactual(self):
        counterfactual = ChoiceModel(self.dummy_user, self.dummy_bundle)
        # print(choice_model.get_site_visits())
