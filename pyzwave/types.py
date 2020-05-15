import enum
import ipaddress
import math


class BitStreamReader:
    """Class for parsing streams bitwise"""

    def __init__(self, value):
        self._start = 0
        self._value = value

    def advance(self, length):
        """Advance the stream length bits"""
        self._start += length

    def bit(self, advance: bool = True) -> int:
        """Return the next bit in the stream"""
        return self.bits(1, advance)

    def bits(self, size: int = 8, advance=True) -> int:
        """Return size number of bits in the stream"""
        startBit = self._start % 8
        byte = (self.peekByte() << startBit) & 0xFF  # Mask off top part of byte
        byte = (byte >> 8 - size) & 0xFF  # Shift down and mask
        if advance:
            self.advance(size)
        return byte

    def byte(self, advance: bool = True) -> int:
        """Return one byte from the stream"""
        return int.from_bytes(self.value(1, advance), "little", signed=False)

    def bytesLeft(self) -> int:
        """Return the number of bytes remaining from the stream"""
        startByte = int(self._start / 8)
        return len(self._value) - startByte

    def peekByte(self) -> int:
        """Return the next byte from the stream without advancing the stream"""
        return self.byte(advance=False)

    def peekValue(self, size: int) -> bytes:
        """Return the next value from the stream without advancing the stream"""
        return self.value(size, advance=False)

    def remaining(self, advance: bool = True) -> bytes:
        """Return all the remaining bytes in the stream"""
        startByte = int(self._start / 8)
        if advance:
            self.advance(len(self._value) * 8)
        return self._value[startByte:]

    def value(self, size: int, advance: bool = True) -> bytes:
        """Return the next size number of bytes from the stream"""
        startByte = int(self._start / 8)
        if advance:
            self.advance(size * 8)
        if startByte + size > len(self._value):
            raise EOFError("Tried to read past end of data")
        return self._value[startByte : startByte + size]


class BitStreamWriter(bytearray):
    """Class for wringing a butearray bitwise"""

    def __init__(self):
        super().__init__()
        self._start = 0

    def addBits(self, value, size):
        """Add size number of bits to the stream"""
        byte = 0
        if self._start == 0:
            # Start new byte
            self.append(0)
        else:
            # Extract the last one
            byte = self[len(self) - 1]
        self[len(self) - 1] = byte | (value << 8 - self._start - size)
        self._start = (self._start + size) % 8

    def addBytes(self, value, size, signed, endian="big"):
        """Add size number of bytes to the stream"""
        newVal = value.to_bytes(size, endian, signed=signed)
        self.extend(newVal)
        self._start = 0


class str_t(str):  # pylint: disable=invalid-name
    """Unicode string"""

    def __getstate__(self):
        return str(self)

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize unicode string"""
        length = stream.byte()
        return stream.value(length).decode("utf-8")


class int_t(int):  # pylint: disable=invalid-name
    """Base class for any int like type"""

    endian = "big"
    signed = True
    size = 0

    def __getstate__(self):
        return int(self)

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize unsigned value from stream"""
        return cls.from_bytes(stream.value(cls.size), cls.endian, signed=cls.signed)

    def serialize(self, stream: BitStreamWriter):
        """Serialize into stream"""
        stream.addBytes(self, self.size, self.signed, self.endian)


class uint_t(int_t):  # pylint: disable=invalid-name
    """Base class for any unsigned int like type"""

    signed = False
    size = 1

    def __repr__(self):
        return "0x{0:0{1}X} ({0})".format(int(self), self.size)


class int24_t(int_t):  # pylint: disable=invalid-name
    """Signed 24 bits value"""

    size = 3


class uint3_t(int):  # pylint: disable=invalid-name
    """Type representing 3 bits value"""

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize bits from stream"""
        return stream.bits(3)

    def serialize(self, stream: BitStreamWriter):
        """Serialize bits into stream"""
        stream.addBits(self, 3)


class uint4_t(int):  # pylint: disable=invalid-name
    """Type representing 4 bits value"""

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize bits from stream"""
        return stream.bits(4)

    def serialize(self, stream: BitStreamWriter):
        """Serialize bits into stream"""
        stream.addBits(self, 4)


class uint5_t(int):  # pylint: disable=invalid-name
    """Type representing 5 bits value"""

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize bits from stream"""
        return stream.bits(5)

    def serialize(self, stream: BitStreamWriter):
        """Serialize bits into stream"""
        stream.addBits(self, 5)


class uint7_t(int):  # pylint: disable=invalid-name
    """Type representing 7 bits value"""

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize bits from stream"""
        return stream.bits(7)

    def serialize(self, stream: BitStreamWriter):
        """Serialize bits into stream"""
        stream.addBits(self, 7)


class uint8_t(uint_t):  # pylint: disable=invalid-name
    """Unsigned byte"""

    size = 1


class uint16_t(uint_t):  # pylint: disable=invalid-name
    """Unsigned word"""

    size = 2


class uint32_t(uint_t):  # pylint: disable=invalid-name
    """Unsigned 32 bits value"""

    size = 4


class BitsBase:
    """Base type for bit values"""

    sizeBits = 1

    def __init__(self, value: int):
        self._value = int(value)

    def __eq__(self, other):
        return self._value.__eq__(other)

    def __int__(self):
        return self._value

    def __repr__(self):
        return "bits_t({0:0{1}b})".format(self._value, self.sizeBits)

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize bits from stream"""
        return stream.bits(cls.sizeBits)

    def serialize(self, stream: BitStreamWriter):
        """Serialize bits into stream"""
        stream.addBits(self._value, self.sizeBits)


class bytes_t(bytes):  # pylint: disable=invalid-name
    """Variable size bytes"""

    default = b""

    def serialize(self, stream: BitStreamWriter):
        """Serialize into stream"""
        stream.extend(self)

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize bytes from stream"""
        return stream.remaining()


class flag_t(BitsBase):  # pylint: disable=invalid-name
    """Type represeting one bit"""

    def __init__(self, value: int):
        super().__init__(int(value) & 1)

    def __bool__(self):
        return bool(self._value)

    def __repr__(self):
        return "flag_t({})".format(bool(self))


def bits_t(size):  # pylint: disable=invalid-name
    """Return the type for size number of bits"""
    # pylint: disable=redefined-outer-name
    class bits_t(BitsBase):  # pylint: disable=invalid-name
        """Type represting arbitrary bits"""

        sizeBits = size

    return bits_t


def enum_t(enumType, baseType):  # pylint: disable=invalid-name
    """Return a new enum type based on the specified type"""
    # pylint: disable=redefined-outer-name
    class enum_t(baseType):  # pylint: disable=invalid-name
        """Type for representing an enum value"""

        def __repr__(self):
            value = int(self)
            try:
                if issubclass(enumType, enum.IntFlag):
                    return "{0} ({1:b})".format(str(enumType(value)), value)
                return "{} (0x{:X})".format(enumType(value).name, value)
            except Exception:
                # Enum not defined
                return "UNKNOWN (0x{:X})".format(value)

    return enum_t


class float_t(float):  # pylint: disable=invalid-name
    """Type for representing signed float values."""

    def __new__(cls, value=0, *_args):  # pylint: disable=keyword-arg-before-vararg
        # Override __new__ to allow *args
        return float.__new__(cls, value)

    def __init__(self, _value=0, size=1, scale=0):
        super().__init__()
        self._size = size
        self._scale = scale

    @property
    def scale(self) -> int:
        """The scale this value represents"""
        return self._scale

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize float value from stream"""
        precision = stream.bits(3)
        scale = stream.bits(2)
        size = stream.bits(3)
        value = int.from_bytes(stream.value(size), "big", signed=True) / math.pow(
            10, precision
        )
        return (value, size, scale)


def reserved_t(size):  # pylint: disable=invalid-name
    """Return the type for bits that are reserved and must not be used"""
    # pylint: disable=redefined-outer-name
    class reserved_t(BitsBase):  # pylint: disable=invalid-name
        """Type for when the bits are reserved and must not be used"""

        default = 0
        sizeBits = size

    return reserved_t


class dsk_t:  # pylint: disable=invalid-name
    """Type for a DSK key"""

    def __init__(self, dsk=None):
        self._dsk = dsk or b""

    def __getstate__(self):
        return "-".join(
            [
                "{:05d}".format((self._dsk[i] << 8) | self._dsk[i + 1])
                for i in range(0, len(self._dsk), 2)
            ]
        )

    def __repr__(self):
        return self.__getstate__()

    def __eq__(self, other):
        return self.__getstate__() == other

    def __setstate__(self, state):
        if isinstance(state, bytes):
            if len(state) == 16 or len(state) == 0:
                self._dsk = state
            else:
                raise ValueError("DSK must be 16 bytes, got {}".format(len(state)))
            return
        fields = state.split("-")
        if len(fields) != 8:
            return
        dsk = bytearray(16)
        for i, value in enumerate(fields):
            word = int(value, base=10)
            dsk[i * 2] = (word >> 8) & 0xFF
            dsk[i * 2 + 1] = word & 0xFF
        self._dsk = bytes(dsk)

    def serialize(self, stream: BitStreamWriter):
        """Serialize DSK"""
        stream.extend(self._dsk)

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize 16 bytes DSK"""
        return cls.deserializeN(stream, 16)

    @staticmethod
    def deserializeN(stream: BitStreamReader, length: int):
        """Deserialize variable length DSK"""
        if length == 0:
            # No key included
            return b""
        if length != 16:
            raise ValueError("DSK must be 16 bytes, got {}".format(length))
        return stream.value(length)


class IPv6(ipaddress.IPv6Address):
    """Type for a IPv6 address"""

    def serialize(self, stream: BitStreamWriter):
        """Serialize the IPv6 address"""
        stream.extend(self.packed)

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize an IPv6 address"""
        return cls(stream.value(16))


class HomeID(uint32_t):
    """Type for Z-Wave Home ID"""

    def __str__(self):
        return "{:X}".format(self)
