# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=missing-class-docstring

from enum import Enum
import ipaddress
import pytest

from pyzwave.types import (
    BitStreamReader,
    BitStreamWriter,
    bits_t,
    bytes_t,
    dsk_t,
    enum_t,
    flag_t,
    float_t,
    HomeID,
    IPv6,
    str_t,
    uint7_t,
    uint8_t,
)


@pytest.fixture
def streamReader():
    return BitStreamReader(b"\x02\x01\xCB\x40")


@pytest.fixture
def streamWriter():
    return BitStreamWriter()


def test_bits_t():
    bits1_t = bits_t(1)
    assert bits1_t.sizeBits == 1
    assert repr(bits1_t(1)) == "bits_t(1)"
    assert int(bits1_t(1)) == 1

    bits2_t = bits_t(2)
    assert bits2_t.sizeBits == 2
    assert repr(bits2_t(2)) == "bits_t(10)"
    assert int(bits2_t(2)) == 2

    bits4_t = bits_t(4)
    assert bits4_t.sizeBits == 4
    assert repr(bits4_t(3)) == "bits_t(0011)"
    assert int(bits4_t(3)) == 3


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


def test_BitStreamReader_bytesLeft(streamReader):
    assert streamReader.bytesLeft() == 4
    assert streamReader.value(1) == b"\x02"
    assert streamReader.bytesLeft() == 3
    assert streamReader.peekValue(2) == b"\x01\xCB"
    assert streamReader.bytesLeft() == 3
    assert streamReader.value(1) == b"\x01"
    assert streamReader.bytesLeft() == 2


def test_BitStreamReader_remaining(streamReader: BitStreamReader):
    assert streamReader.remaining(advance=False) == b"\x02\x01\xcb@"
    assert streamReader.value(1) == b"\x02"
    assert streamReader.remaining() == b"\x01\xcb@"


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
    assert streamWriter == b"\x02\x00\x02"
    streamWriter.addBytes(-2, 1, True)
    assert streamWriter == b"\x02\x00\x02\xFE"


def test_bytes_t(streamReader: BitStreamReader):
    pkt = b"\x02\x01\xcb@"
    assert bytes_t.deserialize(streamReader) == pkt
    writer = BitStreamWriter()
    bytes_t(pkt).serialize(writer)
    assert writer == pkt


def test_dsk_t():
    DSK = "32333-28706-61913-46249-43027-54794-27762-42208"
    rawDSK = b"\x10~Mp\x22\xf1\xd9\xb4\xa9\xa8\x13\xd6\nlr\xa4\xe0"
    bDSK = rawDSK[1:]
    dsk = dsk_t()
    dsk.__setstate__(DSK)
    assert dsk._dsk == bDSK
    assert dsk.__getstate__() == DSK
    assert repr(dsk) == DSK

    writer = BitStreamWriter()
    dsk.serialize(writer)
    assert writer == rawDSK

    reader = BitStreamReader(rawDSK)
    assert dsk_t.deserialize(reader) == bDSK


def test_dsk_t_invalid_data():
    dsk = dsk_t()
    dsk.__setstate__("12345-67890")
    assert dsk._dsk == b""

    with pytest.raises(ValueError):
        dsk.deserialize(
            BitStreamReader(b"\x0f~Mp\x22\xf1\xd9\xb4\xa9\xa8\x13\xd6\nlr\xa4\xe0")
        )
    assert dsk.deserialize(BitStreamReader(b"")) == b""


def test_enum_t():
    class MyEnum(Enum):
        FOO = 1
        BAR = 2

    EnumType = enum_t(MyEnum, uint8_t)
    assert repr(EnumType(1)) == "FOO (0x1)"
    assert repr(EnumType(2)) == "BAR (0x2)"
    assert repr(EnumType(3)) == "UNKNOWN (0x3)"


def test_flags_t():
    assert str(flag_t(True)) == "flag_t(True)"
    assert str(flag_t(False)) == "flag_t(False)"


def test_float_t():
    value = float_t(23.2, 1, 2)
    assert value == 23.2
    assert value.scale == 2

    assert float_t.deserialize(BitStreamReader(b"\x22\x00\xe4")) == (22.8, 2, 0)


def test_HomeID():
    homeID = HomeID.deserialize(BitStreamReader(b"\xea\xec\xfa\xf9"))
    assert str(homeID) == "EAECFAF9"


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


def test_str_t():
    stream = BitStreamReader(b"\x0BHello World")
    assert str_t.deserialize(stream) == "Hello World"


def test_uint7_t(streamReader):
    assert uint7_t.deserialize(streamReader) == 1
    assert uint7_t.deserialize(streamReader) == 0
    assert uint7_t.deserialize(streamReader) == 0x20
    assert uint7_t.deserialize(streamReader) == 0x30

    streamWriter = BitStreamWriter()
    uint7_t(20).serialize(streamWriter)
    assert streamWriter == b"\x28"


def test_uint8_t(streamReader):
    assert uint8_t.deserialize(streamReader) == 2
    assert uint8_t.deserialize(streamReader) == 1
    assert uint8_t.deserialize(streamReader) == 0xCB
    assert uint8_t.deserialize(streamReader) == 0x40
