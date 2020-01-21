import logging

from pyzwave.types import BitStreamReader, BitStreamWriter

_LOGGER = logging.getLogger(__name__)


class Message:
    """Base class for all Z-Wave messages. This class should not be initiated manually"""

    NAME = None
    attributes = ()

    def __init__(self, **kwargs):
        self._attributes = {}
        for attrName, attrType in getattr(self, "attributes"):
            if attrName not in kwargs:
                continue
            if kwargs[attrName] is None:
                # Try to create default value
                self._attributes[attrName] = attrType()
            elif issubclass(attrType, Message):
                self._attributes[attrName] = kwargs[attrName]
            else:
                self._attributes[attrName] = attrType(kwargs[attrName])

    def compose(self) -> bytes:
        """Convert the message to a bytearray ready to be sent over the wire"""
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(self.__class__, (None, None))
        if cmdClass is None or cmd is None:
            # Pure Message object, encode to empty bytes
            return b""
        stream = BitStreamWriter()
        stream.addBytes(cmdClass, 1, False)
        stream.addBytes(cmd, 1, False)
        for name, attrType in self.attributes:
            if name not in self._attributes:
                default = getattr(attrType, "default", None)
                if default is not None:
                    attrType(default).serialize(stream)
                    continue
                raise AttributeError(
                    "Value for attribute '{}' in {} has not been set".format(name, self)
                )
            if not hasattr(self._attributes[name], "serialize"):
                raise ValueError("Cannot encode", name, self._attributes[name])
            self._attributes[name].serialize(stream)
        return bytes(stream)

    def parse(self, stream: BitStreamReader):
        """Populate the attributes from a raw bitstream."""
        for name, attrType in self.attributes:
            serializer = getattr(self, "parse_{}".format(name), None)
            if serializer:
                value = serializer(stream)
            else:
                value = attrType.deserialize(stream)
            # This can be optimized to reduze the second loop in __setattr__
            setattr(self, name, value)

    def serialize(self, stream: BitStreamWriter):
        """Write the message as binary into the bitstream. See compose()"""
        stream.extend(self.compose())

    def __getattr__(self, name):
        return self._attributes.get(name)

    def __setattr__(self, name, value):
        for msgAttrName, attrType in getattr(self, "attributes"):
            if isinstance(value, Message):
                self._attributes[name] = value
                return
            if msgAttrName == name:
                self._attributes[name] = attrType(value)
                return
        super().__setattr__(name, value)

    def __repr__(self):
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(self.__class__, (0, 0))
        cmdClassName = cmdClasses.get(cmdClass, "cmdClass 0x{:02X}".format(cmdClass))
        name = self.NAME or "0x{:02X}".format(cmd)
        return "<Z-Wave {} cmd {}>".format(cmdClassName, name)

    @classmethod
    def decode(cls, pkt: bytearray):
        """Decode a raw bytearray into a Message object"""
        return cls.deserialize(BitStreamReader(pkt))

    @staticmethod
    def deserialize(stream: BitStreamReader):
        """Deserialize a bitstream into a Message object"""
        cmdClass = stream.byte()
        cmd = stream.byte()
        hid = cmdClass << 8 | (cmd & 0xFF)
        MsgCls = ZWaveMessage.get(hid, Message)  # pylint: disable=invalid-name
        msg = MsgCls()
        msg.parse(stream)
        return msg

    @classmethod
    def hid(cls):
        """
        Return the command class id and command id as a single word for easier lookup
        """
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(cls, (0, 0))
        return (cmdClass << 8) | (cmd & 0xFF)


# pylint: disable=wrong-import-position
from pyzwave.commandclass import ZWaveMessage, cmdClasses
