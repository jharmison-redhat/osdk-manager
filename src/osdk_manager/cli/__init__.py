# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager command line interface.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains the main CLI interfaces, based on Click.
"""

import click
import sys

from osdk_manager.util import get_logger
from .util import verbose_opt

logger = get_logger()


@click.group()
@verbose_opt
@click.version_option()
def cli(verbose):
    """Operator SDK Manager.

    Manage the operator-sdk binary and associated dependencies.
    """
    logger = get_logger(verbose)
    logger.debug(sys.argv)
    logger.debug(f'verbose: {verbose}')


import osdk_manager.cli.osdk  # noqa E402
import osdk_manager.cli.opm  # noqa E402
