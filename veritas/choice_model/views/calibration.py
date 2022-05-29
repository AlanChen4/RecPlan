from django.shortcuts import redirect, render

from choice_model.models import BaselineModel, BaselineSite
from choice_model.choicemodel import ChoiceModel


def RecalibrateBaseline(request):
    if request.method == 'GET':
        cm = ChoiceModel()
        baseline_site_visits = cm.get_site_visits(modified_sites=[])

        return render(request, 'choice_model/calibration.html', {'baseline_site_visits': baseline_site_visits})
    elif request.method == 'POST':
        # set other baseline calibration model 'selected' as False, so that current one is selected
        baseline_models = BaselineModel.objects.all()
        for model in baseline_models:
            model.selected = False
            model.save()

        # create baseline calibration model
        baseline_model = BaselineModel.objects.create(
            user=request.user,
            name=request.POST['baselineModelName'],
            selected=True,
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
