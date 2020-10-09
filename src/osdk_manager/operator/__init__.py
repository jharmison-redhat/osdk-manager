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
        if '/' in image:
            self.image = image
        else:
            self.image = "localhost/{}".format(image)
        self.version = version
        self.tag = version
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
        return ("Operator(directory={}, image={}, version={}, tag={},"
                " channels={}, kinds={}, default_sample={}, domain={},"
                " group={}, api_version={}, initialized={},"
                " runtime={})").format(
            self.directory,
            self.image,
            self.version,
            self.tag,
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

    def _set_vars(self) -> None:
        """Export appropriate variables into the environment for the SDK."""
        os.environ["IMG"] = ':'.join([self.image, self.tag])
        os.environ["BUNDLE_IMG"] = ':'.join([
            self.image + "-operator", self.tag
        ])
        if len(self.channels) > 0:
            os.environ["BUNDLE_CHANNELS"] = ','.join(self.channels)
            os.environ["BUNDLE_DEFAULT_CHANNEL"] = self.channels[0]

    def build(self) -> str:
        """Build an operator image using the saved values.

        Returns the image name and tag as a string.
        """
        self._set_vars()
        [line for line in shell("{} build . -t {}".format(self.runtime,
                                                          os.getenv("IMG")))]
        return os.getenv("IMG")

    def get_images(self) -> List[str]:
        """Return a list of all images related to this operator."""
        ret = []
        for line in shell(self.runtime +
                          " images --format='{{.Repository}}:{{.Tag}}'"):
            if line.startswith(self.image):
                ret.append(line.strip())
        return ret
