from ast import Mod
from tkinter import W
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from itertools import chain

from .models import ModifiedSitesBundle, Site, ModifiedSite


class BundleList(LoginRequiredMixin, ListView):
    model = ModifiedSitesBundle
    context_object_name = 'bundles'
    template_name = 'bundles.html'

    def get_queryset(self):
        return super().get_queryset().filter(history_id=self.request.user)


class BundleDetail(LoginRequiredMixin, DetailView):
    model = ModifiedSitesBundle
    context_object_name = 'bundle'
    template_name = 'bundle.html'

    def get_queryset(self):
        return super().get_queryset().filter(history_id=self.request.user)


class BundleCreate(LoginRequiredMixin, CreateView):
    model = ModifiedSitesBundle
    fields = ['nickname']
    success_url = reverse_lazy('bundles')
    template_name = 'bundle_create.html'

    def form_valid(self, form):
        form.instance.history_id = self.request.user
        return super().form_valid(form)


class BundleUpdate(LoginRequiredMixin, UpdateView):
    model = ModifiedSitesBundle
    fields = ['nickname']
    success_url = reverse_lazy('bundles')
    context_object_name = 'bundle'
    template_name = 'bundle_modify.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bundle_id = self.request.path.split('/')[-2]
        if self.request.GET.get('modified-only') == 'on':
            context['modified'] = True
            context['sites'] = ModifiedSite.objects.all().filter(bundle_id=bundle_id).order_by('name')
        else:
            context['modified'] = False
            context['sites'] = Site.objects.all().order_by('name')
        return context

    def get_queryset(self):
        return super().get_queryset().filter(history_id=self.request.user)


class BundleDelete(LoginRequiredMixin, DeleteView):
    model = ModifiedSitesBundle
    context_object_name = 'bundle'
    success_url = reverse_lazy('bundles')
    template_name = 'bundle_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(history_id=self.request.user)


class ModifiedSiteCreate(LoginRequiredMixin, CreateView):
    model = ModifiedSite
    fields = ['name', 'acres', 'trails', 'trail_miles', 'picnic_area', 'sports_facilities', 
              'swimming_facilities', 'boat_launch', 'waterbody', 'bathrooms', 'playgrounds']
    success_url = reverse_lazy('bundles')
    template_name = 'modified_site_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # calculate bundle_id from url and add to context
        bundle_id = self.request.path.split('/')[2]
        context['bundle_id'] = bundle_id

        return context

    def get_initial(self):
        initial =  super().get_initial()

        # check if there is existing modified site
        bundle_id = self.request.path.split('/')[2]
        site_name = self.request.path.split('/')[3]
        if ModifiedSite.objects.all().filter(bundle_id=bundle_id).filter(name=site_name).exists():
            site = ModifiedSite.objects.all().filter(bundle_id=bundle_id).get(name=site_name)
        else:
            # get original data belonging to site
            site = Site.objects.get(name=site_name)

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

    def form_valid(self, form):
        bundle_id = self.request.path.split('/')[2]

        form.instance.history_id = self.request.user
        form.instance.bundle_id = ModifiedSitesBundle.objects.get(bundle_id=bundle_id)

        return super().form_valid(form)