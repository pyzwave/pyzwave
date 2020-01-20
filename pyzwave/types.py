import ipaddress
import struct


class BitStreamReader:
    def __init__(self, value):
        self._start = 0
        self._value = value

    def advance(self, length):
        self._start += length

    def bit(self, advance: bool = True) -> int:
        return self.bits(1, advance)

    def bits(self, size: int = 8, advance=True) -> int:
        startBit = self._start % 8
        byte = (self.peekByte() << startBit) & 0xFF  # Mask off top part of byte
        byte = (byte >> 8 - size) & 0xFF  # Shift down and mask
        if advance:
            self.advance(size)
        return byte

    def byte(self, advance: bool = True) -> int:
        return int.from_bytes(self.value(1, advance), "little", signed=False)

    def peekByte(self) -> int:
        return self.byte(advance=False)

    def peekValue(self, size: int) -> bytes:
        return self.value(size, advance=False)

    def value(self, size: int, advance: bool = True) -> bytes:
        startByte = int((self._start + size) / 8)
        if advance:
            self.advance(size * 8)
        return self._value[startByte : startByte + size]


class BitStreamWriter(bytearray):
    def __init__(self):
        super().__init__()
        self._start = 0

    def addBits(self, value, size):
        byte = 0
        if self._start == 0:
            # Start new byte
            self.append(0)
        else:
            # Extract the last one
            byte = self[len(self) - 1]
        self[len(self) - 1] = byte | (value << 8 - self._start - size)
        self._start = (self._start + size) % 8

    def addBytes(self, value, size, signed):
        newVal = value.to_bytes(size, "little", signed=signed)
        self.extend(newVal)
        self._start = 0


class int_t(int):
    signed = True
    size = 0

    def serialize(self, stream: BitStreamWriter):
        stream.addBytes(self, self.size, self.signed)


class uint_t(int_t):
    signed = False
    size = 1

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        return cls.from_bytes(stream.value(cls.size), "little", signed=cls.signed)


class uint8_t(uint_t):
    size = 1


class BitsBase:
    sizeBits = 1

    def __init__(self, value: bool):
        self._value = bool(value)

    def __eq__(self, other):
        return self._value.__eq__(other)

    def __repr__(self):
        return "flags_t({})".format(self._value)

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        return stream.bits(cls.sizeBits)

    def serialize(self, stream: BitStreamWriter):
        stream.addBits(self._value, self.sizeBits)


class flag_t(BitsBase):
    def __bool__(self):
        return self._value


def bits_t(size):
    class bits_t(BitsBase):
        sizeBits = size

    return bits_t


def reserved_t(size):
    class reserved_t(BitsBase):
        default = 0
        sizeBits = size

    return reserved_t


class IPv6(ipaddress.IPv6Address):
    def serialize(self, stream: BitStreamWriter):
        stream.extend(self.packed)

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        return cls(stream.value(16))
