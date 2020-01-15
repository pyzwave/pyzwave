# -*- coding: utf-8 -*-

import logging

_LOGGER = logging.getLogger(__name__)


class Application:
    def __init__(self, adapter):
        self.adapter = adapter
        self.adapter.addListener(self)
        self._nodes = {}

    @property
    def nodes(self):
        return self._nodes

    async def shutdown(self):
        pass

    async def startup(self):
        self._nodes = await self.adapter.getNodeList()
        _LOGGER.debug("Got nodelist %s", self._nodes)
