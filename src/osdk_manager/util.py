# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager utilities.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains utilities utilized throughout the package and modules.
"""

import os
import logging
import logging.handlers


def make_logger(verbosity: int = None):
    """Create a logger, or return an existing one with specified verbosity."""
    logger = logging.getLogger('osdk-manager')
    logger.setLevel(logging.DEBUG)

    if len(logger.handlers) == 0:
        _format = '{asctime} {name} [{levelname:^9s}]: {message}'
        formatter = logging.Formatter(_format, style='{')

        stderr = logging.StreamHandler()
        stderr.setFormatter(formatter)
        if verbosity is not None:
            stderr.setLevel(40 - (min(3, verbosity) * 10))
        else:
            stderr.setLevel(40)
        logger.addHandler(stderr)

        if os.path.exists('/dev/log'):
            syslog = logging.handlers.SysLogHandler(address='/dev/log')
            syslog.setFormatter(formatter)
            syslog.setLevel(logging.INFO)
            logger.addHandler(syslog)
    else:
        if verbosity is not None:
            stderr = logger.handlers[0]
            stderr.setLevel(40 - (min(3, verbosity) * 10))

    return logger
