import plotly.express as px

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from itertools import chain

from choice_model.choicemodel import ChoiceModel 
from choice_model.dashapps import add_site, site_choice_prob, site_selection
from choice_model.dashapp_helpers import *
from choice_model.models import *


class BundleList(LoginRequiredMixin, ListView):
    model = ModifiedSitesBundle
    context_object_name = 'bundles'
    template_name = 'choice_model/bundles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        choice_model = ChoiceModel(self.request.user)
        baseline_site_visits = choice_model.get_site_visits()
        baseline_visitation_prob = choice_model.get_site_visitation_probability()

        bubble_fig = create_SCP_bubble_plot_fig(baseline_site_visits)
        map_scatter_fig = create_SCP_map_scatter_plot_fig(baseline_visitation_prob, choice_model.get_site_locations())

        context['dash_context'] = {
            'bubble-plot': {'figure': bubble_fig},
            'map-scatter-plot': {'figure': map_scatter_fig}
        }

        return context

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class BundleDetail(LoginRequiredMixin, DetailView):
    model = ModifiedSitesBundle
    context_object_name = 'bundle'
    template_name = 'choice_model/bundle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        choice_model = ChoiceModel(user=self.request.user, bundle=self.object)
        site_visits = choice_model.get_site_visits()
        visitation_prob = choice_model.get_site_visitation_probability()
        choice_model.get_equity_evaluation()
        baseline_equity_evaluation  = choice_model.get_equity_evaluation()
        equity_evaluation = choice_model.get_equity_evaluation()

        bubble_fig = create_SCP_bubble_plot_fig(site_visits)
        map_scatter_fig = create_SCP_map_scatter_plot_fig(visitation_prob, choice_model.get_site_locations())

        context['dash_context'] = {
            'bubble-plot': {'figure': bubble_fig},
            'map-scatter-plot': {'figure': map_scatter_fig}
        }

        context['baseline_equity_black'] = round(baseline_equity_evaluation['average_utility_black'], 3)
        context['baseline_equity_other'] = round(baseline_equity_evaluation['average_utility_other'], 3)
        context['counterfactual_equity_black'] = round(equity_evaluation['average_utility_black'], 3)
        context['counterfactual_equity_other'] = round(equity_evaluation['average_utility_other'], 3)

        return context

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class BundleCreate(LoginRequiredMixin, CreateView):
    model = ModifiedSitesBundle
    fields = ['nickname']
    success_url = reverse_lazy('bundles')
    template_name = 'choice_model/bundle_create.html'

    def form_valid(self, form):
        form.instance.history_id = self.request.user
        return super().form_valid(form)


class BundleUpdate(LoginRequiredMixin, UpdateView):
    model = ModifiedSitesBundle
    fields = ['nickname']
    success_url = reverse_lazy('bundles')
    context_object_name = 'bundle'
    template_name = 'choice_model/bundle_modify.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bundle_id = self.object.id
        context['bundle_id'] = bundle_id

        # check filter for modified-only
        if self.request.GET.get('modified-only') == 'on':
            context['modified'] = True
            context['sites'] = ModifiedSite.objects.all().filter(bundle=bundle_id).order_by('name')
        else:
            context['modified'] = False

            # prevent original site from showing up if already in modified sites
            modified_sites = ModifiedSite.objects.all().filter(bundle=bundle_id)
            modified_sites_names = [site.name for site in modified_sites]
            original_sites = Site.objects.all().exclude(name__in=modified_sites_names)
            context['sites'] = sorted(list(chain(original_sites, modified_sites)), key=lambda site: site.name)

        # check if site is being selected to show on map/characteristics
        if self.request.GET.get('show-site') is not None:
            # get site characteristics based on name
            selected_site_name = self.request.GET.get('show-site')
            
            if ModifiedSite.objects.all().filter(bundle=bundle_id, name=selected_site_name).exists():
                selected_site = ModifiedSite.objects.all().get(bundle=bundle_id, name=selected_site_name)
            else:
                selected_site = Site.objects.all().get(name=selected_site_name)

            # pass selected site into context
            context['selected_site'] = selected_site
            map_scatter_fig = px.scatter_mapbox(
                {'name': {0: selected_site.name}, 'latitude': {0: selected_site.latitude}, 'longitude': {0: selected_site.longitude}, 'empty': {0: 0}},
                lat='latitude', 
                lon='longitude', 
                zoom=14,
                hover_name='name',
                mapbox_style='open-street-map'
            )
            map_scatter_fig.update_layout(margin={'l':0, 'r': 0, 't':0, 'b':0})
        else:
            map_scatter_fig = px.scatter_mapbox(center={'lat': 100, 'lon': 100})
            context['selected_site'] = None

        # include name of sites that have already been modified
        context['modified_site_names'] = ModifiedSite.objects.filter(bundle=self.object).values_list('name', flat=True)
        context['dash_context'] = {'map-plot': {'figure': map_scatter_fig}}

        return context

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class BundleDelete(LoginRequiredMixin, DeleteView):
    model = ModifiedSitesBundle
    context_object_name = 'bundle'
    success_url = reverse_lazy('bundles')
    template_name = 'choice_model/bundle_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
