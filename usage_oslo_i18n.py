#!/usr/bin/env python
#
# Copyright (c) 2015 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A demonstration of oslo.i18n integration module usage.

This example requires the following module to be installed.

$ pip install oslo.i18n

More information can be found at:

  http://docs.openstack.org/developer/oslo.i18n/usage.html
  http://docs.openstack.org/developer/oslo.i18n/guidelines.html
  http://docs.openstack.org/developer/oslo.i18n/api.html
"""

# OpenStack Style Guidelines exception for import statements
# See http://docs.openstack.org/developer/hacking/#imports

from demo._i18n import _, _LW, _LE

# We use the Python standard logging library in this demo
# which enables simple cut/paste demostration syntax.
# https://docs.python.org/2/howto/logging.html
#
# OpenStack modules would use the following import
#
#  from oslo_log import log as logging
#

import logging
import os

LOG = logging.getLogger(__name__)


class Demo(object):
    """A class to demonstrate the various _i18n usage patterns"""

    @staticmethod
    def warning():

        LOG.debug("Demonstrating the use of _LW for LOG.warning")
        try:
            file_name = ".does.not.exist"
            open(file_name, "r")
        except Exception:
            # When using _LW in log messages:
            #
            # Correct:     (_LW("msg %s"), var)
            # Incorrect:   _LW("msg %s") % var
            # Incorrect:   _LW("msg %s" % var)
            #
            # When adding variables to log messages string interpolation
            # should be delayed (i.e. ,) rather then being done at
            # the point of logging (i.e. %)
            #
            # http://docs.openstack.org/developer/oslo.i18n/guidelines.html#adding-variables-to-log-messages
            #
            # See Also [H702]
            # http://docs.openstack.org/developer/hacking/#internationalization-i18n-strings
            LOG.warn(_LW("Unable to open file %s"), file_name)

    @staticmethod
    def warning_multi():

        LOG.debug("Demonstrating the use of positional parameters with _LW")
        try:
            dir_name = "dir.does.not.exist"
            file_name = ".does.not.exist"
            open(os.path.join(dir_name, file_name), "r")
        except Exception:
            # Incorrect:  (_LW("%s %s"), (var, var))
            #
            # When more than one variable is used the named interpolation
            # sytnax (i.e. %(var)s) is used to help translators adjust
            # messages for gammar rules which change parameter ordering
            LOG.warn(_LW("Unable to open file %(file)s in %(dir)s"),
                     {"file": file_name, "dir": dir_name})

    @staticmethod
    def warning_with_traceback():

        LOG.debug("Demonstrating the use of _LW with traceback for warning")
        try:
            file_name = ".does.not.exist"
            open(file_name, "r")
        except Exception:
            LOG.warn(_LW("Unable to open file"),
                     exc_info=True)

    @staticmethod
    def error():

        LOG.debug("Demonstrating the use of _LE")
        try:
            str = "s"
            int(str)
        except ValueError:
            LOG.error(_LE("Unable to parse integer from %s" % str))

    @staticmethod
    def error_and_raise():

        LOG.debug("Demonstrating the use of raising an exception")
        file_name = "demo.txt"
        msg = _("Unable to determine contents of %s.") % file_name
        LOG.exception(msg)
        raise IOError(msg)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        Demo.warning()
        Demo.warning_multi()
        Demo.warning_with_traceback()
        Demo.error()
        try:
            Demo.error_and_raise()
        except IOError as e:
            LOG.debug("Handled expected IOError. %s" % e)
    except:
        pass
