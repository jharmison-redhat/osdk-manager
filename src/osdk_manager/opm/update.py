# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager opm-specific functionality.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This subpackage includes necessary modules for updating the installation of the
Operator Package Manager, opm.
"""

import hashlib
import logging
import os
import requests
from lastversion.lastversion import latest as lastversion

from osdk_manager.util import make_logger

_called_from_test = False


class OpmPaths(object):
    """A basic class to build paths for opm updates."""

    def __init__(self, version: str = None, arch: str = 'linux-amd64',
                 directory: str = os.path.expanduser('~/.operator-sdk'),
                 path: str = os.path.expanduser('~/.local/bin')) -> None:
        """Initialize a simple tracker for OPM-related paths."""
        download_base_url = (f'https://github.com/operator-framework/'
                             f'operator-registry/releases/download/v{version}')
        self.filename = f'{arch}-opm'
        self.download_url = f'{download_base_url}/{self.filename}'
        self.src = f'{directory}/{self.filename}-{version}'
        self.dst = f'{path}/opm'
        logger = make_logger()
        logger.debug(self.__dict__)


def opm_version(directory: str = os.path.expanduser('~/.operator-sdk'),
                path: str = os.path.expanduser('~/.local/bin')) -> str:
    """Return the version of the installed opm binary."""
    logger = make_logger()
    for arg in [directory, path]:
        logger.debug(type(arg))
        logger.debug(arg)

    link_path = os.path.join(path, 'opm')
    if os.path.islink(link_path):
        target = os.readlink(link_path)
        binary = os.path.basename(target)
        assumed_version = binary.split('-')[-1]
    else:
        logger.info('Unable to identify opm symlink.')
        return ''
    paths = OpmPaths(version=assumed_version, directory=directory, path=path)
    if not os.readlink(paths.dst) == paths.src:
        logger.info(f'opm not symlinked into {path}.')
        return ''
    if not os.path.isfile(paths.src):
        logger.info(f'{paths.dst} is a dangling link to {paths.src}')
        return ''

    return assumed_version


def opm_update(directory: str = os.path.expanduser('~/.operator-sdk'),
               path: str = os.path.expanduser('~/.local/bin'),
               version: str = 'latest') -> str:
    """Update the opm binary."""
    logger = make_logger()
    for arg in [directory, path, version]:
        logger.debug(type(arg))
        logger.debug(arg)

    logger.debug(f'Creating {directory}')
    os.makedirs(directory, exist_ok=True)

    logger.debug(f'Creating {path}')
    os.makedirs(path, exist_ok=True)

    if version == 'latest':
        logger.debug('Determining latest version of opm')
        version = lastversion('operator-framework/operator-registry')
        # lastversion sets handlers on the root logger because it's mean.
        if not _called_from_test:  # pragma: no cover
            root_logger = logging.getLogger()
            root_logger.handlers.clear()

    if len(str(version)) < 1:  # pragma: no cover
        raise RuntimeError(('Unable to determine latest version. '
                            'Consider specifying it with the --version '
                            'option at the command line.'))

    logger.info(f'Identified desired installation version as {version}')
    installed_version = opm_version(directory=directory, path=path)

    if version == installed_version:
        logger.info(f'{version} is already installed.')
        return version

    paths = OpmPaths(version=version, directory=directory, path=path)
    if os.path.isfile(paths.src):
        logger.debug(f'Already downloaded: {paths.filename}')
    else:
        logger.debug(f'Requesting {paths.download_url}')
        binary = requests.get(paths.download_url).content
        logger.debug(f'Saving {paths.download_url}')
        with open(paths.src, 'wb') as f:
            f.write(binary)

        binary_sha256 = hashlib.sha256(binary).hexdigest()
        logger.debug(f'Saved {paths.dst} with SHA 256 {binary_sha256}')

    src_mode = os.stat(paths.src).st_mode
    src_mode_ex = src_mode | 0o111
    if src_mode != src_mode_ex:
        logger.info(f'Making {paths.src} executable.')
        os.chmod(paths.src, src_mode_ex & 0o7777)

    if os.path.islink(paths.dst):
        if os.readlink(paths.dst) == paths.src:
            logger.debug(f'Already linked {paths.src} to {paths.dst}')
        else:
            logger.info(f'Symlinking {paths.src} to {paths.dst}')
            os.remove(paths.dst)
            os.symlink(paths.src, paths.dst)
    else:
        logger.info(f'Symlinking {paths.src} to {paths.dst}')
        os.symlink(paths.src, paths.dst)

    return str(version)
