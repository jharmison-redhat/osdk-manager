# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager fixtures.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains common fixtures used by tests for osdk-manager.
"""

import pytest


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
    import shutil
    import tempfile

    folder = tempfile.mkdtemp()
    yield folder
    shutil.rmtree(folder)


@pytest.fixture()
def operator_settings_1():
    """Return a dictionary of some basic operator settings."""
    operator = {
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
    return operator
