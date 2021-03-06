# Copyright (c) 2017 Manfred Roiger <manfred.roiger@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.shortcuts import render, get_object_or_404, redirect
from .forms import SelectComputer, SelectSoftware, SelectMac2Mac
from .models import ComputerGroup, ComputerGroupMembership, Computer
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from .jss2 import Jss


def index(request):
    ''' Show index page with links and short module descriptions. '''
    return render(request, 'mac_admin/index.html')


def under_construction(request):
    ''' Show under construction page for mudules that are noch yet finished. '''
    return render(request, 'mac_admin/under_construction.html')


def c2sg(request):
    ''' Ask user to enter a computer name and a search pattern for software. The cleaned_data method of the form
    checks if a computer name exists and if a software matching the pattern is found. '''
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
    ''' Display a check-list of software that matches the search pattern from c2sg method. Store the choices in a
    session list because it is needed for confirmation and assignemnet later. '''
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
    ''' Display the list of seletced software and ask for confirmation. '''
    software_list = []
    for gid in request.session['picked']:
        software_list.append(ComputerGroup.objects.get(group_id = gid))
    if request.method == 'POST':
        return redirect('mac_admin:assign_c2sg')

    return render(request, 'mac_admin/confirm.html', {'sw_list': software_list})


def assign_c2sg(request):
    ''' Store new computer to static group relations in database and call method to assign computer to static group
    in JSS. '''
    result_list = []
    id_list = []
    jss = Jss()

    if request.method == 'POST':
        return redirect('mac_admin:index', permanent=True)

    for gid in request.session['picked']:
        computer = Computer.objects.get(computer_name__iexact=request.session['computer'])
        group = ComputerGroup.objects.get(group_id=gid)

        # Check if computer to group assignment does already exist
        try:
            computer.computergroup_set.get(group_id=group.group_id)
            result_list.append('Info: %s is already assigned to %s .. was skipped!' % (computer, group))
            # Computer is already in this group, continue with next group
            # Denk mal drüber nach was passiert, wenn der computer im JSS gelöscht und neu angelegt wird.
            continue
        except ObjectDoesNotExist:
            # Nothing to do here, we can insert the id to our update liste for the jss interface
            id_list.append(gid)

        # Create new relationship in database
        ComputerGroupMembership(computer=computer, computer_group=group, date_assigned=timezone.now(),
                                assigned_by='mac_admin c2sg').save()

    # Add computer to static group in jss
    result = jss.update_groups(computer.computer_name, id_list)
    if result != []:
        for line in result:
            result_list.append(line)

    return render(request, 'mac_admin/result.html', {'result_list': result_list, 'computer': computer})



def search_mac2mac(request):
    ''' Search for source computer and target computer. All group assignments of source computer can be copied to
    target computer. '''
    if request.method == 'POST':
        form = SelectMac2Mac(request.POST)
        if form.is_valid():
            request.session['source'] = form.cleaned_data['source']
            request.session['computer'] = form.cleaned_data['target']
            return redirect('mac_admin:select_mac2mac')
    else:
        form = SelectMac2Mac

    return render(request, 'mac_admin/mac2mac.html', {'form': form})



def select_mac2mac(request):
    ''' Show all group assigments of source computer and allow user to select groups for target computer. '''
    try:
        source = Computer.objects.get(computer_name__iexact=request.session['source'])
    except ObjectDoesNotExist:
        raise ValidationError('Fatal error: %s does not exist!')
    try:
        computer = Computer.objects.get(computer_name__iexact=request.session['computer'])
    except ObjectDoesNotExist:
        raise ValidationError('Fatal error: %s does not exist!')
    software_choices = [(sw.group_id, sw.group_name) for sw in source.computergroup_set.all()]
    if request.method == 'POST':
        form = SelectSoftware(request.POST)
        form.fields['select_software'].choices = software_choices
        if form.is_valid():
            request.session['picked'] = form.cleaned_data.get('select_software')
            return redirect('mac_admin:confirm')
    else:
        form = SelectSoftware()
        form.fields['select_software'].choices = software_choices

    return render(request, 'mac_admin/selmac2mac.html', {'form': form, 'source': source.computer_name,
                                                      'dest': computer.computer_name})
