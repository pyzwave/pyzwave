# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import asyncio
import pytest

from pyzwave.commandclass import CommandClass, Version
from pyzwave.message import Message
from pyzwave.node import Node


class Adapter:
    async def sendToNode(self, cmd: Message, *_args, **_kwargs):
        pass


class MockNode(Node):
    def __init__(self, cmdClasses: list):
        super().__init__(1, Adapter, cmdClasses)
        self._queue = []

    def queue(self, msg: Message):
        self._queue.append(msg)

    async def sendAndReceive(
        self, cmd: Message, waitFor: Message, timeout: int = 3, **kwargs
    ) -> Message:
        for msg in self._queue:
            if msg.hid() == waitFor.hid():
                return msg
        raise Exception(
            "Error in test setup. Node is not setup to answer on message {}".format(
                waitFor
            )
        )


@pytest.fixture
def commandclass() -> CommandClass:
    node = Node(1, Adapter(), [])
    return CommandClass.load(0, False, node)


@pytest.fixture
def version() -> Version.Version:
    node = MockNode([Version.COMMAND_CLASS_VERSION])
    node.queue(
        Version.VersionCommandClassReport(
            requestedCommandClass=Version.COMMAND_CLASS_VERSION, commandClassVersion=4,
        )
    )
    node.queue(
        Version.VersionReport(
            zwaveLibraryType=6,
            zwaveProtocolVersion=1,
            zwaveProtocolSubVersion=2,
            applicationVersion=1,
            applicationSubVersion=0,
        )
    )
    # TODO: load settings using __setstate__ once implemented
    node.supported[Version.COMMAND_CLASS_VERSION].zwaveLibraryType = 0x06
    return node.supported[Version.COMMAND_CLASS_VERSION]


def test_getattr(version: Version):
    assert version.zwaveLibraryType == 0x06


def test_id(version: Version.Version):
    assert version.id == 0x86


@pytest.mark.asyncio
async def test_interview(version: Version.Version):
    assert version.version == 0
    await version.interview()
    assert version.version == 4


@pytest.mark.asyncio
async def test_interview_unknownVersion(commandclass: CommandClass):
    assert commandclass.version == 0
    await commandclass.interview()
    assert commandclass.version == 0


def test_node(version: Version.Version):
    assert isinstance(version.node, Node)


@pytest.mark.asyncio
async def test_requestVersion(version: Version.Version):
    assert version.version == 0

    assert await version.requestVersion() == 4
    assert version.version == 4


@pytest.mark.asyncio
async def test_requestVersion_timeout(version: Version.Version):
    async def timeout(*args, **kwargs):
        raise asyncio.TimeoutError()

    version.node.sendAndReceive = timeout
    assert await version.requestVersion() == 0


@pytest.mark.asyncio
async def test_requestVersion_unknownCommandClass(commandclass: CommandClass):
    assert commandclass.version == 0
    assert await commandclass.requestVersion() == 0
    assert commandclass.version == 0


def test_securityS0(version: Version.Version):
    assert version.securityS0 is False
