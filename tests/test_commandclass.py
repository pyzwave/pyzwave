# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import asyncio
import inspect
from unittest.mock import MagicMock
import pytest

from pyzwave.commandclass import CommandClass, VarDictAttribute, Version
from pyzwave.message import Message, UnknownMessage
from pyzwave.node import Node
from pyzwave.types import dsk_t, uint8_t


class Adapter:
    async def sendToNode(self, cmd: Message, *_args, **_kwargs):
        pass


class MockNode(Node):
    def __init__(self, cmdClasses: list):
        super().__init__(1, Adapter, cmdClasses)
        self._queue = []
        self._replies = []
        self._sent = []

    def addCommandClass(self, cmdClass, securityS0=False):
        self._supported[cmdClass] = CommandClass.load(cmdClass, securityS0, self)

    def assert_message_not_sent(self, cmd: Message):
        try:
            self.assert_message_sent(cmd)
        except Exception:
            return True
        raise Exception("Message {} was sent but was not expected".format(cmd))

    def assert_message_sent(self, cmd: Message):
        for msg in self._sent:
            if inspect.isclass(cmd):
                # Not any specific parameters, just make sure any message with this type is sent
                if msg.hid() == cmd.hid():
                    return True
            elif msg == cmd:
                return True
        raise Exception("Excpected message {} was not sent".format(cmd))

    def clear(self, sent=False, queue=False):
        if sent:
            self._sent[:] = []
        if queue:
            self._queue[:] = []

    def queue(self, msg: Message):
        self._queue.insert(0, msg)

    def reply(self, msg: Message, reply: Message):
        self._replies.append((msg, reply))

    async def send(self, cmd: Message, timeout: int = 3) -> bool:
        self._sent.append(cmd)
        for msg, reply in self._replies:
            if msg.hid() == cmd.hid():
                await self.handleMessage(reply)
                break

    async def sendAndReceive(
        self, cmd: Message, waitFor: Message, timeout: int = 3, **kwargs
    ) -> Message:
        self._sent.append(cmd)
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
    node.supported[Version.COMMAND_CLASS_VERSION].__setstate__({"zwaveLibraryType": 6})
    return node.supported[Version.COMMAND_CLASS_VERSION]


def test_getattr(version: Version):
    assert version.zwaveLibraryType == 0x06


def test_getstate(version: Version):
    assert version.__getstate__() == {"version": 0, "zwaveLibraryType": 6}


@pytest.mark.asyncio
async def test_handleMessage(version: Version.Version):
    listener = MagicMock()
    listener.onVersionCommandClassReport.return_value = True
    version.addListener(listener)
    assert await version.handleMessage(Version.VersionCommandClassReport()) is True
    listener.onVersionCommandClassReport.assert_called_once()


@pytest.mark.asyncio
async def test_handleMessage_unknown(version: Version.Version):
    listener = MagicMock()
    version.addListener(listener)
    assert await version.handleMessage(UnknownMessage(0x0000)) is False
    assert listener.mock_calls == []


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


@pytest.mark.asyncio
async def test_send(version: Version.Version):
    await version.send(Version.VersionGet())
    version.node.assert_message_sent(Version.VersionGet())


def test_VarDictAttribute_dsk_t():
    DSK = "09134-08770-57123-33165-04152-33972-09108-15612"
    attribute = VarDictAttribute(dsk_t)()
    attribute[1] = DSK
    assert attribute.__getstate__() == {1: DSK}
    assert (
        attribute.debugString()
        == "VarDictAttributeType:\n\t1 = 09134-08770-57123-33165-04152-33972-09108-15612"
    )


def test_VarDictAttribute_Message():
    attribute = VarDictAttribute(Message)()
    attribute.__setstate__({1: UnknownMessage(0x0000)})
    assert attribute.__getstate__() == {1: {}}
    assert (
        attribute.debugString() == "VarDictAttributeType:\n\t1 = <Z-Wave 0x00.0x00>:\n"
    )


def test_VarDictAttribute_uint8_t():
    attribute = VarDictAttribute(uint8_t)()
    attribute.__setstate__({1: 2, 3: 4, 5: uint8_t(6)})
    assert attribute.__getstate__() == {1: 2, 3: 4, 5: 6}
    assert (
        attribute.debugString()
        == "VarDictAttributeType:\n\t1 = 0x2 (2)\n\t3 = 0x4 (4)\n\t5 = 0x6 (6)"
    )
