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
from osdk_manager.util import in_container


@pytest.mark.parametrize("installed_osdk", ["latest"], indirect=True)
def test_no_runtime(installed_osdk, new_folder, operator_settings_1):
    """Test initialization of an Operator scaffolding."""
    if not in_container():
        pytest.skip("There should be a runtime")

    with pytest.raises(ContainerRuntimeException):
        Operator(directory=new_folder, **operator_settings_1)

    PATH = os.getenv('PATH')
    os.environ['PATH'] = ':'.join([os.path.expanduser('~/.local/bin'), PATH])
    fake_docker = os.path.join(os.path.expanduser('~/.local/bin'), 'docker')
    os.makedirs(os.path.dirname(fake_docker), exist_ok=True)
    with open(fake_docker, "w") as f:
        f.write("")
    os.chmod(fake_docker, 0o755)

    op = Operator(directory=new_folder, **operator_settings_1)
    for key, value in operator_settings_1.items():
        if isinstance(value, str):
            assert value in str(op)

    os.remove(fake_docker)
