from django.shortcuts import redirect, render

from choice_model.models import BaselineModel, BaselineSite
from choice_model.choicemodel import ChoiceModel
from choice_model.constants import BASELINE_VISITS


def RecalibrateBaseline(request):
    if request.method == 'GET':
        return render(request, 'choice_model/calibration.html', {'baseline_site_visits': BASELINE_VISITS.to_dict()['visits']})

    elif request.method == 'POST':
        # create baseline calibration model
        baseline_model = BaselineModel.objects.create(
            user=request.user,
            name=request.POST['baselineModelName'],
        )

        # add site data to the baseline model
        for key, value in request.POST.items():
            if '(site)' in key:
                site_name = key.replace(' (site)', '')
                site_visits = value
                BaselineSite.objects.create(
                    baseline_model=baseline_model,
                    name=site_name,
                    visits=site_visits,
                )

        return redirect('bundles')

    
def EditBaseline(request, **kwargs):
    if request.method == 'GET':
        baseline = BaselineModel.objects.get(user=request.user, id=kwargs['baseline_id'])
        baseline_sites = BaselineSite.objects.filter(baseline_model=baseline)

        return render(request, 'choice_model/edit_baseline.html', {'baseline': baseline, 'baseline_sites': baseline_sites})

    elif request.method == 'POST':
        # fetch baseline model and also update name
        baseline_model = BaselineModel.objects.get(user=request.user, id=kwargs['baseline_id'])
        baseline_model.name = request.POST['baselineModelName']
        baseline_model.save()

        # update site data for baseline model
        for key, value in request.POST.items():
            if '(site)' in key:
                site_name = key.replace(' (site)', '')
                site_visits = value
                baseline_site = BaselineSite.objects.get(baseline_model=baseline_model, name=site_name)
                baseline_site.visits = site_visits
                baseline_site.save()

        return redirect('bundles')


def DeleteBaseline(request, **kwargs):
    # even though delete should not be done with GET, I'm doing so here to simplify logic on the frontend
    if request.method == 'GET':
        baseline = BaselineModel.objects.get(user=request.user, id=kwargs['baseline_id'])
        baseline.delete()

        return redirect('bundles')
