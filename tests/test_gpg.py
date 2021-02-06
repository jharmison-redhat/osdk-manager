# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager osdk update tests.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This test set validates gpg signature validation works when it should and
doesn't when it shouldn't.
"""

import os
import pytest
import requests
from osdk_manager.util import get_logger, GpgTrust


def test_valid_signature(tmp_path):
    """Tests a file with a known good signature."""
    _ = get_logger(verbosity=4)
    release_1_4_0_sums = requests.get((
        'https://github.com/operator-framework/operator-sdk/releases/download'
        '/v1.4.0/checksums.txt'
    )).content
    release_1_4_0_sig = requests.get((
        'https://github.com/operator-framework/operator-sdk/releases/download'
        '/v1.4.0/checksums.txt.asc'
    )).content
    sum_1_4_0_file = os.path.join(tmp_path['path'], 'checksums.txt')
    with open(sum_1_4_0_file, 'wb') as f:
        f.write(release_1_4_0_sums)
    gpg = GpgTrust()
    assert gpg.verify(target=sum_1_4_0_file, signature=release_1_4_0_sig)


def test_invalid_signature(tmp_path):
    """Tests a file with a known bad signature."""
    _ = get_logger(verbosity=4)
    release_1_4_0_sums = requests.get((
        'https://github.com/operator-framework/operator-sdk/releases/download'
        '/v1.4.0/checksums.txt'
    )).content
    release_1_3_1_sig = requests.get((
        'https://github.com/operator-framework/operator-sdk/releases/download'
        '/v1.3.1/checksums.txt.asc'
    )).content
    sum_1_4_0_file = os.path.join(tmp_path['path'], 'checksums.txt')
    with open(sum_1_4_0_file, 'wb') as f:
        f.write(release_1_4_0_sums)
    gpg = GpgTrust()
    with pytest.raises(RuntimeError):
        gpg.verify(target=sum_1_4_0_file, signature=release_1_3_1_sig)
