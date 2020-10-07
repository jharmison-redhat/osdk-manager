# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager operator initialization tests.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that operator initialization can correctly scaffold
the Operator SDK-based skeleton, including a collection of APIs.
"""

import pytest

from osdk_manager.operator import Operator
from osdk_manager.exceptions import ContainerRuntimeException


@pytest.mark.parametrize("installed_osdk", ["latest"], indirect=True)
def test_no_runtime(installed_osdk, new_folder, operator_settings_1):
    """Test initialization of an Operator scaffolding."""
    with pytest.raises(ContainerRuntimeException):
        Operator(directory=new_folder, **operator_settings_1)
