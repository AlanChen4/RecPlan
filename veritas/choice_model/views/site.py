import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy

from choice_model.dashapps import site_choice_prob, site_selection, add_site
from choice_model.models import ModifiedSitesBundle, Site, ModifiedSite
from choice_model.utils import ChoiceModel, create_SCP_bubble_plot_fig, create_SCP_map_scatter_plot_fig, create_add_site_plot_fig

from dash import dcc
from pathlib import Path


class SiteCreate(LoginRequiredMixin, CreateView):
    model = ModifiedSite
    fields = ['name', 'acres', 'trails', 'trail_miles', 'picnic_area', 'sports_facilities', 'swimming_facilities', 'boat_launch', 'waterbody', 'bathrooms', 'playgrounds']
    template_name = 'choice_model/site_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bundle_id = str(self.kwargs['pk'])
        add_site_plot = create_add_site_plot_fig()

        context['bundle_id'] = bundle_id
        context['dash_context'] = {
            'add-site-plot': {'figure': add_site_plot},
            'bundle_id': {'value': bundle_id},
            'csrfmiddlewaretoken': {'value': get_token(self.request)}
        }

        return context

def SiteCreateDash(request, **kwargs):
    if request.method == 'POST':
        form_data = request.POST

        # get the appropriate lat & lon for the respective GEOID
        geoid = form_data['geoid']
        wake_bg_path = Path() / 'choice_model/data/wake_bg.json'
        with open(wake_bg_path) as f:
            wake_bg = json.load(f)
        for feature in wake_bg['features']:
            if geoid == feature['properties']['GEOID']:
                lat = float(feature['properties']['INTPTLAT'])
                lon = float(feature['properties']['INTPTLON'])
                break

        ModifiedSite.objects.create(
            bundle_id=ModifiedSitesBundle.objects.get(bundle_id=form_data['bundle_id']),
            latitude=lat,
            longitude=lon,
            name=form_data['site_name'],
            acres=float(form_data['acres']),
            trails=int(form_data['trails']),
            trail_miles=float(form_data['trail_miles']),
            picnic_area=int(form_data['picnic_area']),
            sports_facilities=int(form_data['sports_facilities']),
            swimming_facilities=int(form_data['swimming_facilities']),
            boat_launch=int(form_data['boat_launch']),
            waterbody=int(form_data['waterbody']),
            bathrooms=int(form_data['bathrooms']),
            playgrounds=int(form_data['playgrounds']),
        )
        return redirect(reverse('bundle-update', kwargs={'pk': form_data['bundle_id']}))


class ModifiedSiteCreate(LoginRequiredMixin, CreateView):
    model = ModifiedSite
    fields = ['name', 'acres', 'trails', 'trail_miles', 'picnic_area', 'sports_facilities', 'swimming_facilities', 'boat_launch', 'waterbody', 'bathrooms', 'playgrounds']
    template_name = 'choice_model/modified_site_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['site_name'] = self.kwargs['site_name']

        return context

    def get_initial(self):
        initial =  super().get_initial()
        site = Site.objects.get(name=self.kwargs['site_name'])

        initial = {
            'name': site.name,
            'acres': site.acres,
            'trails': site.trails,
            'trail_miles': site.trail_miles,
            'picnic_area': site.picnic_area,
            'playgrounds': site.playgrounds,
            'sports_facilities': site.sports_facilities,
            'swimming_facilities': site.swimming_facilities,
            'boat_launch': site.boat_launch,
            'waterbody': site.waterbody,
            'bathrooms': site.bathrooms
        }

        return initial

    def get_success_url(self):
        bundle_id = str(self.kwargs['pk'])

        return reverse_lazy('bundle-update', kwargs={'pk': bundle_id})

    def form_valid(self, form):
        bundle_id = str(self.kwargs['pk'])
        site = Site.objects.get(name=self.kwargs['site_name'])

        form.instance.history_id = self.request.user
        form.instance.bundle_id = ModifiedSitesBundle.objects.get(bundle_id=bundle_id)
        form.instance.latitude = site.latitude
        form.instance.longitude = site.longitude

        return super().form_valid(form)


class ModifiedSiteUpdate(LoginRequiredMixin, UpdateView):
    model = ModifiedSite
    fields = ['name', 'acres', 'trails', 'trail_miles', 'picnic_area', 'sports_facilities', 'swimming_facilities', 'boat_launch', 'waterbody', 'bathrooms', 'playgrounds']
    template_name = 'choice_model/modified_site_create.html'

    def get_object(self, **kwargs):
        bundle_id = str(self.kwargs['pk'])
        site_name = str(self.kwargs['site_name'])

        return ModifiedSite.objects.get(bundle_id=bundle_id, name=site_name)

    def get_success_url(self):
        bundle_id = str(self.kwargs['pk'])

        return reverse_lazy('bundle-update', kwargs={'pk': bundle_id})
