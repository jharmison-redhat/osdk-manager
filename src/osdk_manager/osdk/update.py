# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager update module.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This file contains the code to update the installed Operator SDK binaries.
"""

import hashlib
import logging
import os
import requests
from lastversion.lastversion import latest as lastversion
from tempfile import mkstemp
from pathlib import Path
from typing import List

from osdk_manager.util import get_logger, GpgTrust

_called_from_test = False

# TODO: Go full classful


class OsdkFileData(object):
    """A basic class to build paths for osdk updates."""

    def __init__(self, version: str = None, arch: str = 'linux_amd64',
                 path: Path = os.path.expanduser('~/.local/bin'),
                 verify: bool = True) -> None:
        """Initialize a simple tracker for OSDK-related paths."""
        osdk_download_url = 'https://github.com/operator-framework/operator-sdk/releases/download'  # noqa: E501
        download_base_url = f'{osdk_download_url}/v{version}'
        osdk_downloads = ['operator-sdk', 'ansible-operator', 'helm-operator']

        self.logger = get_logger()
        self.logger.debug(self.__dict__)

        self.hashes = requests.get(
            f'{download_base_url}/checksums.txt'
        ).content
        self.hash_signature = requests.get(
            f'{download_base_url}/checksums.txt.asc'
        ).content if verify else None

        self.downloads = {}
        for download in osdk_downloads:
            filename = f'{download}_{arch}'
            file_data = {
                'filename': filename,
                'url': f'{download_base_url}/{filename}',
                'dst': f'{path}/{download}'
            }
            for sha256 in self.hashes.decode().split('\n'):
                if sha256.endswith(f' {file_data["filename"]}'):
                    file_data.update({"hash": sha256.split()[0]})
                    break
            self.logger.debug({download: file_data})
            self.downloads[download] = file_data

    def files_not_matching(self) -> List[str]:
        """Return all of the download names that don't pass checksum."""
        not_matching = []
        for download in self.downloads:
            filename = self.downloads[download]['dst']
            expected_hash = self.downloads[download]['hash']
            self.logger.debug(
                f'Checking {filename} for expected hash {expected_hash}'
            )
            if os.path.exists(filename):
                existing_hash = hashlib.sha256()
                with open(filename, 'rb') as f:
                    existing_hash.update(f.read())
                if existing_hash.hexdigest() != expected_hash:
                    self.logger.info((f'Hash for {filename} does not match'
                                      f' expected hash, {expected_hash}.'))
                    not_matching.append(download)
                else:
                    self.logger.info(f'Hash for {filename} appears current.')
            else:
                self.logger.info(f'{filename} not present.')
                not_matching.append(download)
        self.logger.debug(f'not_matching: {not_matching}')
        return not_matching


def osdk_update(path: str = os.path.expanduser('~/.local/bin'),
                version: str = 'latest', verify: bool = True) -> str:
    """Update the operator-sdk binaries."""
    logger = get_logger()
    for arg in [path, version, verify]:
        logger.debug(type(arg))
        logger.debug(arg)

    logger.debug(f'Creating {path}')
    os.makedirs(path, exist_ok=True)

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
    osdk_file_data = OsdkFileData(version=version, path=path)

    if verify:
        gpg = GpgTrust()
        gpg.trust('3B2F1481D146238080B346BB052996E2A20B5C7E')
        hashes_fd, hashes_path = mkstemp()
        with os.fdopen(hashes_fd, 'wb') as f:
            f.write(osdk_file_data.hashes)
        try:
            gpg.verify(hashes_path, osdk_file_data.hash_signature)
        finally:
            os.remove(hashes_path)
    else:
        logger.warning('Not validating signatures as requested.')

    for download in osdk_file_data.files_not_matching():
        data = osdk_file_data.downloads[download]
        binary = requests.get(data["url"]).content
        logger.info(f'Writing {data["dst"]}.')
        with open(data["dst"], 'wb') as f:
            f.write(binary)

        mode = os.stat(data["dst"]).st_mode
        mode_ex = mode | 0o111
        if mode != mode_ex:
            logger.info(f'Making {data["dst"]} executable.')
            os.chmod(data["dst"], mode_ex & 0o7777)

    return str(version)
