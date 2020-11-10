#!/usr/bin/env python
import gnupg
import io
import logging
import os
import os.path
import requests
import tempfile
from lastversion.lastversion import latest as lastversion
from operator_sdk_manager.util import make_logger


def operator_sdk_update(directory: str = os.path.expanduser('~/.operator-sdk'),
                        path: str = os.path.expanduser('~/.local/bin'),
                        version: str = 'latest') -> str:
    """
    Update the operator-sdk binary
    """
    logger = make_logger()

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
    operator_sdk_keys = [
        ('keys.gnupg.net', '8018D6F1B58E194625E38581D16086E39AF46519'),
        ('keys.gnupg.net', 'BF6F6F18846753754CBB1DDFBC9679ED89ED8983'),
        ('keys.gnupg.net', '0CF50BEE7E4DF6445E08C0EA9AFDE59E90D2B445'),
        ('keys.gnupg.net', 'B3956A23A74E7EB8733C5A1EEDC7A519E04837AD'),
        ('keys.gnupg.net', 'ADE83605E945FA5A1BD8639C59E5B47624962185')
    ]
    for key_server_and_key_id in operator_sdk_keys:
        gpg.recv_keys(*key_server_and_key_id)

    if version == 'latest':
        version = lastversion('operator-framework/operator-sdk')

    # lastversion sets handlers on the root logger because it's mean.
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    logger.debug(f'Identified latest version as {version}')

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
            binary = requests.get(download_url).content
            with os.fdopen(binary_fd, 'wb') as f:
                f.write(binary)

            signature = io.BytesIO(requests.get(signature_url).content)

            logger.debug((f'Validating {download_url} with signature '
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
