# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager command line utilities.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains multiple utility functions used by the cli modules
"""

import click


# We'll be using these repeatedly
def verbose_opt(func):
    """Wrap the function in a click.option for verbosity."""
    return click.option(
        "-v", "--verbose", count=True,
        help="Increase verbosity (specify multiple times for more)."
    )(func)
