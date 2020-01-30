# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import pytest

from pyzwave.application import Application
from pyzwave.commandclass import Basic, NetworkManagementProxy
from pyzwave.node import Node

from test_adaper import AdapterImpl


@pytest.fixture
def app() -> Application:
    adapter = AdapterImpl()
    app = Application(adapter)
    app._nodes = {3: Node(3, adapter, [])}
    return app


def test_messageReceived(app: Application):
    assert app.messageReceived(None, 4, Basic.Report(value=0), 0) is False
    assert app.messageReceived(None, 3, Basic.Report(value=0), 0) is True


def test_nodes(app: Application):
    assert app.nodes.keys() == {3}


def test_setNodeInfo(app: Application):
    # Not implemented yet
    app.setNodeInfo(0, 0, [])


@pytest.mark.asyncio
async def test_shutdown(app: Application):
    # Function not yet implemented. Update this function when it is
    assert await app.shutdown() is None


@pytest.mark.asyncio
async def test_startup(app: Application):
    async def getFailedNodeList():
        return [2]

    async def getNodeInfo(_):
        return NetworkManagementProxy.NodeInfoCachedReport(commandClass=b"")

    async def getNodeList():
        return [1, 2, 3]

    app.adapter.getFailedNodeList = getFailedNodeList
    app.adapter.getNodeInfo = getNodeInfo
    app.adapter.getNodeList = getNodeList
    await app.startup()
    assert app.nodes.keys() == {1, 2, 3}
