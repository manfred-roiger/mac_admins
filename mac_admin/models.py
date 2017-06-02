from django.db import models

class Computer(models.Model):
    computer_name = models.CharField(max_length=7, blank=False, unique=True)
    computer_id = models.IntegerField(blank=False, unique=True)

    def __str__(self):
        return self.computer_name


class ComputerGroup(models.Model):
    group_name = models.CharField(max_length=200, blank=False, unique=True)
    group_id = models.CharField(max_length=4, blank=False, unique=True)

    def __str__(self):
        return self.group_name


class ComputerGroupMembership(models.Model):
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE)
    computer_group = models.OneToOneField(ComputerGroup, on_delete=models.CASCADE)

    def __str__(self):
        return '%s in %s' % (self.computer.computer_name, self.computer_group.group_name)
