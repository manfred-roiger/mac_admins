from django.db import models
import django.utils

class Computer(models.Model):
    computer_name = models.CharField(max_length=7, blank=False, unique=True)
    computer_id = models.IntegerField(blank=False, unique=True)

    def __str__(self):
        return self.computer_name


class ComputerGroup(models.Model):
    group_name = models.CharField(max_length=200, blank=False, unique=True)
    group_id = models.CharField(max_length=4, blank=False, unique=True)
    group_members = models.ManyToManyField(Computer, through='ComputerGroupMembership')

    def __str__(self):
        return self.group_name


class ComputerGroupMembership(models.Model):
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE)
    computer_group = models.ForeignKey(ComputerGroup, on_delete=models.CASCADE)
    date_assigned = models.DateField(default=django.utils.timezone.now)
    assigned_by = models.CharField(max_length=64, default='jss import')

    def __str__(self):
        return '%s in %s by %s' % (self.computer.computer_name, self.computer_group.group_name, self.assigned_by)
