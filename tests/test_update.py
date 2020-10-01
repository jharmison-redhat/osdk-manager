# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager update tests.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that an update correctly installs and validates the
latest version, but can also be used to pin a version.
"""

import os
import os.path
import osdk_manager.osdk.update as osdk_update
import pytest
import sys


@pytest.fixture()
def installed_osdk(request):
    """Update the Operator SDK and return the version."""
    osdk_update._called_from_test = True
    python_version = "3.{}".format(sys.version_info.minor)
    return osdk_update.osdk_update(directory="/tmp/{}".format(python_version),
                                   path="/tmp/{}".format(python_version),
                                   version=request.param)


@pytest.mark.parametrize("installed_osdk", ["latest", "1.0.0"],
                         indirect=True)
def test_update(installed_osdk):
    """Test updates with both unspecified version and a pinned version."""
    link_path = "/tmp/3.{}/operator-sdk".format(sys.version_info.minor)
    assert os.path.islink(link_path)

    link_inode = os.stat(link_path)
    bin_path = "/tmp/3.{}/operator-sdk-v{}-x86_64-linux-gnu".format(
        sys.version_info.minor,
        installed_osdk
    )
    bin_inode = os.stat(bin_path)
    assert link_inode == bin_inode
