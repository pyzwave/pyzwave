# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import asyncio
from unittest.mock import MagicMock

import pytest

from pyzwave.adapter import Adapter
from pyzwave.commandclass import Basic
from pyzwave.node import Node
from test_zipconnection import ZIPConnectionImpl


@pytest.fixture
def node() -> Node:
    connection = ZIPConnectionImpl(None, None)
    future = asyncio.Future()
    future.set_result(True)
    connection.sendToNode = MagicMock()
    connection.sendToNode.return_value = future
    return Node(2, connection, [])


def test_adapter(node: Node):
    assert isinstance(node.adapter, Adapter)


def test_basicdeviceclass(node: Node):
    assert node.basicDeviceClass == 0
    node.basicDeviceClass = 2
    assert node.basicDeviceClass == 2


def test_flirs(node: Node):
    assert node.flirs is False
    node.flirs = True
    assert node.flirs is True


def test_genericdeviceclass(node: Node):
    assert node.genericDeviceClass == 0
    node.genericDeviceClass = 2
    assert node.genericDeviceClass == 2


def test_isFailed(node: Node):
    assert node.isFailed is False
    node.isFailed = True
    assert node.isFailed is True


def test_listening(node: Node):
    assert node.listening is False
    node.listening = True
    assert node.listening is True


def test_nodeId(node: Node):
    assert node.nodeId == 2


@pytest.mark.asyncio
async def test_send(node: Node):
    msg = Basic.Get()
    assert await node.send(msg) is True
    node._adapter.sendToNode.assert_called_with(2, msg, sourceEP=0, destEP=0, timeout=3)


def test_specificdeviceclass(node: Node):
    assert node.specificDeviceClass == 0
    node.specificDeviceClass = 2
    assert node.specificDeviceClass == 2
