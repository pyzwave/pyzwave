import pytest
import struct

from pyzwave.message import Message
from pyzwave.commandclass import Basic
from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_BASIC,
    BASIC_GET,
)


@pytest.fixture
def basic():
    return Basic.Get.create()


def test_cmdClass(basic):
    assert basic.cmdClass == COMMAND_CLASS_BASIC


def test_cmd(basic):
    assert basic.cmd == BASIC_GET


def test_data():
    msg = Message.decode(b"\x00\x00\x01")
    assert msg.data == b"\x01"


def test_encode_byte():
    assert Basic.Get.encode(b"\x01") == struct.pack(
        "3B", COMMAND_CLASS_BASIC, BASIC_GET, 1
    )


def test_encode_int():
    assert Basic.Get.encode(1) == struct.pack("3B", COMMAND_CLASS_BASIC, BASIC_GET, 1)


def test_encode_unknown():
    with pytest.raises(ValueError):
        Basic.Get.encode(None)


def test_encode_list():
    # Change when implemented
    with pytest.raises(ValueError):
        Basic.Get.encode([1, 2])
