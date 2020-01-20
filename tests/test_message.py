import pytest
import struct

from pyzwave.message import Message
from pyzwave.commandclass import Basic, ZWaveMessage
from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_BASIC,
    BASIC_GET,
)


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


def test_repr():
    assert str(Basic.Report()) == "<Z-Wave BASIC cmd REPORT>"
