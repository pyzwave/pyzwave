# -*- coding: utf-8 -*-

import asyncio
import inspect
import logging
from typing import Dict, Any

from pyzwave.types import BitStreamReader

_LOGGER = logging.getLogger(__name__)


class AttributesMixin:
    """Inheritable class to implement defined attributes"""

    attributes = ()

    def __init__(self, **kwargs):
        super().__init__()
        self._attributes = {}
        for attr in getattr(self, "attributes"):
            attrName, attrType = attr[0], attr[1]
            if attrName not in kwargs:
                continue
            value = kwargs[attrName]
            if isinstance(value, AttributesMixin):
                # Is a subclass of ourself, not not wrap it
                self._attributes[attrName] = value
            elif hasattr(attrType, "__setstate__"):
                self._attributes[attrName] = attrType()
                self._attributes[attrName].__setstate__(value)
            else:
                self._attributes[attrName] = attrType(value)

    def attributeUpdated(self, name, newValue, oldValue):
        """Called if an attribute value was updated"""

    def debugString(self, indent=0):
        """
        Convert all attributes in this object to a human readable string used for debug output.
        """
        attrs = []
        for attr in self.attributes:
            attrName = attr[0]
            if attrName not in self._attributes:
                continue
            if hasattr(self._attributes[attrName], "debugString"):
                value = self._attributes[attrName].debugString(indent + 1)
            else:
                value = repr(self._attributes[attrName])
            attrs.append("{}{} = {}".format("\t" * (indent + 1), attrName, value))
        return "{}:\n{}".format(str(self), "\n".join(attrs))

    def parseAttributes(self, stream: BitStreamReader):
        """Populate the attributes from a raw bitstream."""
        for attr in self.attributes:
            if stream.bytesLeft() == 0:
                # No more data, cannot decode rest of the attributes
                break
            attrName, attrType = attr[0], attr[1]
            deserializer = getattr(self, "parse_{}".format(attrName), None)
            if deserializer:
                value = deserializer(stream)
            else:
                value = attrType.deserialize(stream)
            # This can be optimized to reduce the second loop in __setattr__
            setattr(self, attrName, value)

    def __getattr__(self, name):
        if name not in self._attributes:
            # Try to load default
            for attrName, attrType in getattr(self, "attributes"):
                if attrName != name:
                    continue
                attr = attrType()
                self._attributes[name] = attr
                return attr
        return self._attributes.get(name)

    def __getstate__(self) -> Dict[str, Any]:
        values = {}
        for attr, value in self._attributes.items():
            if hasattr(value, "__getstate__"):
                values[attr] = value.__getstate__()
            else:
                values[attr] = value
        return values

    def __setattr__(self, name, value):
        for attr in getattr(self, "attributes"):
            attrName, attrType = attr[0], attr[1]
            if attrName == name:
                oldValue = self._attributes.get(name, None)
                if isinstance(value, attrType):
                    # Correct type set, use it directly
                    newValue = value
                elif hasattr(attrType, "__setstate__"):
                    newValue = attrType()
                    newValue.__setstate__(value)
                elif isinstance(value, tuple):
                    newValue = attrType(*value)
                else:
                    newValue = attrType(value)
                if oldValue == newValue:
                    return
                self._attributes[name] = newValue
                self.attributeUpdated(name, newValue, oldValue)
                return
        super().__setattr__(name, value)

    def __setstate__(self, state):
        for attrName, attrType in getattr(self, "attributes"):
            if attrName not in state:
                continue
            if hasattr(attrType, "__setstate__"):
                value = attrType()
                value.__setstate__(state[attrName])
            else:
                value = attrType(state[attrName])
            self._attributes[attrName] = value


class Listenable:
    """Inheritable class to implement listaner interface between classes"""

    def __init__(self):
        super().__init__()
        self._listeners = []

    def addListener(self, listener):
        """Add class as listener for messages"""
        self._listeners.append(listener)

    async def ask(self, message, *args) -> list:
        """
        Send message to listeners and wait for the listeners to respond.
        This a shorthand for awaiting thre result from speak()
        """
        return await asyncio.gather(*self.speak(message, *args))

    def speak(self, message, *args) -> list:
        """
        Send message to listeners.
        Returns a list of futures if the listeners are async. This can be used to allow waiting
        for all listeners to finish before continue.
        """
        retval = []
        for listener in self._listeners:
            method = getattr(listener, message, None)
            if not method:
                continue
            if inspect.iscoroutinefunction(method):
                # Listener is a coroutine, call async
                retval.append(asyncio.ensure_future(method(self, *args)))
                continue
            try:
                future = asyncio.get_event_loop().create_future()
                future.set_result(method(self, *args))
                retval.append(future)
            except Exception as error:
                _LOGGER.warning("Error calling listener.%s: %s", message, error)
        return retval


class MessageWaiter:
    """Inheritable class to implement listening for specific messages"""

    def __init__(self):
        super().__init__()
        self._sessions = {}

    def addWaitingSession(self, msgType):
        """
        Setup the session to wait for _before_ doing the wait. Do this to avoid
        a race condition where the message is received before we wait for it
        """
        hid = msgType.hid()
        session = self._sessions.get(hid, None)
        if not session:
            session = asyncio.get_event_loop().create_future()
            self._sessions[hid] = session
        return session

    def messageReceived(self, message) -> bool:
        """Called when a message is received directed to this node"""
        session = self._sessions.pop(message.hid(), None)
        if session:
            session.set_result(message)
            return True
        return False

    async def waitForMessage(self, msgType, timeout: int = 3, session=None):
        """Async method for waiting for a specific message to arrive from the node."""
        if not session:
            session = self.addWaitingSession(msgType)
        try:
            await asyncio.wait_for(session, timeout)
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout waiting for message %s", msgType)
            raise
        finally:
            self._sessions.pop(msgType.hid(), None)
        return session.result()
