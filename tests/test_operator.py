# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager operator initialization tests.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that operator object can properly scaffold, build, and
bundle operators from a settings definition or file.
"""

import os
import pytest

from osdk_manager.exceptions import ContainerRuntimeException
from osdk_manager.operator import Operator


def test_load_operator(operator_settings_file_1):
    """Test a basic load of an Operator from YAML."""
    op = Operator.load(directory=os.path.dirname(operator_settings_file_1),
                       filename=os.path.basename(operator_settings_file_1))
    assert str(op).startswith('Operator(')


@pytest.mark.parametrize("installed_osdk", ["latest"], indirect=True)
def test_initialize(installed_osdk, new_folder, operator_settings_1):
    """Test initialization of an Operator scaffolding."""
    op = Operator(directory=new_folder, runtime="fake", **operator_settings_1)
    try:
        op = Operator(directory=new_folder, **operator_settings_1)
    except ContainerRuntimeException:
        pass

    for key, value in operator_settings_1.items():
        if isinstance(value, str):
            assert value in str(op)

    op.initialize_ansible_operator()
    assert op.initialized

    watches_file = os.path.join(new_folder, 'watches.yaml')
    crd_files = [
        os.path.join(new_folder, "config/crd/bases/{}.{}_{}s.yaml".format(
            operator_settings_1["group"],
            operator_settings_1["domain"],
            kind.lower()
        )) for kind in operator_settings_1["kinds"]
    ]
    assert os.path.isfile(watches_file)
    for crd_file in crd_files:
        assert os.path.isfile(crd_file)

    op.initialize_ansible_operator()
    assert op.initialized


@pytest.mark.parametrize("installed_osdk", ["latest"], indirect=True)
def test_build_1(installed_osdk, new_folder, operator_settings_1):
    """Test building an initialized operator image."""
    op = Operator(directory=new_folder, runtime="fake", **operator_settings_1)
    try:
        op = Operator(directory=new_folder, **operator_settings_1)
    except ContainerRuntimeException:
        pass

    op.initialize_ansible_operator()
    image = op.build()
    expected_image = ":".join([operator_settings_1["image"],
                               operator_settings_1["version"]])
    assert expected_image in image

    images = op.get_images()
    assert (expected_image in images or
            "localhost/{}".format(expected_image) in images)


@pytest.mark.parametrize("installed_osdk", ["latest"], indirect=True)
def test_build_2(installed_osdk, new_folder, operator_settings_2):
    """Test building a different initialized operator image."""
    op = Operator(directory=new_folder, runtime="fake", **operator_settings_2)
    try:
        op = Operator(directory=new_folder, **operator_settings_2)
    except ContainerRuntimeException:
        pass

    op.initialize_ansible_operator()
    image = op.build()
    expected_image = ":".join([operator_settings_2["image"],
                               operator_settings_2["version"]])
    assert expected_image in image

    images = op.get_images()
    assert (expected_image in images or
            "localhost/{}".format(expected_image) in images)
