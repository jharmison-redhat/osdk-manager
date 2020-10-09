# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager fixtures.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains common fixtures used by tests for osdk-manager.
"""

import os
import pytest
import shutil
import tempfile
import yaml


settings_1 = {
    "domain": "io",
    "group": "operators",
    "kinds": [
        "PytestResource"
    ],
    "api_version": "v1alpha1",
    "image": "pytest-operator",
    "version": "0.0.1",
    "channels": [
        "alpha"
    ],
    "default_sample": "operators_v1alpha1_pytestresource.yaml",
}


@pytest.fixture()
def installed_opm(request):
    """Update the Operator Package Manager and return the version."""
    import osdk_manager.opm.update as opm_update
    opm_update._called_from_test = True
    return opm_update.opm_update(directory="/tmp", path="/tmp",
                                 version=request.param)


@pytest.fixture()
def installed_osdk(request):
    """Update the Operator SDK and return the version."""
    import osdk_manager.osdk.update as osdk_update
    osdk_update._called_from_test = True
    return osdk_update.osdk_update(directory="/tmp", path="/tmp",
                                   version=request.param)


@pytest.fixture()
def new_folder():
    """Create a new temp folder, cleaning it up after the test."""
    good_name = False
    while not good_name:
        folder = tempfile.mkdtemp()
        if '_' in folder:
            shutil.rmtree(folder)
        else:
            good_name = True
    yield folder
    shutil.rmtree(folder)


def operator_settings_file(settings: dict = {}) -> str:
    """Yield the path to a file with settings saved as YAML."""
    operator_file = tempfile.mkstemp()[1]
    with open(operator_file, "w") as f:
        yaml.safe_dump(settings, f)
    return operator_file


@pytest.fixture()
def operator_settings_1():
    """Return a dictionary of some basic operator settings."""
    return settings_1


@pytest.fixture()
def operator_settings_file_1():
    """Yield the path to a file with operator_settings_1 saved in it."""
    settings = {k.replace('_', '-'): v for k, v in settings_1.items()}
    operator_file = operator_settings_file(settings)
    yield operator_file
    os.remove(operator_file)
