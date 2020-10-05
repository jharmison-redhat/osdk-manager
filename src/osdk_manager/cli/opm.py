# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager command line OPM commands.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains the CLI subcommands directly related to the Operator Package
Manager binaries.
"""

import click
import os

from osdk_manager.cli import cli
from osdk_manager.cli.util import verbose_opt
from osdk_manager.util import get_logger


@cli.group()
@verbose_opt
def opm(verbose):
    """Manage the opm installation."""
    logger = get_logger(verbose)
    logger.debug(f'verbose: {verbose}')


@opm.command()
@verbose_opt
@click.option('-d', '--directory',
              default=os.path.expanduser('~/.operator-sdk'),
              help='The directory into which to unpack opm')
@click.option('-p', '--path', default=os.path.expanduser('~/.local/bin'),
              help='The directory in your $PATH to symlink opm into')
@click.option('-V', '--version', default='latest',
              help='The version of the Operator Package Manager to install')
def update(verbose, directory, path, version):
    """Update the opm binary, validating sums."""
    logger = get_logger(verbose)
    logger.debug(f'verbose: {verbose}')
    logger.debug(f'directory: {directory}')
    logger.debug(f'path: {path}')
    logger.debug(f'version: {version}')

    from osdk_manager.opm.update import opm_update
    version = opm_update(directory=directory, path=path, version=version)

    if path in os.getenv('PATH').split(':'):
        click.echo(f'opm version {version} is in your path as opm')
    else:
        click.echo(f'opm version {version} is available at {path}/opm')


@opm.command()
@verbose_opt
@click.option('-d', '--directory',
              default=os.path.expanduser('~/.operator-sdk'),
              help='The directory in which to look for the opm')
@click.option('-p', '--path', default=os.path.expanduser('~/.local/bin'),
              help='The directory in which to look for the opm symlink')
def version(verbose, directory, path):
    """Print the version of the installed opm binary."""
    logger = get_logger(verbose)
    logger.debug(f'verbose: {verbose}')
    logger.debug(f'directory: {directory}')
    logger.debug(f'path: {path}')
    from osdk_manager.opm.update import opm_version
    click.echo(opm_version(directory=directory, path=path))
