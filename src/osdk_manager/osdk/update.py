# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager update module.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains the code to update the installed Operator SDK binaries.
"""

import gnupg
import io
import logging
import os
import requests
import tempfile
import hashlib
from lastversion.lastversion import latest as lastversion

from osdk_manager.util import get_logger

_called_from_test = False
osdk_downloads = ['operator-sdk', 'ansible-operator', 'helm-operator']


class OsdkPaths(object):
    """A basic class to build paths for osdk updates."""

    def __init__(self, download: str = None, version: str = None,
                 arch: str = 'x86_64-linux-gnu',
                 directory: str = os.path.expanduser('~/.operator-sdk'),
                 path: str = os.path.expanduser('~/.local/bin')) -> None:
        """Initialize a simple tracker for OSDK-related paths."""
        download_base_url = (f'https://github.com/operator-framework/'
                             f'operator-sdk/releases/download/v{version}')
        self.filename = f'{download}-v{version}-{arch}'
        self.download_url = f'{download_base_url}/{self.filename}'
        self.signature_url = f'{self.download_url}.asc'
        self.src = f'{directory}/{self.filename}'
        self.dst = f'{path}/{download}'
        logger = get_logger()
        logger.debug(self.__dict__)


def osdk_version(directory: str = os.path.expanduser('~/.operator-sdk'),
                 path: str = os.path.expanduser('~/.local/bin')) -> str:
    """Return the version of the installed operator-sdk binaries."""
    logger = get_logger()
    for arg in [directory, path]:
        logger.debug(type(arg))
        logger.debug(arg)

    link_path = os.path.join(path, 'operator-sdk')
    if os.path.islink(link_path):
        target = os.readlink(link_path)
        binary = os.path.basename(target)
        assumed_version = binary.split('-')[2].strip('v')
    else:
        logger.info('Unable to identify operator-sdk symlink.')
        return ''

    for download in osdk_downloads:
        paths = OsdkPaths(download=download, version=assumed_version,
                          directory=directory, path=path)
        try:
            if not os.readlink(paths.dst) == paths.src:
                logger.info(f'{download} not symlinked into {path}.')
                return ''
            if not os.path.isfile(paths.src):
                logger.info(f'{paths.dst} is a dangling link to {paths.src}')
                return ''
        except FileNotFoundError:
            logger.info(f'{paths.dst} link does not exist')
            return ''

    return assumed_version


def osdk_update(directory: str = os.path.expanduser('~/.operator-sdk'),
                path: str = os.path.expanduser('~/.local/bin'),
                version: str = 'latest') -> str:
    """Update the operator-sdk binaries."""
    logger = get_logger()
    for arg in [directory, path, version]:
        logger.debug(type(arg))
        logger.debug(arg)

    gnupghome = os.path.expanduser('~/.gnupg')

    logger.debug(f'Creating {gnupghome}')
    os.makedirs(gnupghome, mode=0o700, exist_ok=True)

    logger.debug(f'Creating {directory}')
    os.makedirs(directory, exist_ok=True)

    logger.debug(f'Creating {path}')
    os.makedirs(path, exist_ok=True)

    try:
        validate_signatures = True
        gpg = gnupg.GPG(gnupghome=gnupghome)
        operator_sdk_release_keys = [
            ('keys.gnupg.net', '8018D6F1B58E194625E38581D16086E39AF46519'),
            ('keys.gnupg.net', 'BF6F6F18846753754CBB1DDFBC9679ED89ED8983'),
            ('keys.gnupg.net', '0CF50BEE7E4DF6445E08C0EA9AFDE59E90D2B445')
        ]
        for key_server, key_id in operator_sdk_release_keys:
            logger.debug(f'Importing key {key_id} from {key_server}')
            gpg.recv_keys(key_server, key_id)
    except FileNotFoundError:  # pragma: no cover
        validate_signatures = False
        logger.warning('Unable to validate signatures!')

    if version == 'latest':
        logger.debug('Determining latest version of the operator-sdk')
        version = lastversion('operator-framework/operator-sdk')
        # lastversion sets handlers on the root logger because it's mean.
        if not _called_from_test:  # pragma: no cover
            root_logger = logging.getLogger()
            root_logger.handlers.clear()

    if len(str(version)) < 1:  # pragma: no cover
        raise RuntimeError(('Unable to determine latest version. '
                            'Consider specifying it with the --version '
                            'option at the command line.'))

    logger.info(f'Identified desired installation version as {version}')
    installed_version = osdk_version(directory=directory, path=path)

    if version == installed_version:
        logger.info(f'{version} is already installed.')
        return version

    for download in osdk_downloads:
        paths = OsdkPaths(download=download, version=version,
                          directory=directory, path=path)
        if os.path.isfile(paths.src):
            logger.debug(f'Already downloaded: {paths.filename}')
        else:
            binary_fd, binary_path = tempfile.mkstemp()
            logger.debug(f'Requesting {paths.download_url}')
            binary = requests.get(paths.download_url).content
            logger.debug(f'Saving {paths.download_url}')
            with os.fdopen(binary_fd, 'wb') as f:
                f.write(binary)

            binary_sha256 = hashlib.sha256(binary).hexdigest()
            logger.debug(f'Saved {paths.dst} with SHA 256 {binary_sha256}')
            if validate_signatures:
                signature = io.BytesIO(
                    requests.get(paths.signature_url).content
                )

                logger.debug((f'Validating {paths.download_url} with signature'
                              f' from {paths.signature_url}'))

                if gpg.verify_file(signature, binary_path):
                    logger.debug(f'{paths.filename} passed GPG verification')
                else:  # pragma: no cover
                    raise RuntimeError(f'{paths.filename} failed verification')

            logger.info(f'Saving {paths.filename} to {paths.src}')
            with open(paths.src, 'wb') as f:
                f.write(binary)
            os.remove(binary_path)

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
