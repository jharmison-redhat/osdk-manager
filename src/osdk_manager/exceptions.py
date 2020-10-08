# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager exceptions.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains the custom exceptions utilized for the osdk_manager.
"""


class ContainerRuntimeException(Exception):
    """Unable to identify a container runtime in your current environment."""

    pass


class ShellRuntimeException(RuntimeError):
    """Shell command returned non-zero return code.

    Attributes:
        code -- the return code from the shell command
    """

    def __init__(self, code):
        self.code = code
