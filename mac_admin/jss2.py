#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
'''jss.py

Class to access JSS computers and static groups.

'''

import requests
from requests.packages import urllib3
import json
import logging
import os
import sys
# TLSAdapter by https://github.com/sheagcraig/python-jss
from .tlsadapter import TLSAdapter
from .models import ComputerGroup, Computer, ComputerGroupMembership
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

class Jss:
    ''' This class handles all communication with a JSS. The basic connection settings are feteched from a json file
    and the session to a JSS is established with these connection settings (refere to __init__ method for more info.
    The class provides the following methods to fetch or update computers and static groups:

            get_all_computers(self):
                Get all computer objects from JSS and store them in database.
            get_computer(self, computer):
                Get a full computer record from JSS.
            get_static_groups(self):
                Get all computergroups from JSS and store all static groups in database.
            get_group_selection(self, software, sg):
                Not used, could search for a software name (pattern) in static groups.
            update_groups(self, computer, id_list):
                Update all static groups in id_list and add computer to those groups.
            import_group_memberships(self):
                Read all computer to static group assigments and store them in database.
    '''

    # Initialize a session
    s = requests.session()
    jss_url = ''

    def __init__(self):
        ''' The init method reads connection settings from a json file and activates those session settings. '''
        # Setup logging
        self.logger = logging.getLogger(__name__)
        # The connection settings must be provided in a JSON file:
        #   filename: ~//Library/Preferences/com.github.mvc2c.plist
        #   dict with connection settings:
        #       {
        #           'jss_pass':'yourPassword',
        #           'jss_user':'yourUser',
        #           'jss_url':'https://yourJSSUrl:8443',
        #           'jss_verify':0,
        #           'jss_warn':1
        #       }
        #       if your JSS has a self signed certificate set jsss_verify to 0 and jss_warn to 1
        #       jss_url must be the full url including https:// and port i.e. :8443
        config_path = '~/Library/Preferences/com.github.mvc2c.plist'
        full_path = os.path.expanduser(config_path)
        if os.path.exists(full_path):
            with open(full_path) as config_file:
                pl = json.load(config_file)
        else:
            self.logger.info('No jss config file %s found .. exiting!' % full_path)
            sys.exit(1)

        # Full url i.e. https://jssserver.domain.com:8443
        self.jss_url = pl['jss_url']
        # The user needs read access to computers and computergroups and update access to computergroups
        jss_user = pl['jss_user']
        jss_pass = pl['jss_pass']
        # If set to True (1) we disable warnigs for self signed certificates
        jss_warn = pl['jss_warn']
        # If set to False (0) we disable ssl verify for self signed certificates
        jss_verify = pl['jss_verify']

        # Disable urrlib3 warnigs for JSS with self signed certificate
        if jss_warn:
            urllib3.disable_warnings()

        self.s.auth = (jss_user, jss_pass)
        self.s.verify = jss_verify
        self.s.mount(self.jss_url, TLSAdapter())

    def __str__(self):
        print('Initializing session with %s' % self.jss_url)

    def get_all_computers(self):
        ''' Get all computer objects from JSS and store in database. '''
        self.s.headers.update({'Accept': 'application/json'})
        try:
            response = self.s.get(self.jss_url + '/JSSResource/computers')
        except requests.exceptions.ProxyError:
            #.info('Cannot connect to ' + self.jss_url + ' ProxyError .. exiting')
            return None
        if response.status_code != requests.codes.ok:
            self.logger.error("Request " + computer + " by name failed with return code: " + str(response.status_code))
            return None
        else:
            content = json.loads(response.content)
            for line in content['computers']:
                try:
                    Computer(computer_name=line['name'], computer_id=str(line['id'])).save()
                except IntegrityError:
                    pass
            return True


    def get_computer(self, computer):
        '''Get full set of computer information that can be retrieved by computer name!'''
        self.s.headers.update({'Accept': 'application/json'})
        try:
            response = self.s.get(self.jss_url + '/JSSResource/computers/name/' + computer)
        except requests.exceptions.ProxyError:
            self.logger.error('Cannot connect to ' + self.jss_url + ' ProxyError .. exiting')
            return None
        if response.status_code != requests.codes.ok:
            self.logger.error("Request " + computer + " by name failed with return code: " + str(response.status_code))
            return None
        else:
            content = json.loads(response.content)
            return content

    def get_static_groups(self):
        '''Get only static groups from all computergroups'''
        self.s.headers.update({'Accept': 'application/json'})
        try:
            response = self.s.get(self.jss_url + '/JSSResource/computergroups')
        except requests.exceptions.ProxyError:
            self.logger.error('Cannot connect to ' + self.jss_url + ' ProxyError .. exiting')
            return None
        if response.status_code != requests.codes.ok:
            self.logger.error('Could not load computergroups, return code was: ' + str(response.status_code))
            return None

        computergroups = json.loads(response.content)
        # In static_groups we select all static groups from computegroups
        static_groups = []
        # Extract all static groups from computer groups, we only assign to static groups
        for value in computergroups['computer_groups']:
            if value['is_smart'] == False:
                static_groups.append((str(value['id']), value['name']))
                try:
                    ComputerGroup(group_name=value['name'], group_id=str(value['id'])).save()
                except IntegrityError:
                    pass
        return static_groups

    def get_group_selection(self, software, sg):
        '''Select only groups with software in group name'''
        group_selection = []
        for value in sg:
            if lower(software) in lower(value[1]):
                group_selection.append(value)
        return group_selection

    def update_groups(self, computer, id_list):
        '''Update groups with computer'''
        put_results = []
        self.s.headers.update({'content-type': 'application/xml'})
        data = '<computer_group><computer_additions><computer><name>' \
               + computer + '</name></computer></computer_additions></computer_group>'

        for group in id_list:
            group_url = self.jss_url + '/JSSResource/computergroups/id/' + group
            try:
                response = self.s.put(url=group_url, data=data)
            except requests.exceptions.ProxyError:
                self.logger.error('Could not connect to %s : ProxyError' % group_url)
            if response.status_code == 201:
                self.logger.info('Added %s to group with id: %s' % (computer, group))
                put_results.append('Added %s to group with id: %s' % (computer, group))
            else:
                self.logger.error('Update for group %s failed with return code: %d' % (group, response.status_code))
        return put_results

    def import_group_memberships(self):
        ''' Read all computer to static group assigments and store them in database. '''
        all_computers = Computer.objects.all()
        for line in all_computers:
            content = self.get_computer(str(line))
            for value in content['computer']['groups_accounts']['computer_group_memberships']:
                try:
                    group = ComputerGroup.objects.get(group_name=value)
                    try:
                        ComputerGroupMembership(computer=line, computer_group=group, date_assigned=timezone.now(),
                                                assigned_by='jss import').save()
                    except IntegrityError:
                        pass
                except ObjectDoesNotExist:
                    pass

    def end_session(self):
        self.s.close()


# If run as main just import all data to the database to initialize
if __name__ == '__main__':
    jss = Jss()
    jss.get_all_computers()
    jss.get_static_groups()
    jss.import_group_memberships()
    jss.end_session()