# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-02 12:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mac_admin', '0004_auto_20170601_0819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computergroupmembership',
            name='computer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mac_admin.Computer'),
        ),
        migrations.AlterField(
            model_name='computergroupmembership',
            name='computer_group',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mac_admin.ComputerGroup'),
        ),
    ]