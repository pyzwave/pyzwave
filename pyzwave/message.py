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
            elif hasattr(attrType, "__setstate__"):
                self._attributes[attrName] = attrType()
                self._attributes[attrName].__setstate__(kwargs[attrName])
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

    def debugString(self, indent=0):
        """
        Convert all attributes in this message to a human readable string used for debug output.
        """
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(self.__class__, (0, 0))

        attrs = []
        for name, _ in self.attributes:
            if name not in self._attributes:
                continue
            if hasattr(self._attributes[name], "debugString"):
                value = self._attributes[name].debugString(indent + 1)
            else:
                value = repr(self._attributes[name])
            attrs.append("{}{} = {}".format("\t" * (indent + 1), name, value))

        cmdClassName = cmdClasses.get(cmdClass, "cmdClass 0x{:02X}".format(cmdClass))
        name = self.NAME or "0x{:02X}".format(cmd)
        return "{}.{}:\n{}".format(cmdClassName, name, "\n".join(attrs))

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

    def __eq__(self, other):
        return self.compose() == other.compose()

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
        hid = self.hid()
        cmdClass = (hid >> 8) & 0xFF
        cmd = hid & 0xFF
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
        MsgCls = ZWaveMessage.get(hid, None)  # pylint: disable=invalid-name
        if MsgCls:
            msg = MsgCls()
            msg.parse(stream)
        else:
            msg = UnknownMessage(hid)
        return msg

    @classmethod
    def hid(cls):
        """
        Return the command class id and command id as a single word for easier lookup
        """
        cmdClass, cmd = ZWaveMessage.reverseMapping.get(cls, (0, 0))
        return (cmdClass << 8) | (cmd & 0xFF)


class UnknownMessage(Message):
    """
    Wrapper class for wrapping unknown messages. Using this class we still know which
    command class and command this message is (but we don't know how to decode it)
    """

    def __init__(self, hid):
        super().__init__()
        self._hid = hid

    def hid(self):
        return self._hid


# pylint: disable=wrong-import-position
from pyzwave.commandclass import ZWaveMessage, cmdClasses
