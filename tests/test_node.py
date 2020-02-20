# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import asyncio
from unittest.mock import MagicMock

import pytest

from pyzwave.adapter import Adapter
from pyzwave.commandclass import (
    AssociationGrpInfo,
    Basic,
    Supervision,
    SwitchBinary,
    Version,
    ZwavePlusInfo,
)
from pyzwave.node import Node, NodeEndPoint
from test_zipconnection import ZIPConnectionImpl

from test_adaper import runDelayed
from test_commandclass import MockNode


@pytest.fixture
def mocknode() -> Node:
    cmdClasses = [Basic.COMMAND_CLASS_BASIC, Version.COMMAND_CLASS_VERSION]
    cmdClasses.extend([0xF1, 0x00])  # Security Scheme 0 Mark
    cmdClasses.append(SwitchBinary.COMMAND_CLASS_SWITCH_BINARY)
    cmdClasses.append(0xEF)  # Support/Control mark
    cmdClasses.append(SwitchBinary.COMMAND_CLASS_SWITCH_BINARY)
    return MockNode(cmdClasses)


@pytest.fixture
def node() -> Node:
    connection = ZIPConnectionImpl(None, None)
    future = asyncio.Future()
    future.set_result(True)
    connection.sendToNode = MagicMock()
    connection.sendToNode.return_value = future
    return Node(
        2,
        connection,
        [
            ZwavePlusInfo.COMMAND_CLASS_ZWAVEPLUS_INFO,
            AssociationGrpInfo.COMMAND_CLASS_ASSOCIATION_GRP_INFO,
        ],
    )


@pytest.fixture
def nodeendpoint() -> Node:
    connection = ZIPConnectionImpl(None, None)
    node = Node(2, connection, [ZwavePlusInfo.COMMAND_CLASS_ZWAVEPLUS_INFO])
    return NodeEndPoint(node, 1, connection, [])


def test_adapter(node: Node):
    assert isinstance(node.adapter, Adapter)


def test_basicdeviceclass(node: Node):
    assert node.basicDeviceClass == 0
    node.basicDeviceClass = 2
    assert node.basicDeviceClass == 2


def test_basicdeviceclass_nodeendpoint(nodeendpoint: Node):
    assert nodeendpoint.basicDeviceClass == 0
    nodeendpoint.parent.basicDeviceClass = 2
    assert nodeendpoint.basicDeviceClass == 2


def test_endpoint(node: Node):
    assert node.endpoint == 0
    node.endpoint = 2
    assert node.endpoint == 2


def test_flirs(node: Node):
    assert node.flirs is False
    node.flirs = True
    assert node.flirs is True


def test_flirs_nodeendpoint(nodeendpoint: Node):
    assert nodeendpoint.flirs is False
    nodeendpoint.parent.flirs = True
    assert nodeendpoint.flirs is True


def test_genericdeviceclass(node: Node):
    assert node.genericDeviceClass == 0
    node.genericDeviceClass = 2
    assert node.genericDeviceClass == 2


@pytest.mark.asyncio
async def test_handleMessage(node: Node):
    # Skip handlers, when there is a session wating for the message
    node.addWaitingSession(Basic.Get)
    assert await node.handleMessage(Basic.Get()) is True

    # Try again without any sessions
    assert await node.handleMessage(Basic.Get()) is False

    # Send message with handler
    assert (
        await node.handleMessage(
            AssociationGrpInfo.GroupNameReport(groupingsIdentifier=1, name="Lifeline")
        )
        is True
    )


@pytest.mark.asyncio
async def test_handleMessage_onMessage(node: Node):
    # Test catch all message handler
    listener = MagicMock()
    node.addListener(listener)

    listener.onMessage.return_value = True
    assert await node.handleMessage(Basic.Report(value=0)) is True

    listener.onMessage.return_value = False
    assert await node.handleMessage(Basic.Report(value=0)) is False


@pytest.mark.asyncio
async def test_interview(mocknode: Node):
    mocknode.queue(
        Version.VersionCommandClassReport(
            requestedCommandClass=Version.COMMAND_CLASS_VERSION, commandClassVersion=4,
        )
    )
    mocknode.queue(
        Version.VersionReport(
            zwaveLibraryType=6,
            zwaveProtocolVersion=1,
            zwaveProtocolSubVersion=2,
            applicationVersion=1,
            applicationSubVersion=0,
        )
    )
    await mocknode.interview()
    assert mocknode.supported[Version.COMMAND_CLASS_VERSION].version == 4


@pytest.mark.asyncio
async def test_interview_timeout(mocknode: Node):
    async def interview():
        raise asyncio.TimeoutError()

    mocknode.supported[Version.COMMAND_CLASS_VERSION].interview = interview
    mocknode.supported[Basic.COMMAND_CLASS_BASIC].interview = interview
    await mocknode.interview()
    assert mocknode.supported[Version.COMMAND_CLASS_VERSION].version == 0


def test_isFailed(node: Node):
    assert node.isFailed is False
    node.isFailed = True
    assert node.isFailed is True


def test_isFailed_nodeendpoint(nodeendpoint: Node):
    assert nodeendpoint.isFailed is False
    nodeendpoint.parent.isFailed = True
    assert nodeendpoint.isFailed is True


def test_isZWavePlus(node: Node):
    assert node.isZWavePlus is True


def test_listening(node: Node):
    assert node.listening is False
    node.listening = True
    assert node.listening is True


def test_listening_nodeendpoint(nodeendpoint: Node):
    assert nodeendpoint.listening is False
    nodeendpoint.parent.listening = True
    assert nodeendpoint.listening is True


def test_nodeId(node: Node):
    assert node.nodeId == "2:0"


@pytest.mark.asyncio
async def test_send(node: Node):
    msg = Basic.Get()
    assert await node.send(msg) is True
    node._adapter.sendToNode.assert_called_with(2, msg, sourceEP=0, destEP=0, timeout=3)


@pytest.mark.asyncio
async def test_sendAndReceive(node: Node):
    async def noop(_):
        pass

    node.send = noop
    values = await asyncio.gather(
        node.sendAndReceive(Basic.Get(), Basic.Report),
        runDelayed(node.messageReceived, Basic.Report()),
    )
    assert isinstance(values[0], Basic.Report)


def test_specificdeviceclass(node: Node):
    assert node.specificDeviceClass == 0
    node.specificDeviceClass = 2
    assert node.specificDeviceClass == 2


@pytest.mark.asyncio
async def test_supervision_handled(node: Node):
    supervision = Supervision.Get(
        statusUpdates=False, sessionID=42, command=Basic.Report(value=1)
    )
    node.addWaitingSession(Basic.Report)
    assert await node.handleMessage(supervision) is True
    node._adapter.sendToNode.assert_called_with(
        node.rootNodeId,
        Supervision.Report(
            moreStatusUpdates=False,
            wakeUpRequest=False,
            sessionID=supervision.sessionID,
            status=0xFF,
            duration=0,
        ),
        destEP=0,
        sourceEP=0,
        timeout=3,
    )


@pytest.mark.asyncio
async def test_supervision_not_handled(node: Node):
    supervision = Supervision.Get(
        statusUpdates=False, sessionID=42, command=Basic.Report(value=1)
    )
    assert await node.handleMessage(supervision) is False
    node._adapter.sendToNode.assert_called_with(
        node.rootNodeId,
        Supervision.Report(
            moreStatusUpdates=False,
            wakeUpRequest=False,
            sessionID=supervision.sessionID,
            status=0x0,
            duration=0,
        ),
        destEP=0,
        sourceEP=0,
        timeout=3,
    )
