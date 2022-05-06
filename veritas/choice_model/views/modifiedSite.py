from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from choice_model.dashapps import site_choice_prob, site_selection, add_site
from choice_model.models import ModifiedSitesBundle, Site, ModifiedSite
from choice_model.utils import ChoiceModel, create_SCP_bubble_plot_fig, create_SCP_map_scatter_plot_fig, create_add_site_plot_fig


class ModifiedSiteCreate(LoginRequiredMixin, CreateView):
    model = ModifiedSite
    fields = ['name', 'latitude', 'longitude', 'acres', 'trails', 'trail_miles', 'picnic_area', 'sports_facilities', 'swimming_facilities', 'boat_launch', 'waterbody', 'bathrooms', 'playgrounds']
    template_name = 'modified_site_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bundle_id = self.request.path.split('/')[2]
        site_name = self.request.path.split('/')[3]

        # calculate bundle_id from url and add to context
        context['bundle_id'] = bundle_id

        # add plotly-dash figure & initial data
        add_site_plot = create_add_site_plot_fig()
        context['dash_context'] = {
            'add-site-plot': {'figure': add_site_plot},
            'slug': {'children': bundle_id},
        }

        # if site_name != 'new-site':
        #     site = ModifiedSite.objects.get(bundle_id=bundle_id, name=site_name)
        #     context['dash_context']['site_name'] = {'value': site.name}
        #     context['dash_context']['acres'] = {'value': site.acres}
        #     context['dash_context']['trails'] = {'value': site.trails}
        #     context['dash_context']['trail_miles'] = {'value': site.trail_miles}
        #     context['dash_context']['bathrooms'] = {'value': site.bathrooms}
        #     context['dash_context']['picnic_area'] = {'value': site.picnic_area}
        #     context['dash_context']['sports_facilities'] = {'value': site.sports_facilities}
        #     context['dash_context']['swimming_facilities'] = {'value': site.swimming_facilities}
        #     context['dash_context']['boat_launch'] = {'value': site.boat_launch}
        #     context['dash_context']['waterbody'] = {'value': site.waterbody}
        #     context['dash_context']['playgrounds'] = {'value': site.playgrounds}

        return context

    def get_initial(self):
        initial =  super().get_initial()

        # check if there is existing modified site
        bundle_id = self.request.path.split('/')[2]
        site_name = self.request.path.split('/')[3]
        if ModifiedSite.objects.all().filter(bundle_id=bundle_id).filter(name=site_name).exists():
            site = ModifiedSite.objects.all().filter(bundle_id=bundle_id).get(name=site_name)
        elif site_name == 'new-site':
            return initial
        else:
            # get original data belonging to site
            site = Site.objects.get(name=site_name)

        initial = {
            'name': site.name,
            'latitude': site.latitude,
            'longitude': site.longitude,
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
        bundle_id = self.request.path.split('/')[2]
        return reverse_lazy('bundle-update', kwargs={'pk': bundle_id})

    def form_valid(self, form):
        bundle_id = self.request.path.split('/')[2]

        form.instance.history_id = self.request.user
        form.instance.bundle_id = ModifiedSitesBundle.objects.get(bundle_id=bundle_id)

        if ModifiedSite.objects.filter(bundle_id=bundle_id).filter(name=form.instance.name).exists():
            ModifiedSite.objects.filter(bundle_id=bundle_id).filter(name=form.instance.name).delete()

        return super().form_valid(form)