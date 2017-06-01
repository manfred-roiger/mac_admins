# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-30 09:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Computer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('computer_name', models.CharField(max_length=7)),
                ('computer_id', models.IntegerField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='ComputerGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=7)),
                ('group_id', models.IntegerField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='ComputerGroupMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('computer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mac_admin.Computer')),
                ('computer_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mac_admin.ComputerGroup')),
            ],
        ),
    ]
