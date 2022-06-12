import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy

from choice_model.choicemodel import ChoiceModel
from choice_model.dashapps import add_site, site_choice_prob, site_selection
from choice_model.dashapp_helpers import *
from choice_model.models import *

from pathlib import Path


@login_required
def SiteCreate(request, **kwargs):
    if request.method == 'GET':
        # calculate sum of equity for each block
        choice_model = ChoiceModel(user=request.user)
        bg_utility_black = choice_model.get_utility_by_block_group()[0].sum().to_frame()

        # convert to format that can be read by choropleth mapbox
        bg_utility_black['GEOID'] = bg_utility_black.index.str.replace(', ', '').str[:6]
        bg_utility_black = bg_utility_black.rename(columns={0: 'black_utility'})
        
        bundle_id = str(kwargs['pk'])
        context = {
            'bundle_id': bundle_id,
            'dash_context': {
                'add-site-plot': {'figure': create_add_site_plot_fig(bg_utility_black)},
                'bundle_id': {'value': bundle_id},
                'csrfmiddlewaretoken': {'value': get_token(request)}
            }
        }

        return render(request, 'choice_model/site_create.html', context)
    
    elif request.method == 'POST':
        form_data = request.POST
        bundle_id = str(kwargs['pk'])

        # get the appropriate lat & lon for the respective GEOID
        geoid = form_data['geo_id']
        wake_bg_path = Path() / 'choice_model/data/wake_bg.json'
        with open(wake_bg_path) as f:
            wake_bg = json.load(f)
        for feature in wake_bg['features']:
            if geoid == feature['properties']['GEOID']:
                lat = float(feature['properties']['INTPTLAT'])
                lon = float(feature['properties']['INTPTLON'])
                break

        ModifiedSite.objects.create(
            bundle=ModifiedSitesBundle.objects.get(id=bundle_id),
            latitude=lat,
            longitude=lon,
            name=form_data['site_name'],
            acres=float(form_data['acres']),
            trails=int(form_data['trails']),
            trail_miles=float(form_data['trail_miles']),
            picnic_area=(1 if form_data.get('picnic_area') else 0),
            sports_facilities=(1 if form_data.get('picnic_area') else 0),
            swimming_facilities=(1 if form_data.get('swimming_facilities') else 0),
            boat_launch=(1 if form_data.get('boat_launch') else 0),
            waterbody=(1 if form_data.get('waterbody') else 0),
            bathrooms=(1 if form_data.get('bathrooms') else 0),
            playgrounds=(1 if form_data.get('playgrounds') else 0),
        )

        return redirect(reverse('bundle-update', kwargs={'pk': bundle_id}))


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

        form.instance.bundle = ModifiedSitesBundle.objects.get(id=bundle_id)
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

        return ModifiedSite.objects.get(id=bundle_id, name=site_name)

    def get_success_url(self):
        bundle_id = str(self.kwargs['pk'])

        return reverse_lazy('bundle-update', kwargs={'pk': bundle_id})


class ModifiedSiteDelete(LoginRequiredMixin, DeleteView):
    model = ModifiedSite
    template_name = 'choice_model/modified_site_delete.html'

    def get_success_url(self):
        return reverse_lazy('bundle-update', kwargs={'pk': self.object.bundle.id})
