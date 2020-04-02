from typing import Any, Dict

from sphinx.application import Sphinx
from pyzwave.util import AttributesMixin
from pyzwave.types import reserved_t


def resolveAttributes(
    _app: Sphinx,
    objtype: str,
    _name: str,
    obj: Any,
    _options: Dict,
    _signature: str,
    retann: str,
) -> None:
    """Rewrite the object constructor to include the attributes"""
    if objtype != "class":
        return
    if not issubclass(obj, AttributesMixin):
        return

    attrs = []
    for attr in obj.attributes:
        attrType = attr[1]
        if issubclass(attrType, reserved_t(0)):
            continue
        attrs.append(attr[0])

    return ("({})".format(", ".join(attrs)), retann)


def setup(app):
    """Setup the attributesMixin documentation helper plugin"""
    app.connect("autodoc-process-signature", resolveAttributes)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
