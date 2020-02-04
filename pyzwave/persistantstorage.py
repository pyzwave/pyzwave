# -*- coding: utf-8 -*-

import logging
import pathlib
import yaml

from pyzwave.commandclass import CommandClass
from pyzwave.node import Node

_LOGGER = logging.getLogger(__name__)


class PersistantStorage:
    """Base class for implementing persistant storage for nodes"""

    def nodeAdded(self, application, node: Node):
        """Called when a new node has been added and/or loaded"""

    def nodeUpdated(self, node: Node):
        """
        Called then the settings for a node or one of it's command classes
        has been updated
        """


class YamlStorage(PersistantStorage):
    """Store persistant settings as yaml files"""

    def __init__(self, path):
        self._path = path

    def nodeAdded(self, application, node: Node):
        path: pathlib.Path = self.pathForNode(node.nodeId)
        if not path.exists():
            return
        with open(path, "r") as fd:
            # We use base loader here to not let yaml initiate command classes itself
            settings = yaml.load(fd, Loader=yaml.BaseLoader)
        supported = settings.get("supported", {})
        for cmdClassId, cmdClass in node.supported.items():
            if str(cmdClassId) not in supported:
                continue
            cmdClass.__setstate__(supported[str(cmdClassId)])

    def nodeUpdated(self, node: Node):
        settings = {"supported": {}}
        for cmdClassId, cmdClass in node.supported.items():
            settings["supported"][cmdClassId] = self.cmdClassRepresenter(cmdClass)
        with open(self.pathForNode(node.nodeId), "w") as fd:
            yaml.dump(settings, fd)

    @property
    def path(self) -> str:
        """The path to store the yaml files"""
        return self._path

    @path.setter
    def path(self, path: str):
        self._path = path

    def pathForNode(self, nodeId: int) -> pathlib.Path:
        """Returns the path for settings for a node"""
        return pathlib.Path(self._path) / "nodes" / "{}.yml".format(nodeId)

    @staticmethod
    def cmdClassRepresenter(cmdClass: CommandClass):
        """Wrapper method for converting to YAML format"""

        class YAMLCommandClass(
            yaml.YAMLObject
        ):  # pylint: disable=missing-class-docstring
            yaml_tag = cmdClass.NAME

            def __getstate__(self):
                return cmdClass.__getstate__()

        return YAMLCommandClass()
