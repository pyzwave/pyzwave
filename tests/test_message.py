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


def test_compose_no_attribute():
    with pytest.raises(AttributeError):
        Basic.Report().compose()


def test_encode_list():
    # Change when implemented
    with pytest.raises(ValueError):
        Basic.Get.encode([1, 2])


def test_repr():
    assert str(Basic.Report()) == "<Z-Wave BASIC cmd REPORT>"
