#!/usr/bin/env python
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
import sys
import os
import urllib2
import httplib    # For the  httplib.BadStatusLine Exception
import json
import logging
import pickle
import time
from coveragelink import CoverageLink


LINKS_JSON_FILE = 'links.json'
ZUUL_STATUS_FILE = 'status.json'
DEFAULT_ZUUL_STATUS_URL = 'http://zuul.openstack.org/' + ZUUL_STATUS_FILE
DEFAULT_OUTPUT_LOGS = 'http://logs.openstack.org'
PURGE_SECONDS = 60 * 5  # 5 minutes


class CoverageIndex(object):

    @staticmethod
    def read_from_url(zuul_status_url=DEFAULT_ZUUL_STATUS_URL):
        """Get the provided Zuul status file via provided url"""

        try:
            res = urllib2.urlopen(zuul_status_url)
            json_contents = res.read()
            with open(os.path.join(os.sep, 'tmp', ZUUL_STATUS_FILE), 'w') as f:
                f.write(json_contents)

        except (urllib2.HTTPError, httplib.BadStatusLine):
            raise Exception('Unable to read Zuul status at ' + zuul_status_url)

        try:
            return json.loads(json_contents)

        except ValueError:
            raise Exception('Unable to parse JSON Zuul status at ' +
                            zuul_status_url)

    @staticmethod
    def read_from_file(filename=ZUUL_STATUS_FILE):
        """Read the Zuul status from the provided filename"""

        try:
            with open(filename, 'r') as f:
                json_contents = f.read()

        except IOError:
            raise Exception('Unable to read Zuul status from ' + filename)

        try:
            return json.loads(json_contents)

        except ValueError:
            raise Exception('Unable to parse JSON Zuul status from ' +
                            filename)

    def parse_status(self, data):
        """Parse the provided Zuul Status for post/check pipelines
        and look for coverage jobs
        """

        coverage_links = []

        for pipeline in data['pipelines']:
            if pipeline['name'] in ['post', 'check']:
                links = self.process_pipeline(pipeline['name'],
                                              pipeline['change_queues'])
                coverage_links += links

        return coverage_links

    def process_pipeline(self, type, queues):
        """For the given pipeline queues identify coverage jobs
        and generate the url for the project and pipeline type
        """

        pipeline_post = 'post'
        pipeline_check = 'check'
        coverage_suffix = '-coverage'
        report_dir = 'cover'
        links = []

        for queue in queues:
            if queue['heads'] and len(queue['heads']) > 0:

                for head in queue['heads'][0]:
                    id = head['id'].split(',', 2)[0]

                    for job in head['jobs']:

                        job_name = job['name']
                        project = job_name[:len(job_name) -
                                           len(coverage_suffix)]
                        uri = []
                        # For 'post' pipeline coverage jobs
                        if job_name.endswith(coverage_suffix) and job['uuid']:

                            uuid_prefix = job['uuid'][:7]
                            if type == pipeline_post:

                                # e.g. http://logs.openstack.org/b8/b88aa ...
                                #      /post/ironic-coverage/53a1364/cover/
                                uri = [id[:2], id, type, job_name,
                                       uuid_prefix, report_dir]

                            elif type == pipeline_check:

                                # e.g. http://logs.openstack.org/27/219727/1
                                #      /check/rally-coverage/3550a36/cover/
                                patchset = head['id'].split(',', 2)[1]
                                uri = [id[-2:], id, patchset, type, job_name,
                                       uuid_prefix, report_dir]

                        if uri:
                            url = '/'.join(['http://logs.openstack.org'] + uri)
                            logging.debug(url)
                            link = CoverageLink(project, url, type)
                            links.append(link)

        logging.info('Captured {} links for {} '.format(len(links), type))
        return links

    def validate_links(self, new_links):
        """Process the list of coverage urls to confirm they
        exist and have a total line
        """

        for entry in new_links:
            if entry:
                try:
                    entry.validate()

                except Exception as e:
                    logging.warn(str(e))
                    if int(time.time()) - entry.created > PURGE_SECONDS:
                        logging.debug("Purging old link " + entry.url)
                        new_links.remove(entry)
                    continue

                logging.info('URL verified ' + entry.url)

        return

    def read_existing_links(self, filename=LINKS_JSON_FILE):
        """Read the existing links file to append new validated
        coverage links
        """

        try:
            with open(filename + '.obj', 'rb') as fo:
                links = pickle.load(fo)

            logging.info('Loaded {} existing links'.format(len(links)))

        except IOError:
            return []

        return links

    def trim_duplicates(self, links):
        """Look for older duplicate project entries and
        remove them.
        """

        new_links = []

        projects = []
        for entry in reversed(links):
            if entry.project not in projects:
                projects.append(entry.project)
                new_links.append(entry)
            else:
                logging.warn('Removal of ' + entry.url)

        logging.info('Removed {} duplicate project links'.format(
                     len(links) - len(new_links)))

        return new_links

    def publish_links(self, links, filename=LINKS_JSON_FILE):
        """Write the current valid links to the specified file"""

        # Save the unique list of links either valid or invalid
        # for future reprocessing
        links = self.trim_duplicates(links)
        try:

            logging.info('Saving %d links for reuse' % (len(links)))
            with open(filename + '.obj', 'wb') as fo:
                pickle.dump(links, fo)

        except IOError as e:
            logging.error('I/O error({}): {}'.format(e.errno, e.strerror))


        # Publish the valid links to a JSON file
        valid_links = []
        for entry in links:
            if entry and entry.isValid():
                valid_links.append(entry)

        valid_links = self.trim_duplicates(valid_links)

        json_links = []
        for entry in valid_links:
            json_links.append(entry.json())

        try:
            with open(filename, 'w') as f:
                json.dump(json_links, f)

        except IOError as e:
            logging.error('I/O error({}): {}'.format(e.errno, e.strerror))

        return

    def __init__(self, filename=None):

        logging.info('Processing started')
        # Determine if to process url or provided file
        if filename:
            data = self.read_from_file(sys.argv[1])
        else:
            try:
                data = self.read_from_url()
            # if there is an error reading url or parsing url, try again
            except Exception:
                logging.warning(
                    'First attempt to read from url failed, retrying')
                time.sleep(2)
                data = self.read_from_url()

        new_links = self.parse_status(data)
        if len(new_links) == 0:      # No new work
            return

        self.validate_links(new_links)
        # TODO Append existing links
        existing_links = self.read_existing_links()
        if existing_links:
            self.validate_links(existing_links)
            new_links = existing_links + new_links
        self.publish_links(new_links)


if __name__ == '__main__':
    logging.getLogger(__name__)
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

    CoverageIndex(sys.argv[1] if len(sys.argv) > 1 else None)
