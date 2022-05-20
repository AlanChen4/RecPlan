from django.shortcuts import render

from choice_model.utils import ChoiceModel


def RecalibrateBaseline(request):
    if request.method == 'GET':
        cm = ChoiceModel()
        baseline_site_visits = cm.get_site_visits(modified_sites=[])

        context = {
            'baseline_site_visits': baseline_site_visits
        }

        return render(request, template_name='choice_model/calibration.html', context=context)

    elif request.method == 'POST':
        print(request.POST)
