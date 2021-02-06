# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager about details.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains some basic variables used for setup.
"""


__title__ = "osdk-manager"
__name__ = __title__
__summary__ = "A script for managing Operator SDK-based operators."
__uri__ = "https://github.com/jharmison-redhat/osdk-manager"
__version__ = "0.3.0"
__release__ = "1"
__status__ = "Development"
__author__ = "James Harmison"
__email__ = "jharmison@gmail.com"
__license__ = "BSD-2-Clause"
__copyright__ = "2020 %s" % __author__
__requires__ = [
    'requests',
    'click',
    'lastversion',
    'python-gnupg',
    'PyYAML'
]
