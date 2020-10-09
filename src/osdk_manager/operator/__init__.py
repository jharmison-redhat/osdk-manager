# SPDX-License-Identifier: BSD-2-Clause
"""osdk-manager Operator scaffolding functionality.

Manage osdk and opm binary installation, and help to scaffold, release, and
version Operator SDK-based Kubernetes operators.

This subpackage includes the classes and modules required to scaffold, build,
validate, and push Operator-related repositories and images.
"""

import os
import yaml
from typing import TypeVar, List

from osdk_manager.util import determine_runtime, get_logger, shell


T = TypeVar("Operator")


class Operator(object):
    """A basic abstraction around manipulating operator repos and images.

    Executes various operator-sdk and opm commands as necessary to manage your
    operator project.
    """

    logger = get_logger()

    def __init__(self, directory: str = None, image: str = None,
                 version: str = None, channels: List[str] = [],
                 kinds: List[str] = [], default_sample: str = None,
                 domain: str = None, group: str = None,
                 api_version: str = None, initialized: bool = False,
                 runtime: str = None) -> None:
        """Initialize an Operator with the necessary variables."""
        self.directory = directory
        os.chdir(self.directory)
        self.image = image
        self.version = version
        self.channels = channels
        self.kinds = kinds
        self.default_sample = default_sample
        self.domain = domain
        self.group = group
        self.api_version = api_version
        self.initialized = initialized
        if runtime is not None:
            self.runtime = runtime
        else:
            self.runtime = determine_runtime()

    def __repr__(self) -> str:
        """Represent the state of this object as a string."""
        return ("Operator(directory={}, image={}, version={}, channels={},"
                " kinds={}, default_sample={}, domain={}, group={},"
                " api_version={}, initialized={}, runtime={})").format(
            self.directory,
            self.image,
            self.version,
            self.channels,
            self.kinds,
            self.default_sample,
            self.domain,
            self.group,
            self.api_version,
            self.initialized,
            self.runtime
        )

    @classmethod
    def load(cls, directory: str = '.', filename: str = "operate.yml",
             runtime: str = None) -> T:
        """Alternate constructor to load settings from a yaml file."""
        with open(os.path.join(directory, filename)) as f:
            settings = yaml.safe_load(f)
        cls.logger.debug("Recovered settings:")
        cls.logger.debug(settings)

        return cls(directory=os.path.realpath(directory),
                   image=settings.get("image"),
                   version=settings.get("version"),
                   channels=settings.get("channels"),
                   kinds=settings.get("kinds"),
                   default_sample=settings.get("default-sample"),
                   domain=settings.get("domain"),
                   group=settings.get("group"),
                   api_version=settings.get("api-version"),
                   runtime=runtime)

    def initialize_ansible_operator(self) -> None:
        """Initialize an Ansible Operator SDK operator.

        Also creates APIs represented by the Kinds specified.
        """
        if self.initialized:
            return

        [line for line in shell(
            "operator-sdk init --plugins=ansible --domain={}".format(
                self.domain
            )
        )]
        [[line for line in shell(
            "operator-sdk create api --group={} --version={} --kind={}".format(
                self.group, self.api_version, kind
            )
        )] for kind in self.kinds]

        self.initialized = True
