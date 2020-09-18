#!/usr/bin/env python
import click
import os.path
import sys
from functools import partial

from operator_sdk_manager.util import make_logger, verbose_opt


logger = make_logger()


@click.group()
@verbose_opt
@click.version_option()
def main(verbose):
    """
    Operator SDK Manager

    Manage the operator-sdk binary and associated dependencies
    """
    logger = make_logger(verbose)
    logger.debug(sys.argv)
    logger.debug(f'verbose: {verbose}')


# Show default values for all subcommands
click.option = partial(click.option, show_default=True)


@main.command()
@verbose_opt
@click.option('-d', '--directory',
              default=os.path.expanduser('~/.operator-sdk'),
              help='The directory into which to unpack the operator-sdk')
@click.option('-p', '--path', default=os.path.expanduser('~/.local/bin'),
              help='The directory in your $PATH to symlink operator-sdk into')
@click.option('-V', '--version', default='latest',
              help='The version of the Operator SDK to install')
def update(verbose, directory, path, version):
    """Updates the operator-sdk binary, validating sums"""
    logger = make_logger(verbose)
    logger.debug(f'verbose: {verbose}')
    logger.debug(f'directory: {directory}')
    logger.debug(f'path: {path}')
    logger.debug(f'version: {version}')

    from operator_sdk_manager.update import operator_sdk_update
    version = operator_sdk_update(directory=directory, path=path,
                                  version=version)

    if path in os.getenv('PATH').split(':'):
        print((f'operator-sdk version {version} is in your path as '
               '`operator-sdk`'))
    else:
        print((f'operator-sdk version {version} is available at '
               '{path}/operator-sdk'))
