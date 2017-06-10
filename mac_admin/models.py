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

from django.db import models
import django.utils

class Computer(models.Model):
    ''' Store a computer name and a JSS computer id in database. '''
    computer_name = models.CharField(max_length=7, blank=False, unique=True)
    computer_id = models.CharField(max_length=4, blank=False, unique=True)

    def __str__(self):
        return self.computer_name


class ComputerGroup(models.Model):
    ''' Store a group name and a JSS group id in database. Store computer to group memberships. '''
    group_name = models.CharField(max_length=200, blank=False, unique=True)
    group_id = models.CharField(max_length=4, blank=False, unique=True)
    group_members = models.ManyToManyField(Computer, through='ComputerGroupMembership')

    def __str__(self):
        return self.group_name


class ComputerGroupMembership(models.Model):
    ''' Computer to group relationship. '''
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE)
    computer_group = models.ForeignKey(ComputerGroup, on_delete=models.CASCADE)
    date_assigned = models.DateField(default=django.utils.timezone.now)
    # Distinguish between initial jss import and mac_admin c2sg assigned relationships
    assigned_by = models.CharField(max_length=64, default='jss import')

    def __str__(self):
        return self.computer.computer_name
