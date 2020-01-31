# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import pathlib
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pyzwave.commandclass import Basic, Version

# from pyzwave.message import Message
from pyzwave.persistantstorage import YamlStorage

from test_commandclass import MockNode


@pytest.fixture
def node() -> MockNode:
    return MockNode([Basic.COMMAND_CLASS_BASIC, Version.COMMAND_CLASS_VERSION])


@pytest.fixture
def storage() -> YamlStorage:
    return YamlStorage("/tmp")


YAML_DATA = "supported:\n  134:\n    version: 2"


@patch("builtins.open", mock_open(read_data=YAML_DATA))
@patch("pathlib.Path")
def test_nodeAdded(path, node: MockNode, storage: YamlStorage):
    path.exists.return_value = True
    storage.nodeAdded(None, node)
    assert node.supported[Version.COMMAND_CLASS_VERSION].version == 2


def test_nodeAdded_noConfig(node: MockNode, storage: YamlStorage):
    storage.pathForNode = MagicMock(return_value=pathlib.Path("///impossible/path"))
    storage.nodeAdded(None, node)


@patch("builtins.open", new_callable=mock_open)
def test_nodeUpdated(mockOpen, node: MockNode, storage: YamlStorage):
    node.supported[Version.COMMAND_CLASS_VERSION].zwaveLibraryType = 6
    storage.nodeUpdated(node)
    # TODO: Check the written output
    print(mockOpen.mock_calls)


def test_path(storage: YamlStorage):
    assert storage.path == "/tmp"
    storage.path = "newpath"
    assert storage.path == "newpath"
