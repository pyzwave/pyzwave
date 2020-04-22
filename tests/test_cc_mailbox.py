# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

import pytest

from pyzwave.message import Message


@pytest.mark.parametrize(
    "pkt,queueHandle",
    [
        (b"i\x06H", 72,),
        (b"i\x06\xfd\x00\xbb\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00r", 114),
    ],
)
def test_NodeFailing(pkt, queueHandle):
    msg = Message.decode(pkt)
    assert msg.queueHandle == queueHandle
