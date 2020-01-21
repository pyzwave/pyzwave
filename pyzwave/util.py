# -*- coding: utf-8 -*-

import logging

_LOGGER = logging.getLogger(__name__)


class Listenable:
    """Inheritable class to implement listaner interface between classes"""

    def __init__(self):
        self._listeners = []

    def addListener(self, listener):
        """Add class as listener for messages"""
        self._listeners.append(listener)

    def speak(self, message, *args):
        """Send message to listeners"""
        for listener in self._listeners:
            method = getattr(listener, message, None)
            if not method:
                continue
            try:
                method(self, *args)
            except Exception as error:
                _LOGGER.warning("Error calling listener.%s: %s", message, error)
