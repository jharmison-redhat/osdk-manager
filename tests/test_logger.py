# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager logger tests.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates that an update correctly installs and validates the
latest version, but can also be used to pin a version.
"""

from osdk_manager.util import make_logger


def test_normal_logger():
    """Test that a normal logger works as expected."""
    logger = make_logger()
    logger2 = make_logger()
    assert logger == logger2
    logger.handlers.clear()


def test_new_verbose_logger():
    """Test that creating a verbose logger from nothing works as expected."""
    logger = make_logger(verbosity=3)
    assert int(logger.handlers[0].level) == 10
    logger.handlers.clear()


def test_verbose_logger():
    """Test that a verbose logger correctly overrides a normal one."""
    logger = make_logger()
    assert int(logger.handlers[0].level) == 40

    logger = make_logger(verbosity=3)
    assert int(logger.handlers[0].level) == 10

    logger2 = make_logger()
    assert logger == logger2
    logger.handlers.clear()


def test_syslog_logger():
    """Test that a syslog logger problem won't break things deeply."""
    import os
    if not os.path.exists('/dev/log'):
        logger = make_logger()
        logger.debug("Test message")
        logger.handlers.clear()
        with open('/dev/log', 'w') as f:
            f.write("")
        logger = make_logger()
        logger.debug("Test message")
    else:
        logger = make_logger()
        logger.debug("Test message")
    logger.handlers.clear()
