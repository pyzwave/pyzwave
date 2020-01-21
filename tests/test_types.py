# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import ipaddress
import pytest

from pyzwave.types import (
    BitStreamReader,
    BitStreamWriter,
    bits_t,
    flag_t,
    IPv6,
    uint8_t,
)


@pytest.fixture
def streamReader():
    return BitStreamReader(b"\x02\x01\xCB\x40")


@pytest.fixture
def streamWriter():
    return BitStreamWriter()


def test_bits_t():
    assert bits_t(1).sizeBits == 1
    assert bits_t(2).sizeBits == 2
    assert bits_t(4).sizeBits == 4


def test_BitStreamReader_bits(streamReader):
    streamReader.advance(16)
    assert streamReader.peekValue(1) == b"\xCB"
    assert streamReader.peekByte() == 0xCB
    assert streamReader.bit() == 1
    assert streamReader.bit() == 1
    assert streamReader.bits(4) == 2


def test_BitStreamReader_bytes(streamReader):
    assert streamReader.value(1) == b"\x02"
    assert streamReader.peekValue(2) == b"\x01\xCB"
    assert streamReader.value(1) == b"\x01"


def test_BitStreamWriter_bits(streamWriter: BitStreamWriter):
    streamWriter.addBits(1, 1)
    assert streamWriter == b"\x80"
    streamWriter.addBits(3, 2)
    assert streamWriter == b"\xE0"
    streamWriter.addBits(3, 5)
    assert streamWriter == b"\xE3"
    # Make sure a new byte is appended
    streamWriter.addBits(1, 1)
    assert streamWriter == b"\xE3\x80"


def test_BitStreamWriter_bytes(streamWriter: BitStreamWriter):
    streamWriter.addBytes(2, 1, False)
    assert streamWriter == b"\x02"
    streamWriter.addBytes(2, 2, False)
    assert streamWriter == b"\x02\x02\x00"
    streamWriter.addBytes(-2, 1, True)
    assert streamWriter == b"\x02\x02\x00\xFE"


def test_flags_t():
    assert str(flag_t(True)) == "flags_t(True)"
    assert str(flag_t(False)) == "flags_t(False)"


def test_IPv6_t():
    # pylint: disable=line-too-long
    pkt = b"X\x01\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xc0\xa8\x00\xee\xea\xec\xfa\xf9"
    stream = BitStreamReader(pkt)
    assert stream.byte() == 88
    assert stream.byte() == 1
    assert stream.bits(5) == 0
    assert stream.bit() == 0
    assert stream.bits(2) == 0
    assert stream.byte() == 6
    ipv6 = IPv6.deserialize(stream)
    assert ipv6 == ipaddress.ip_address("::ffff:c0a8:ee")
    streamWriter = BitStreamWriter()
    ipv6.serialize(streamWriter)
    assert (
        streamWriter
        == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xc0\xa8\x00\xee"
    )


def test_uint8_t(streamReader):
    assert uint8_t.deserialize(streamReader) == 2
    assert uint8_t.deserialize(streamReader) == 1
    assert uint8_t.deserialize(streamReader) == 0xCB
    assert uint8_t.deserialize(streamReader) == 0x40
