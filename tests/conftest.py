# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager fixtures.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains common fixtures used by tests for osdk-manager.
"""

import logging
import os
import pytest
import shutil
import tempfile
import yaml

from osdk_manager.util import shell
from osdk_manager.exceptions import ShellRuntimeException


logger = logging.getLogger()

settings_1 = {
    "domain": "io",
    "group": "operators",
    "kinds": [
        "PytestResource"
    ],
    "api_version": "v1alpha1",
    "image": "harbor.jharmison.com/osdk-testing/pytest-operator",
    "version": "0.0.1",
    "channels": [
        "alpha"
    ],
    "default_sample": "operators_v1alpha1_pytestresource.yaml",
}
settings_2 = {
    "domain": "io",
    "group": "operators",
    "kinds": [
        "PytestResourceTwo"
    ],
    "api_version": "v1beta1",
    "image": "quay.io/jharmison/pytest-operator-two",
    "version": "0.0.1",
    "channels": [
        "alpha"
    ],
    "default_sample": "operators_v1beta1_pytestresourcetwo.yaml",
}


@pytest.fixture()
def tmp_path():
    """Return a simple dictionary for temporary directories."""
    return {"path": "/tmp"}


@pytest.fixture()
def installed_opm(request):
    """Update the Operator Package Manager and return the version.

    The request.param is used to specify the version to request. If specified
    as "latest", it will attempt to identify the latest version from the GitHub
    API.
    """
    import osdk_manager.opm.update as opm_update
    opm_update._called_from_test = True
    return opm_update.opm_update(directory="/tmp", path="/tmp",
                                 version=request.param)


@pytest.fixture()
def new_folder():
    """Create a new temp folder, cleaning it up after the test."""
    good_name = False
    while not good_name:
        folder = tempfile.mkdtemp()
        if '_' in folder:
            logger.debug("removing bad generated tmpdir")
            shutil.rmtree(folder)
        else:
            logger.debug("good tmpdir")
            good_name = True
    yield folder
    logger.debug("cleaning up tmpdir")
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


@pytest.fixture()
def operator_settings_2():
    """Return a dictionary of some basic operator settings."""
    return settings_2


@pytest.fixture()
def operator_settings_file_2():
    """Yield the path to a file with operator_settings_1 saved in it."""
    settings = {k.replace('_', '-'): v for k, v in settings_2.items()}
    operator_file = operator_settings_file(settings)
    yield operator_file
    os.remove(operator_file)


@pytest.fixture()
def minikube_profile():
    """Identify a running minikube instance and return its profile name.

    Returns None if the minikube or kubectl binaries aren't in $PATH, or if the
    cluster is not up and running.
    """
    try:
        ''.join(shell("which minikube"))
    except ShellRuntimeException:
        logger.warning("no minikube")
        return None  # we need minikube
    try:
        ''.join(shell("which kubectl"))
    except ShellRuntimeException:
        logger.warning("no kubectl")
        return None  # we need kubectl
    try:
        ''.join(shell("minikube status"))
    except ShellRuntimeException:
        logger.warning("no cluster up")
        return None  # we need a running cluster

    logger.info("returning minikube profile")
    return ''.join(shell("minikube profile"))
