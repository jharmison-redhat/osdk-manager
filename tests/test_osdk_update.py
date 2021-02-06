# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager osdk update tests.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that an update correctly installs and validates the
latest version of the operator-sdk binaries, but can also be used to pin a
version.
"""

import os

from osdk_manager.util import get_logger
import osdk_manager.osdk.update as osdk_update
osdk_update._called_from_test = True


def test_update(tmp_path):
    """Test updates with both latest version and a pinned version."""
    _ = get_logger(verbosity=4)
    for osdk_version in ["latest", "1.3.1", "1.3.1"]:
        version = osdk_update.osdk_update(version=osdk_version, **tmp_path)
        file_data = osdk_update.OsdkFileData(version=version, **tmp_path)
        assert file_data.files_not_matching() == []
        for filename in file_data.downloads:
            try:
                os.remove(file_data.downloads[filename]['dst'])
            except Exception:
                pass
