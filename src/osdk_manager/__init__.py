# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager package.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.
"""

import platform

if platform.system() != "Linux":
    raise EnvironmentError("osdk_manager is designed only for Linux.")
