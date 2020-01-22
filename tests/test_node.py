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
    return Node(2, connection)


def test_adapter(node: Node):
    assert isinstance(node.adapter, Adapter)


def test_nodeId(node: Node):
    assert node.nodeId == 2


@pytest.mark.asyncio
async def test_send(node: Node):
    msg = Basic.Get()
    assert await node.send(msg) is True
    node._adapter.sendToNode.assert_called_with(2, msg, sourceEP=0, destEP=0, timeout=3)
