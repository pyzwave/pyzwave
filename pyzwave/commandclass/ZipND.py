from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_ZIP_ND,
    ZIP_INV_NODE_SOLICITATION,
    ZIP_NODE_ADVERTISEMENT,
)
from pyzwave.message import Message
from pyzwave.types import (
    bits_t,
    flag_t,
    HomeID,
    IPv6,
    reserved_t,
    uint8_t,
)
from . import ZWaveMessage, registerCmdClass

registerCmdClass(COMMAND_CLASS_ZIP_ND, "ZIP_ND")


@ZWaveMessage(COMMAND_CLASS_ZIP_ND, ZIP_INV_NODE_SOLICITATION)
class ZipInvNodeSolicitation(Message):
    """
    Command Class Message COMMAND_CLASS_ZIP_ND ZIP_INV_NODE_SOLICITATION
    """

    NAME = "ZIP_INV_NODE_SOLICITATION"
    attributes = (
        ("-", reserved_t(4)),
        ("local", flag_t),
        ("-", reserved_t(3)),
        ("nodeId", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_ZIP_ND, ZIP_NODE_ADVERTISEMENT)
class ZipNodeAdvertisement(Message):
    """
    Command Class message COMMAND_CLASS_ZIP_ND ZIP_NODE_ADVERTISEMENT
    """

    NAME = "ZIP_NODE_ADVERTISEMENT"

    attributes = (
        ("-", reserved_t(5)),
        ("local", flag_t),
        ("validity", bits_t(2)),
        ("nodeId", uint8_t),
        ("ipv6", IPv6),
        ("homeId", HomeID),
    )
