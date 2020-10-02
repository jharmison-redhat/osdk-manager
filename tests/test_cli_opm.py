# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager cli update tests.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that the CLI correctly reports information about
updates to the Operator Package Manager.
"""

import os
import shlex
from click.testing import CliRunner
from osdk_manager.cli import cli
import osdk_manager.opm.update as opm_update

opm_update._called_from_test = True


def test_opm_update():
    """Test a basic invocation of opm update."""
    runner = CliRunner()
    args = shlex.split('opm update --directory=/tmp --path=/tmp')

    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    assert 'opm version' in result.output
    assert 'is available at /tmp/opm' in result.output


def test_opm_version_update():
    """Test a version-pinned invocation of opm update."""
    runner = CliRunner()
    args = shlex.split(
        'opm update --directory=/tmp --path=/tmp --version=1.14.2'
    )

    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    assert 'opm version 1.14.2 is available at /tmp/opm' in result.output


def test_opm_update_path():
    """Test the opm update difference between using a value in PATH."""
    PATH = os.getenv('PATH')
    os.environ['PATH'] = ':'.join([os.path.expanduser('~/.local/bin'), PATH])

    runner = CliRunner()
    args = shlex.split('opm update --version=1.14.2')
    result = runner.invoke(cli, args)

    assert 'is in your path' in result.output


def test_opm_version():
    """Test the opm version command."""
    runner = CliRunner()
    args = shlex.split('opm version')
    result = runner.invoke(cli, args)

    assert result.output.strip() == '1.14.2'
