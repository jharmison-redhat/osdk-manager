# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager osdk update tests.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that an update correctly installs and validates the
latest version of the operator-sdk binaries, but can also be used to pin a
version.
"""

import os
import os.path
import osdk_manager.osdk.update as osdk_update
import pytest


@pytest.fixture()
def installed_osdk(request):
    """Update the Operator SDK and return the version."""
    osdk_update._called_from_test = True
    return osdk_update.osdk_update(directory="/tmp", path="/tmp",
                                   version=request.param)


@pytest.mark.parametrize("installed_osdk", ["latest", "1.0.0", "1.0.0"],  # noqa: PT014,E501
                         indirect=True)
def test_update(installed_osdk):
    """Test updates with both unspecified version and a pinned version."""
    link_path = "/tmp/operator-sdk"
    assert os.path.islink(link_path)

    link_inode = os.stat(link_path)
    bin_path = "/tmp/operator-sdk-v{}-x86_64-linux-gnu".format(
        installed_osdk
    )
    bin_inode = os.stat(bin_path)
    assert link_inode == bin_inode


@pytest.mark.parametrize("installed_osdk", ["1.0.0", "1.0.0"],  # noqa: PT014
                         indirect=True)
def test_broken_link_update(installed_osdk):
    """Test updates with broken successive installations."""
    link_path = "/tmp/operator-sdk"
    assert os.path.islink(link_path)

    link_inode = os.stat(link_path)
    bin_path = "/tmp/operator-sdk-v{}-x86_64-linux-gnu".format(
        installed_osdk
    )
    bin_inode = os.stat(bin_path)
    assert link_inode == bin_inode

    # Partially unlink the installation to test ability to reapply
    ansible_operator_link_path = "/tmp/ansible-operator"
    if os.path.islink(ansible_operator_link_path):
        os.remove(ansible_operator_link_path)


@pytest.mark.parametrize("installed_osdk", ["1.0.0", "1.0.0"],  # noqa: PT014
                         indirect=True)
def test_dangling_link_update(installed_osdk):
    """Test updates with broken successive installations."""
    link_path = "/tmp/operator-sdk"
    assert os.path.islink(link_path)

    link_inode = os.stat(link_path)
    bin_path = "/tmp/operator-sdk-v{}-x86_64-linux-gnu".format(
        installed_osdk
    )
    bin_inode = os.stat(bin_path)
    assert link_inode == bin_inode

    # Partially unlink the installation to test ability to reapply
    ansible_operator_link_path = "/tmp/ansible-operator"
    if os.path.islink(ansible_operator_link_path):
        os.remove(os.readlink(ansible_operator_link_path))
