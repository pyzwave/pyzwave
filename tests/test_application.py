import asyncio
import pytest

from pyzwave.adapter import Adapter
from pyzwave.application import Application


@pytest.fixture
def app():
    return Application(Adapter())


def test_nodes(app: Application):
    assert app.nodes == {}


@pytest.mark.asyncio
async def test_shutdown(app: Application):
    # Function not yet implemented. Update this function when it is
    assert await app.shutdown() == None


@pytest.mark.asyncio
async def test_startup(app: Application):
    async def getNodeList():
        return [1, 2, 3]

    app.adapter.getNodeList = getNodeList
    await app.startup()
    assert app.nodes == [1, 2, 3]
