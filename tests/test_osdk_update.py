# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager osdk update tests.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that an update correctly installs and validates the
latest version of the operator-sdk binaries, but can also be used to pin a
version.
"""

import os
import os.path
import pytest

import osdk_manager.osdk.update as osdk_update
osdk_update._called_from_test = True


def test_osdk_validate(tmp_path):
    """Test validation of signatures on an unverifiable release of the osdk."""
    unvalidatable_version = "1.0.0-alpha.2"
    bin_path = "/tmp/operator-sdk-v{}-x86_64-linux-gnu".format(
        unvalidatable_version
    )
    if os.path.exists(bin_path):
        os.remove(bin_path)

    with pytest.raises(RuntimeError):
        osdk_update.osdk_update(version=unvalidatable_version, **tmp_path)
    version = osdk_update.osdk_update(version=unvalidatable_version,
                                      verify=False, **tmp_path)
    assert version == unvalidatable_version


def test_update(tmp_path):
    """Test updates with both latest version and a pinned version."""
    for osdk_version in ["latest", "1.0.0", "1.0.0"]:
        installed_osdk = osdk_update.osdk_update(version=osdk_version,
                                                 **tmp_path)
        link_path = "/tmp/operator-sdk"
        assert os.path.islink(link_path)

        link_inode = os.stat(link_path)
        bin_path = "/tmp/operator-sdk-v{}-x86_64-linux-gnu".format(
            installed_osdk
        )
        bin_inode = os.stat(bin_path)
        assert link_inode == bin_inode


def test_broken_osdk_update(tmp_path):
    """Test updates with successive installations missing the osdk link."""
    osdk_version = "1.0.0"
    installed_osdk = osdk_update.osdk_update(version=osdk_version,
                                             **tmp_path)
    link_path = "/tmp/operator-sdk"
    assert os.path.islink(link_path)

    # Unlink the installation to test ability to reapply
    os.remove(link_path)
    assert not os.path.islink(link_path)

    # Reinstall things
    installed_osdk = osdk_update.osdk_update(version=osdk_version,
                                             **tmp_path)

    # Make sure they are how we hope
    assert os.path.islink(link_path)
    link_inode = os.stat(link_path)
    bin_path = "/tmp/operator-sdk-v{}-x86_64-linux-gnu".format(
        installed_osdk
    )
    bin_inode = os.stat(bin_path)
    assert link_inode == bin_inode


def test_broken_link_update(tmp_path):
    """Test updates with successive installations missing a link."""
    osdk_version = "1.0.0"
    installed_osdk = osdk_update.osdk_update(version=osdk_version,
                                             **tmp_path)
    ansible_link_path = "/tmp/ansible-operator"
    assert os.path.islink(ansible_link_path)

    # Partially unlink the installation to test ability to reapply
    os.remove(ansible_link_path)
    assert not os.path.islink(ansible_link_path)

    # Reinstall things
    installed_osdk = osdk_update.osdk_update(version=osdk_version,
                                             **tmp_path)

    # Make sure they are how we hope
    assert os.path.islink(ansible_link_path)
    ansible_link_inode = os.stat(ansible_link_path)
    bin_path = "/tmp/ansible-operator-v{}-x86_64-linux-gnu".format(
        installed_osdk
    )
    ansible_bin_inode = os.stat(bin_path)
    assert ansible_link_inode == ansible_bin_inode


def test_dangling_link_update(tmp_path):
    """Test updates with successive installations missing a binary."""
    osdk_version = "1.0.0"
    installed_osdk = osdk_update.osdk_update(version=osdk_version,
                                             **tmp_path)

    link_path = "/tmp/operator-sdk"
    assert os.path.islink(link_path)

    link_inode = os.stat(link_path)
    bin_path = "/tmp/operator-sdk-v{}-x86_64-linux-gnu".format(
        installed_osdk
    )
    bin_inode = os.stat(bin_path)
    assert link_inode == bin_inode

    # Remove the target to make the link dangle
    os.remove(bin_path)
    assert not os.path.exists(bin_path)

    # Reinstall things
    installed_osdk = osdk_update.osdk_update(version=osdk_version,
                                             **tmp_path)
    link_inode = os.stat(link_path)
    bin_inode = os.stat(bin_path)
    assert link_inode == bin_inode
