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

    def addBytes(self, value, size, signed):
        newVal = value.to_bytes(size, "little", signed=signed)
        self.extend(newVal)
        self._start = 0


class flag_t(type):
    sizeBits = 1


class int_t(int):
    signed = True
    size = 0

    def serialize(self, stream: BitStreamWriter):
        stream.addBytes(self, self.size, self.signed)


class uint_t(int_t):
    signed = False
    size = 1

    @classmethod
    def deseralize(cls, stream: BitStreamReader):
        return cls.from_bytes(stream.value(cls.size), "little", signed=cls.signed)


class uint8_t(uint_t):
    size = 1
