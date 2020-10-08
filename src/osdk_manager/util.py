# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager utilities.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains utilities utilized throughout the package and modules.
"""

import logging
import logging.handlers
import os
import shlex
import subprocess
from typing import List, Iterable

from osdk_manager.exceptions import (
    ContainerRuntimeException,
    ShellRuntimeException
)


def get_logger(verbosity: int = None):
    """Create a logger, or return an existing one with specified verbosity."""
    logger = logging.getLogger('osdk-manager')
    logger.setLevel(logging.DEBUG)

    if len(logger.handlers) == 0:
        _format = '{asctime} {name} [{levelname:^9s}]: {message}'
        formatter = logging.Formatter(_format, style='{')

        stderr = logging.StreamHandler()
        stderr.setFormatter(formatter)
        if verbosity is not None:
            stderr.setLevel(40 - (min(3, verbosity) * 10))
        else:
            stderr.setLevel(40)
        logger.addHandler(stderr)

        if os.path.exists('/dev/log'):
            syslog = logging.handlers.SysLogHandler(address='/dev/log')
            syslog.setFormatter(formatter)
            syslog.setLevel(logging.INFO)
            logger.addHandler(syslog)
    else:
        if verbosity is not None and verbosity != 0:
            stderr = logger.handlers[0]
            stderr.setLevel(40 - (min(3, verbosity) * 10))

    return logger


def _utf8ify(line_bytes: List[bytes] = None) -> str:
    """Decode line_bytes as utf-8 and strips excess whitespace."""
    return line_bytes.decode("utf-8").rstrip()


def shell(cmd: str = None, fail: bool = True) -> Iterable[str]:
    """Run a command in a subprocess, yielding lines of output from it.

    By default will cause a failure using the return code of the command. To
    change this behavior, pass fail=False.
    """
    logger = get_logger()
    logger.debug("Running: {}".format(cmd))
    proc = subprocess.Popen(shlex.split(cmd),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    for line in map(_utf8ify, iter(proc.stdout.readline, b'')):
        logger.debug("Line:    {}".format(line))
        yield line

    ret = proc.wait()
    if fail and ret != 0:
        logger.error("Command errored: {}".format(cmd))
        raise ShellRuntimeException(ret)
    elif ret != 0:
        logger.warning("Command returned {}: {}".format(ret, cmd))


def determine_runtime() -> str:  # pragma: no cover
    """Determine the container runtime installed on the system."""
    try:
        [line for line in shell("docker --help", fail=False)]
        return "docker"
    except FileNotFoundError:
        pass
    try:
        [line for line in shell("podman --help", fail=False)]
        return "podman"
    except FileNotFoundError:
        raise ContainerRuntimeException
