from django import forms
from .models import ComputerGroup, Computer
from django.core.exceptions import ObjectDoesNotExist


class SelectComputer(forms.Form):
    computer = forms.CharField(max_length=7, required=True)
    software = forms.CharField(max_length=200, required=True)

    def clean(self):
        cleaned_data = super(SelectComputer, self).clean()
        computer = cleaned_data.get('computer')
        software = cleaned_data.get('software')

        try:
            Computer.objects.get(computer_name=computer)
        except ObjectDoesNotExist:
            raise forms.ValidationError('A computer with this name does not exist!')

        if not ComputerGroup.objects.filter(group_name__contains=software):
            raise forms.ValidationError('No software matching this pattern found!')


class SelectSoftware(forms.Form):
    software_choices = [(sw.group_id, sw.group_name) for sw in ComputerGroup.objects.all()]
    select_software = forms.MultipleChoiceField(choices=software_choices, widget=forms.CheckboxSelectMultiple())