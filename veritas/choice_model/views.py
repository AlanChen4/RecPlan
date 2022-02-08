from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import ModifiedSitesBundle


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

    def get_queryset(self):
        return super().get_queryset().filter(history_id=self.request.user)


class BundleDelete(LoginRequiredMixin, DeleteView):
    model = ModifiedSitesBundle
    context_object_name = 'bundle'
    success_url = reverse_lazy('bundles')
    template_name = 'bundle_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(history_id=self.request.user)
