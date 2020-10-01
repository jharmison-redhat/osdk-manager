# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager update module.

Manager Operator SDK binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains the code to update the installed Operator SDK binaries.
"""

import gnupg
import io
import logging
import os
import os.path
import requests
import tempfile
import hashlib
from lastversion.lastversion import latest as lastversion
from osdk_manager.util import make_logger

_called_from_test = False


def osdk_update(directory: str = os.path.expanduser('~/.operator-sdk'),
                path: str = os.path.expanduser('~/.local/bin'),
                version: str = 'latest') -> str:
    """Update the operator-sdk binaries."""
    logger = make_logger()
    lastversionrun = False
    for arg in [directory, path, version]:
        logger.debug(type(arg))
        logger.debug(arg)

    gnupghome = os.path.expanduser('~/.gnupg')
    if not os.path.isdir(gnupghome):
        logger.debug(f'Creating {gnupghome}')
        os.mkdir(gnupghome, mode=0o700)
    if not os.path.isdir(directory):
        logger.debug(f'Creating {directory}')
        os.mkdir(directory)
    if not os.path.isdir(path):
        logger.debug(f'Creating {path}')
        os.mkdir(path)

    gpg = gnupg.GPG(gnupghome=gnupghome)
    operator_sdk_release_keys = [
        ('keys.gnupg.net', '8018D6F1B58E194625E38581D16086E39AF46519'),
        ('keys.gnupg.net', 'BF6F6F18846753754CBB1DDFBC9679ED89ED8983'),
        ('keys.gnupg.net', '0CF50BEE7E4DF6445E08C0EA9AFDE59E90D2B445')
    ]
    for key_server, key_id in operator_sdk_release_keys:
        logger.debug(f'Importing key {key_id} from {key_server}')
        gpg.recv_keys(key_server, key_id)

    if version == 'latest':
        logger.debug('Determining latest version of the operator-sdk')
        version = lastversion('operator-framework/operator-sdk')
        lastversionrun = True

    # lastversion sets handlers on the root logger because it's mean.
    # But when testing, don't do this!
    if not _called_from_test:
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
    if len(str(version)) < 1:
        raise RuntimeError(('Unable to determine latest version. '
                            'Consider specifying it with the --version '
                            'option at the command line.'))
    elif lastversionrun:
        logger.info(f'Identified latest version as {version}')

    downloads = ['operator-sdk', 'ansible-operator', 'helm-operator']
    download_base_url = (f'https://github.com/operator-framework/operator-sdk/'
                         f'releases/download/v{version}')
    arch = 'x86_64-linux-gnu'

    for download in downloads:
        filename = f'{download}-v{version}-{arch}'
        download_url = f'{download_base_url}/{filename}'
        signature_url = f'{download_url}.asc'
        src = f'{directory}/{filename}'
        dst = f'{path}/{download}'

        if os.path.isfile(src):
            logger.debug(f'Already downloaded: {filename}')
        else:
            binary_fd, binary_path = tempfile.mkstemp()
            logger.debug(f'Requesting {download_url}')
            binary = requests.get(download_url).content
            logger.debug(f'Saving {download_url}')
            with os.fdopen(binary_fd, 'wb') as f:
                f.write(binary)

            binary_sha256 = hashlib.sha256(binary).hexdigest()
            logger.debug(f'Saved {dst} with SHA 256 {binary_sha256}')

            signature = io.BytesIO(requests.get(signature_url).content)

            logger.debug((f'Validating {download_url} with signature from '
                          f'{signature_url}'))

            if gpg.verify_file(signature, binary_path):
                logger.debug(f'{filename} passed GPG verification')
            else:
                logger.error(f'{filename} failed verification!')
                raise RuntimeError(f'{filename} failed verification!')

            logger.info(f'Saving {filename} to {src}')
            with open(src, 'wb') as f:
                f.write(binary)
            os.remove(binary_path)

        src_mode = os.stat(src).st_mode
        src_mode_ex = src_mode | 0o111
        if src_mode != src_mode_ex:
            logger.info(f'Making {src} executable.')
            os.chmod(src, src_mode_ex & 0o7777)

        if os.path.islink(dst):
            symlink_inode = os.stat(dst)
            download_inode = os.stat(src)
            if download_inode == symlink_inode:
                logger.debug(f'Already linked {src} to {dst}')
            else:
                logger.info(f'Updating symlink from {src} to {dst}')
                os.remove(dst)
                os.symlink(src, dst)
        else:
            logger.info(f'Symlinking {src} to {dst}')
            os.symlink(src, dst)

    return str(version)
