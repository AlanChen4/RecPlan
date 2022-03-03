from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView, UpdateView
from django.shortcuts import redirect


class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    fields = '__all__'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('bundles')
        return super().get(*args, **kwargs)


class RegisterPage(FormView):
    template_name = 'authentication/register.html'
    form_class = UserCreationForm

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)    

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('bundles')
        return super().get(*args, **kwargs)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['email', 'username', 'first_name', 'last_name']
    template_name = 'authentication/profile.html'

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            return redirect('bundles')
        return super().form_valid(form)

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)
