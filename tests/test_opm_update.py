# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager opm update tests.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that an update correctly installs and validates the
latest version of opm, the Operator Package Manager, but can also be used to
pin a version.
"""

import osdk_manager.opm.update  # noqa: F401
