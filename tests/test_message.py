# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=unidiomatic-typecheck
import pytest

from pyzwave.message import Message
from pyzwave.commandclass import Basic, ZWaveMessage


@pytest.fixture
def basic():
    return Basic.Get.create()


@ZWaveMessage(1, 1)
class NonEncodableType(Message):
    attributes = (("dummy", str),)


def test_compose_no_attribute():
    with pytest.raises(AttributeError):
        Basic.Report().compose()


def test_compose_non_serializable():
    msg = NonEncodableType(dummy="FooBar")
    with pytest.raises(ValueError):
        msg.compose()


def test_compose_type():
    assert type(Basic.Get().compose()) == bytes


def test_debugString():
    assert (Basic.Report().debugString()) == "<Z-Wave BASIC.REPORT>:\n"
    assert (
        Basic.Report(value=0xFF).debugString()
    ) == "<Z-Wave BASIC.REPORT>:\n\tvalue = 0xFF (255)"
    msg = Message.decode(b"#\x02\x80P\x01\x03\x00 \x02")
    assert (
        msg.debugString()
        == "<Z-Wave ZIP.ZIP_PACKET>:\n\
	ackRequest = flag_t(True)\n\
	ackResponse = flag_t(False)\n\
	nackResponse = flag_t(False)\n\
	nackWaiting = flag_t(False)\n\
	nackQueueFull = flag_t(False)\n\
	nackOptionError = flag_t(False)\n\
	_ = bits_t(00)\n\
	headerExtIncluded = flag_t(False)\n\
	zwCmdIncluded = flag_t(True)\n\
	moreInformation = flag_t(False)\n\
	secureOrigin = flag_t(True)\n\
	_ = bits_t(00)\n\
	seqNo = 0x1 (1)\n\
	- = bits_t(0)\n\
	sourceEP = 3\n\
	- = bits_t(0)\n\
	destEP = 0\n\
	headerExtension = HeaderExtension:\n\n\
	command = <Z-Wave BASIC.GET>:\n"
    )


def test_decode_default():
    msg = Message.decode(bytes.fromhex("8503010500"))
    assert msg.nodes == []


def test_eq():
    assert Basic.Report() != 42


def test_repr():
    assert str(Basic.Report()) == "<Z-Wave BASIC.REPORT>"
