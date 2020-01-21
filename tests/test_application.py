# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import pytest

from pyzwave.application import Application

from test_adaper import AdapterImpl


@pytest.fixture
def app() -> Application:
    return Application(AdapterImpl())


def test_nodes(app: Application):
    assert app.nodes == {}


@pytest.mark.asyncio
async def test_shutdown(app: Application):
    # Function not yet implemented. Update this function when it is
    assert await app.shutdown() is None


@pytest.mark.asyncio
async def test_startup(app: Application):
    async def getNodeList():
        return [1, 2, 3]

    app.adapter.getNodeList = getNodeList
    await app.startup()
    assert app.nodes == [1, 2, 3]
