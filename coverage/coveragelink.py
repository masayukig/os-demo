#!/usr/bin/env python
#
# Copyright (C) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import division
from bs4 import BeautifulSoup
import urllib2
import time


class CoverageLink(object):
    """A coverage report url link for a given project"""

    valid = 'valid'

    project = ''
    url = ''
    type = ''         # type is specific for Zuul gate links
    status = ''

    created = 0       # keep a record to purge older entries

    statements = 0
    missing = 0
    excluded = 0
    branches = 0
    partial = 0
    percent = 0.0

    def __init__(self, project, url, type=None, status='unknown'):
        """Coverage link class initialization"""

        self.project = project
        self.url = url
        self.type = type
        self.status = status
        self.created = int(time.time())

    def __str__(self):
        """Simplified replication for printing object"""

        return str(self.json())

    def validate(self):
        """Determine if the specified link url is valid"""

        age = int(time.time()) - self.created
        req = urllib2.Request(self.url)

        try:
            res = urllib2.urlopen(req)
            html = res.read()
        except ValueError as e:
            raise Exception('Invalid URL')
        except urllib2.HTTPError as e:
            if e.code == 404:
                raise Exception('URL does not exist (yet %d seconds old). %s '
                                % (age, self.url))

        # Link is valid
        self.status = self.valid

        # Try to determine totals information for link
        try:
            soup = BeautifulSoup(html)
            footer = soup.find('tfoot').find('tr')
            values = list(footer.children)

            if len(values) > 7:
                self.statements = int(values[3].string)
                self.missing = int(values[5].string)
                self.excluded = int(values[7].string)

            if len(values) > 11:
                self.branches = int(values[9].string)
                self.partial = int(values[11].string)

            if len(values) == 11:     # Branch is not defined for coverage
                self.percent = float(values[9].string.strip('%'))
            if len(values) == 15:
                self.percent = float(values[13].string.strip('%'))

        except AttributeError:
            raise Exception('Unable to parse Total from ' + self.url)

        return self.isValid()

    def isValid(self):
        """Determine if the link is a valid coverage url"""

        return self.status == self.valid

    def json(self):
        """Return a simplified JSON representation"""

        return self.__dict__
