# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager command line OSDK commands.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains the CLI subcommands directly related to the Operator SDK
binaries.
"""

import click
import os

from osdk_manager.cli import cli
from osdk_manager.cli.util import verbose_opt
from osdk_manager.util import get_logger


@cli.group()
@verbose_opt
def osdk(verbose):
    """Manage the operator-sdk installation."""
    logger = get_logger(verbose)
    logger.debug(f'verbose: {verbose}')


@osdk.command()
@verbose_opt
@click.option('-p', '--path', default=os.path.expanduser('~/.local/bin'),
              help='The directory in your $PATH to install operator-sdk into')
@click.option('-V', '--version', default='latest',
              help='The version of the Operator SDK to install')
@click.option('-n', '--no-verify', is_flag=True,
              help="Don't verify GPG signatures")
def update(verbose, path, version, no_verify):
    """Update the operator-sdk binary, validating sums."""
    logger = get_logger(verbose)
    logger.debug(f'verbose: {verbose}')
    logger.debug(f'path: {path}')
    logger.debug(f'version: {version}')
    logger.debug(f'no_verify: {no_verify}')

    from osdk_manager.osdk.update import osdk_update
    version = osdk_update(path=path, version=version, verify=not no_verify)

    if path in os.getenv('PATH').split(':'):
        click.echo((f'operator-sdk version {version} is in your path as '
                    f'operator-sdk'))
    else:
        click.echo((f'operator-sdk version {version} is available at '
                    f'{path}/operator-sdk'))
