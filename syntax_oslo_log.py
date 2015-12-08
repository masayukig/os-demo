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

"""A step by step syntax of minimum Oslo Logging

This example requires the following modules to be installed.

$ pip install oslo.config oslo.log

More information can be found at:

  http://docs.openstack.org/developer/oslo.log/usage.html
"""

from oslo_config import cfg
from oslo_log import log as logging
# Use default Python logging to display running output
import logging as py_logging


LOG = py_logging.getLogger(__name__)
CONF = cfg.CONF
DOMAIN = "demo"


def prepare():
    """Prepare Oslo Logging (2 or 3 steps)

    Use of Oslo Logging involves the following:

    * logging.register_options
    * logging.set_defaults (optional)
    * logging.setup
    """

    LOG.debug("Prepare Oslo Logging")

    LOG.info("Size of configuration options before %d", len(CONF))

    # Required step to register common, logging and generic configuration
    # variables
    logging.register_options(CONF)

    LOG.info("Size of configuration options after %d", len(CONF))
    for c in CONF:
        LOG.info("%s = %s" % (c, CONF[c]))

    # Optionally set new defaults if necessary for
    # * logging_context_format_string
    # * default_log_levels
    #
    # These variables default to respectively:
    #
    #  import oslo_log
    #  oslo_log._options.DEFAULT_LOG_LEVELS
    #  oslo_log._options.log_opts[0].default
    #

    extra_log_level_defaults = [
        'dogpile=INFO',
        'routes=INFO'
    ]

    logging.set_defaults(default_log_levels=CONF.default_log_levels +
                         extra_log_level_defaults)
    for pair in CONF.default_log_levels:
        LOG.info(pair.partition('='))

    # Setup further logging based on configuration
    logging.setup(CONF, DOMAIN)


if __name__ == '__main__':
    py_logging.basicConfig(level=py_logging.DEBUG)

    prepare()
