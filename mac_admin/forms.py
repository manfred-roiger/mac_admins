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

from django import forms
from .models import ComputerGroup, Computer, ComputerGroupMembership
from django.core.exceptions import ObjectDoesNotExist
from .jss2 import Jss
from django.db.utils import IntegrityError


class SelectComputer(forms.Form):
    computer = forms.CharField(max_length=7, required=True)
    software = forms.CharField(max_length=200, required=True)

    def clean(self):
        cleaned_data = super(SelectComputer, self).clean()
        computer = cleaned_data.get('computer')
        software = cleaned_data.get('software')

        try:
            my_computer = Computer.objects.get(computer_name=computer)
        except ObjectDoesNotExist:
            jss = Jss()
            jss_computer = jss.get_computer(computer)
            jss.end_session()
            # If computer is not in database and not in JSS the name is probably misspelled
            if jss_computer == None:
                raise forms.ValidationError('%s : a computer with this name does not exist!' % computer)
            # Comuter exists but is new in JSS, add it to the database
            else:
                try:
                    Computer(computer_name=jss_computer['computer']['general']['name'], computer_id=str(jss_computer['computer']['general']['id'])).save()
                except IntegrityError:
                    raise forms.ValidationError('Fatal error: %s not found in db and could not be added!')
                # Add group memberships if any available
                for value in jss_computer['computer']['groups_accounts']['computer_group_memberships']:
                    try:
                        group = ComputerGroup.objects.get(group_name=value)
                        try:
                            ComputerGroupMembership(computer=line, computer_group=group, date_assigned=timezone.now(),
                                                    assigned_by='jss import').save()
                        except IntegrityError:
                            pass
                    except ObjectDoesNotExist:
                        pass

        if not ComputerGroup.objects.filter(group_name__contains=software):
            raise forms.ValidationError('No software matching this pattern found!')


class SelectMac2Mac(forms.Form):
    source = forms.CharField(max_length=7, required=True)
    target = forms.CharField(max_length=7, required=True)

    def clean(self):
        cleaned_data = super(SelectMac2Mac, self).clean()
        source = cleaned_data.get('source')
        target = cleaned_data.get('target')
        to_fetch = []

        # Search for source in database
        try:
            source_computer = Computer.objects.get(computer_name=source)
        except ObjectDoesNotExist:
            to_fetch.append(source)

        # Search for target in database
        try:
            target_computer = Computer.objects.get(computer_name=source)
        except ObjectDoesNotExist:
            to_fetch.append(target)

        # If source and or target don't exist in database try to fetch them from JSS
        if to_fetch != []:
            jss = Jss()
            for get_computer in to_fetch:
                jss_computer = jss.get_computer(get_computer)
                if jss_computer == None:
                    raise forms.ValidationError('%s : a computer with this name does not exist!' % computer)
                else:
                    try:
                        Computer(computer_name=jss_computer['computer']['general']['name'],
                                 computer_id=str(jss_computer['computer']['general']['id'])).save()
                    except IntegrityError:
                        raise forms.ValidationError('Fatal error: %s not found in db and could not be added!')
                    # Add group memberships if any available
                    for value in jss_computer['computer']['groups_accounts']['computer_group_memberships']:
                        try:
                            group = ComputerGroup.objects.get(group_name=value)
                            try:
                                ComputerGroupMembership(computer=line, computer_group=group,
                                                        date_assigned=timezone.now(),
                                                        assigned_by='jss import').save()
                            except IntegrityError:
                                pass
                        except ObjectDoesNotExist:
                            pass
            jss.end_session()


class SelectSoftware(forms.Form):
    software_choices = [(sw.group_id, sw.group_name) for sw in ComputerGroup.objects.all()]
    select_software = forms.MultipleChoiceField(choices=software_choices, widget=forms.CheckboxSelectMultiple(),
                                                required=True)
