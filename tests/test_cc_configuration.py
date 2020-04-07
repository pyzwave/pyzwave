# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

from pyzwave.commandclass import Configuration


def test_set():
    msg = Configuration.Set(parameterNumber=1, default=False, size=1, value=0x42)
    assert msg.compose() == b"\x70\x04\x01\x01\x42"
    msg = Configuration.Set(parameterNumber=1, default=False, size=2, value=0x1234)
    assert msg.compose() == b"\x70\x04\x01\x02\x12\x34"
    msg = Configuration.Set(parameterNumber=1, default=False, size=4, value=0x12345678)
    assert msg.compose() == b"\x70\x04\x01\x04\x12\x34\x56\x78"
