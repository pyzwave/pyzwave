# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
from unittest.mock import MagicMock
import pytest

from pyzwave.application import Application
from pyzwave.commandclass import Basic, NetworkManagementProxy
from pyzwave.const.ZW_classcmd import COMMAND_CLASS_MULTI_CHANNEL_V2
from pyzwave.node import Node

from test_adaper import AdapterImpl


@pytest.fixture
def app() -> Application:
    async def getFailedNodeList():
        return [2]

    async def getMultiChannelCapability(_, __):
        return NetworkManagementProxy.MultiChannelCapabilityReport(commandClass=b"")

    async def getMultiChannelEndPoints(_):
        return 1

    async def getNodeInfo(_):
        return NetworkManagementProxy.NodeInfoCachedReport(
            commandClass=bytes([COMMAND_CLASS_MULTI_CHANNEL_V2])
        )

    async def getNodeList():
        return [1, 2, 3]

    adapter = AdapterImpl()
    app = Application(adapter, None)
    app._nodes = {"3:0": Node(3, adapter, [Basic.COMMAND_CLASS_BASIC])}
    app.adapter.getFailedNodeList = getFailedNodeList
    app.adapter.getMultiChannelCapability = getMultiChannelCapability
    app.adapter.getMultiChannelEndPoints = getMultiChannelEndPoints
    app.adapter.getNodeInfo = getNodeInfo
    app.adapter.getNodeList = getNodeList
    return app


@pytest.mark.asyncio
async def test_loadEndPointNode(app: Application):
    await app.loadEndPointNode(app.nodes["3:0"], 1)
    assert app.nodes.keys() == {"3:0", "3:1"}


@pytest.mark.asyncio
async def test_messageReceived(app: Application):
    handler = MagicMock()
    cmdClass = app.nodes["3:0"].supported[Basic.COMMAND_CLASS_BASIC]
    cmdClass.addListener(handler)
    assert await app.messageReceived(None, 4, 0, Basic.Report(value=42), 0) is False
    assert await app.messageReceived(None, 3, 0, Basic.Report(value=42), 0) is True
    assert await app.messageReceived(None, 3, 0, Basic.Set(value=0), 0) is False
    handler.report.assert_called_once_with(cmdClass, 42)
    assert (
        await app.messageReceived(
            None, app.adapter.nodeId, 0, Basic.Report(value=42), 0
        )
        is True
    )


def test_nodes(app: Application):
    assert app.nodes.keys() == {"3:0"}


def test_setNodeInfo(app: Application):
    # Not implemented yet
    app.setNodeInfo(0, 0, [])


@pytest.mark.asyncio
async def test_shutdown(app: Application):
    # Function not yet implemented. Update this function when it is
    assert await app.shutdown() is None


@pytest.mark.asyncio
async def test_startup(app: Application):
    await app.startup()
    assert app.nodes.keys() == {"2:0", "2:1", "3:0", "3:1"}
