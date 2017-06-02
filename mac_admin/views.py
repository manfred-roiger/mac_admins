from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import SelectComputer, SelectSoftware, ConfirmSoftware
from .models import ComputerGroup, ComputerGroupMembership, Computer
from django.urls import reverse
from django import forms
from django.db.utils import IntegrityError


def index(request):
    return render(request, 'mac_admin/index.html')


def under_construction(request):
    return render(request, 'mac_admin/under_construction.html')


def c2sg(request):
    if request.method == 'POST':
        form = SelectComputer(request.POST)
        if form.is_valid():
            request.session['computer'] = form.cleaned_data['computer']
            request.session['software'] = form.cleaned_data['software']
            return redirect('mac_admin:select')
    else:
        form = SelectComputer
    return render(request, 'mac_admin/c2sg.html', {'form': form})


def select(request):
    software = request.session['software']
    software_choices = [(sw.group_id, sw.group_name) for sw in ComputerGroup.objects.filter(group_name__contains=software)]
    if request.method == 'POST':
        form = SelectSoftware(request.POST)
        form.fields['select_software'].choices = software_choices
        if form.is_valid():
            request.session['picked'] = form.cleaned_data.get('select_software')
            return redirect('mac_admin:confirm')
    else:
        form = SelectSoftware()
        form.fields['select_software'].choices = software_choices
    return render(request, 'mac_admin/select.html', {'form': form})


def confirm(request):
    software_list = []
    for gid in request.session['picked']:
        software_list.append(ComputerGroup.objects.get(group_id = gid))
    if request.method == 'POST':
        return redirect('mac_admin:assign_c2sg')

    return render(request, 'mac_admin/confirm.html', {'sw_list': software_list})


def assign_c2sg(request):
    result_list = []

    if request.method == 'POST':
        return redirect('mac_admin:index')

    for gid in request.session['picked']:
        computer = Computer.objects.get(computer_name = request.session['computer'])
        group = ComputerGroup.objects.get(group_id = gid)
        try:
            ComputerGroupMembership(computer=computer, computer_group=group).save()
            result_list.append('Success: %s assigned to %s' % (computer,group))
        except IntegrityError:
            result_list.append('Failed: %s is already assigned to %s .. was skipped!' % (computer, group))

    return render(request, 'mac_admin/result.html', {'result_list': result_list}, {'computer': computer})
