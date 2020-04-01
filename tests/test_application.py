# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=missing-class-docstring
from unittest.mock import MagicMock, call
import pytest

from pyzwave.application import Application
from pyzwave.commandclass import (
    Basic,
    NetworkManagementInclusion,
    NetworkManagementProxy,
    Zip,
)
from pyzwave.const.ZW_classcmd import COMMAND_CLASS_MULTI_CHANNEL_V2
from pyzwave.node import Node

from test_adaper import AdapterImpl


def asyncReturn(value):
    async def wrapper():
        return value

    return wrapper()


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
    handler.onSet.return_value = False  # Do not handle these messages
    cmdClass = app.nodes["3:0"].supported[Basic.COMMAND_CLASS_BASIC]
    cmdClass.addListener(handler)
    assert await app.messageReceived(None, 4, 0, Basic.Report(value=42), 0) is False
    assert await app.messageReceived(None, 3, 0, Basic.Report(value=42), 0) is True
    assert await app.messageReceived(None, 3, 0, Basic.Set(value=0), 0) is False
    handler.onReport.assert_called_once_with(cmdClass, Basic.Report(value=42))
    assert (
        await app.messageReceived(
            None, app.adapter.nodeId, 0, Basic.Report(value=42), 0
        )
        is True
    )


@pytest.mark.asyncio
async def test_nodeListUpdated(app: Application):
    listener = MagicMock()
    app.addListener(listener)
    assert app._nodes.keys() == {"3:0"}

    app.adapter.getNodeList = MagicMock(return_value=asyncReturn([1, 2, 3]))
    await app.nodeListUpdated(None)
    assert app._nodes.keys() == {"2:0", "2:1", "3:0"}
    listener.nodesAdded.assert_called_once_with(
        app, [app._nodes["2:0"], app._nodes["2:1"]]
    )
    assert listener.nodeAdded.call_args_list == [
        call(app, app._nodes["2:0"]),
        call(app, app._nodes["2:1"]),
    ]
    listener.nodesRemoved.assert_not_called()
    listener.nodeRemoved.assert_not_called()

    app.adapter.getNodeList.return_value = asyncReturn([1, 2])
    listener.reset_mock()
    await app.nodeListUpdated(None)
    assert app._nodes.keys() == {"2:0", "2:1"}
    listener.nodesAdded.assert_not_called()
    listener.nodeAdded.assert_not_called()
    listener.nodesRemoved.assert_called_once_with(app, ["3:0"])
    listener.nodeRemoved.assert_called_once_with(app, "3:0")


def test_nodes(app: Application):
    assert app.nodes.keys() == {"3:0"}


@pytest.mark.asyncio
async def test_onMessageReceived(app: Application):
    listener = MagicMock()
    app.addListener(listener)
    command = NetworkManagementInclusion.NodeAddStatus()
    assert await app.onMessageReceived(None, Zip.ZipPacket(command=command)) is True
    listener.addNodeStatus.assert_called_once_with(app, command)

    listener.reset_mock()
    command = NetworkManagementInclusion.NodeRemoveStatus(
        status=NetworkManagementInclusion.NodeRemoveStatus.Status.FAILED
    )
    assert await app.onMessageReceived(None, Zip.ZipPacket(command=command)) is True
    listener.nodeRemoved.assert_not_called()
    listener.nodesRemoved.assert_not_called()

    listener.reset_mock()
    command = NetworkManagementInclusion.NodeRemoveStatus(
        status=NetworkManagementInclusion.NodeRemoveStatus.Status.DONE, nodeID=0
    )
    assert await app.onMessageReceived(None, Zip.ZipPacket(command=command)) is True
    listener.nodeRemoved.assert_called_once_with(app, 0)
    listener.nodesRemoved.assert_called_once_with(app, [0])

    assert (
        await app.onMessageReceived(None, Zip.ZipPacket(command=Basic.Get())) is False
    )

    listener.reset_mock()
    listener.messageReceived.return_value = True
    assert await app.onMessageReceived(None, Zip.ZipPacket(command=Basic.Get())) is True


def test_setNodeInfo(app: Application):
    # Not implemented yet
    app.setNodeInfo(0, 0, [])


@pytest.mark.asyncio
async def test_shutdown(app: Application):
    # Function not yet implemented. Update this function when it is
    assert await app.shutdown() is None


@pytest.mark.asyncio
async def test_startup(app: Application):
    class Listener:
        calls = 0

        async def nodeAdded(self, _, __):
            Listener.calls += 1

    app.addListener(Listener())
    await app.startup()
    assert Listener.calls == 4
    assert app.nodes.keys() == {"2:0", "2:1", "3:0", "3:1"}
