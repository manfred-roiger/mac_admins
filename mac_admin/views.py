from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import SelectComputer, SelectSoftware
from .models import ComputerGroup, ComputerGroupMembership, Computer
from django.urls import reverse
from django import forms

software = ''
computer = ''


def index(request):
    return render(request, 'mac_admin/index.html')


def base(request):
    return render(request, 'mac_admin/base.html', context=None)


def c2sg(request):
    global software
    global computer
    if request.method == 'POST':
        form = SelectComputer(request.POST)
        if form.is_valid():
            computer = form.cleaned_data['computer']
            software = form.cleaned_data['software']
            return redirect('mac_admin:select')

    else:
        form = SelectComputer
    return render(request, 'mac_admin/c2sg.html', {'form': form})


def select(request):
    global software
    if request.method == 'POST':
        form = SelectSoftware(request.POST)
        if form.is_valid():
            picked = form.cleaned_data.get('select_software')
            print(picked)
            return HttpResponseRedirect('.')
    else:
        software_choices = [(sw.group_id, sw.group_name) for sw in ComputerGroup.objects.filter(
            group_name__contains=software)]
        form = SelectSoftware()
        form.fields['select_software'].choices = software_choices
        print(form.fields['select_software'].choices)
    return render(request, 'mac_admin/select.html', {'form': form})
