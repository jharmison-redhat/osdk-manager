# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager operator initialization tests.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that operator initialization can correctly scaffold
the Operator SDK-based skeleton, including a collection of APIs.
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
