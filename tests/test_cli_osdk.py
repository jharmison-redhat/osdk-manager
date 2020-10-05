# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager cli update tests.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that the CLI correctly reports information about
updates to the Operator SDK.
"""

import os
import shlex
from click.testing import CliRunner
from osdk_manager.cli import cli
from osdk_manager.util import get_logger
import osdk_manager.osdk.update as osdk_update

osdk_update._called_from_test = True


def test_osdk_update():
    """Test a basic invocation of osdk-manager update."""
    runner = CliRunner()
    args = shlex.split('osdk update --directory=/tmp --path=/tmp')

    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    assert 'operator-sdk version' in result.output
    assert 'is available at /tmp/operator-sdk' in result.output


def test_osdk_version_update():
    """Test a version-pinned invocation of osdk-manager update."""
    runner = CliRunner()
    args = shlex.split(
        'osdk update --directory=/tmp --path=/tmp --version=1.0.0'
    )

    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    assert 'operator-sdk version 1.0.0 is available at /tmp/operator-sdk' in \
        result.output


def test_osdk_update_verbosity():
    """Test the osdk-manager update command verbosity flag."""
    runner = CliRunner()
    args = shlex.split('osdk update --directory=/tmp --path=/tmp -vvv')
    logger = get_logger()
    logger.handlers.clear()

    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    assert int(logger.handlers[0].level) == 10


def test_osdk_verbosity_update():
    """Test the osdk-manager verbosity with an update afterwards."""
    runner = CliRunner()
    args = shlex.split('-vvv osdk update --directory=/tmp --path=/tmp')
    logger = get_logger()
    logger.handlers.clear()

    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    assert int(logger.handlers[0].level) == 10


def test_osdk_update_path():
    """Test the osdk-manager difference between using a value in PATH."""
    PATH = os.getenv('PATH')
    os.environ['PATH'] = ':'.join([os.path.expanduser('~/.local/bin'), PATH])

    runner = CliRunner()
    args = shlex.split('osdk update --version=1.0.0')
    result = runner.invoke(cli, args)

    assert 'is in your path' in result.output


def test_osdk_version():
    """Test the osdk-manager osdk version command."""
    runner = CliRunner()
    args = shlex.split('osdk version')
    result = runner.invoke(cli, args)

    assert result.output.strip() == '1.0.0'
