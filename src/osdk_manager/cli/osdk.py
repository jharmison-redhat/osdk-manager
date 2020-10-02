# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager command line OSDK commands.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains the CLI subcommands directly related to the Operator SDK
binaries.
"""

import click
import os

from osdk_manager.cli import cli
from osdk_manager.cli.util import verbose_opt
from osdk_manager.util import make_logger


@cli.command()
@verbose_opt
@click.option('-d', '--directory',
              default=os.path.expanduser('~/.operator-sdk'),
              help='The directory into which to unpack the operator-sdk')
@click.option('-p', '--path', default=os.path.expanduser('~/.local/bin'),
              help='The directory in your $PATH to symlink operator-sdk into')
@click.option('-V', '--version', default='latest',
              help='The version of the Operator SDK to install')
def update(verbose, directory, path, version):
    """Update the operator-sdk binary, validating sums."""
    logger = make_logger(verbose)
    logger.debug(f'verbose: {verbose}')
    logger.debug(f'directory: {directory}')
    logger.debug(f'path: {path}')
    logger.debug(f'version: {version}')

    from osdk_manager.osdk.update import osdk_update
    version = osdk_update(directory=directory, path=path, version=version)

    if path in os.getenv('PATH').split(':'):
        click.echo((f'operator-sdk version {version} is in your path as '
                    f'operator-sdk'))
    else:
        click.echo((f'operator-sdk version {version} is available at '
                    f'{path}/operator-sdk'))
