# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-30 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mac_admin', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computer',
            name='computer_id',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='computergroup',
            name='group_id',
            field=models.IntegerField(),
        ),
    ]
