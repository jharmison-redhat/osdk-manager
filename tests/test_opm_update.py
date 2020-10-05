# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager opm update tests.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that an update correctly installs and validates the
latest version of opm, the Operator Package Manager, but can also be used to
pin a version.
"""

import os
import os.path
import pytest


@pytest.mark.parametrize("installed_opm", ["latest", "1.14.2", "1.14.2"],  # noqa: PT014,E501
                         indirect=True)
def test_update(installed_opm):
    """Test updates with both unspecified version and a pinned version."""
    link_path = "/tmp/opm"
    assert os.path.islink(link_path)

    link_inode = os.stat(link_path)
    bin_path = "/tmp/linux-amd64-opm-{}".format(
        installed_opm
    )
    bin_inode = os.stat(bin_path)
    assert link_inode == bin_inode


@pytest.mark.parametrize("installed_opm", ["1.14.3", "1.14.3"],  # noqa: PT014
                         indirect=True)
def test_broken_link_update(installed_opm):
    """Test updates with successive installations missing a link."""
    link_path = "/tmp/opm"
    assert os.path.islink(link_path)

    link_inode = os.stat(link_path)
    bin_path = "/tmp/linux-amd64-opm-{}".format(
        installed_opm
    )
    bin_inode = os.stat(bin_path)
    assert link_inode == bin_inode

    # Unlink the installation to test ability to reapply
    os.remove(link_path)


@pytest.mark.parametrize("installed_opm", ["1.14.3", "1.14.3"],  # noqa: PT014
                         indirect=True)
def test_dangling_link_update(installed_opm):
    """Test updates with successive installations missing a binary."""
    link_path = "/tmp/opm"
    assert os.path.islink(link_path)

    link_inode = os.stat(link_path)
    bin_path = "/tmp/linux-amd64-opm-{}".format(
        installed_opm
    )
    bin_inode = os.stat(bin_path)
    assert link_inode == bin_inode

    # Remove the installation binary to test ability to reapply
    os.remove(bin_path)


@pytest.mark.parametrize("installed_opm", ["1.14.3", "1.14.3"],  # noqa: PT014
                         indirect=True)
def test_wrong_link_update(installed_opm):
    """Test updates with successive installations with the wrong link."""
    link_path = "/tmp/opm"
    assert os.path.islink(link_path)

    link_inode = os.stat(link_path)
    bin_path = "/tmp/linux-amd64-opm-{}".format(
        installed_opm
    )
    bin_inode = os.stat(bin_path)
    assert link_inode == bin_inode

    # Mislink the installation to test ability to reapply
    if os.path.islink(link_path):
        os.remove(link_path)
        os.symlink("/etc/passwd", link_path)
