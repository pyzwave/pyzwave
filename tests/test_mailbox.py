# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import asyncio
import ipaddress

from unittest.mock import patch, MagicMock

import pytest

from pyzwave.commandclass import Mailbox
from pyzwave.mailbox import MailboxService, QueueItem
from test_adaper import AdapterImpl

sleep = asyncio.sleep


class AsyncMock(MagicMock):
    # pylint: disable=useless-super-delegation
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class SleepMock(MagicMock):
    # pylint: disable=arguments-differ
    async def __call__(self, time):
        return await sleep(0)


@pytest.fixture
def mailbox() -> MailboxService:
    adapter = AdapterImpl()
    adapter.send = AsyncMock(return_value=True)
    adapter.sendToNode = AsyncMock(return_value=True)
    return MailboxService(adapter)


@pytest.mark.asyncio
async def test_initialize(mailbox: MailboxService):
    assert (
        await mailbox.initialize(ipaddress.IPv6Address("::ffff:c0a8:31"), 4123) is True
    )


@pytest.mark.asyncio
async def test_popQueue(mailbox: MailboxService):
    assert await mailbox.__pushQueue__(1, 3, b"hello") is True
    mailbox._adapter.sendToNode.reset_mock()

    assert await mailbox.__popQueue__(1, 3) is True
    mailbox._adapter.sendToNode.assert_called_once_with(
        1,
        Mailbox.Queue(
            last=True,
            operation=Mailbox.Queue.Operation.POP,
            queueHandle=3,
            mailboxEntry=b"hello",
        ),
    )


@pytest.mark.asyncio
async def test_messageReceived_QueueAck(mailbox: MailboxService):
    assert (
        await mailbox.messageReceived(
            None,
            1,
            0,
            Mailbox.Queue(
                last=False, operation=Mailbox.Queue.Operation.ACK, queueHandle=42
            ),
            0,
        )
        is True
    )


@pytest.mark.asyncio
async def test_messageReceived_QueuePush(mailbox: MailboxService):
    assert (
        await mailbox.messageReceived(
            None,
            1,
            0,
            Mailbox.Queue(
                last=False,
                operation=Mailbox.Queue.Operation.PUSH,
                queueHandle=42,
                mailboxEntry=b"hello",
            ),
            0,
        )
        is True
    )
    mailbox._adapter.sendToNode.assert_called_once_with(
        1,
        Mailbox.Queue(
            last=False,
            operation=Mailbox.Queue.Operation.WAITING,
            queueHandle=42,
            mailboxEntry=b"hello",
        ),
    )


@pytest.mark.asyncio
async def test_messageReceived_WakeupNotification(mailbox: MailboxService):
    assert mailbox._lastQueueId is None
    assert (
        await mailbox.messageReceived(
            None, 1, 0, Mailbox.WakeupNotification(queueHandle=42), 0
        )
        is True
    )
    assert mailbox._lastQueueId == 42


@pytest.mark.asyncio
async def test_popQueue_empty(mailbox: MailboxService):
    assert await mailbox.__popQueue__(1, 3) is True
    mailbox._adapter.sendToNode.assert_called_once_with(
        1,
        Mailbox.Queue(last=True, operation=Mailbox.Queue.Operation.POP, queueHandle=3,),
    )


@pytest.mark.asyncio
async def test_pushQueue(mailbox: MailboxService):
    assert len(mailbox._queue) == 0
    assert await mailbox.__pushQueue__(1, 3, b"hello") is True
    assert len(mailbox._queue[3]) == 1

    # Adding the same message again should be discarded
    assert await mailbox.__pushQueue__(1, 3, b"hello") is False
    assert len(mailbox._queue[3]) == 1


@pytest.mark.asyncio
async def test_QueueItem_runner(mailbox: MailboxService):
    async def runner():
        with patch("asyncio.sleep", new_callable=SleepMock):
            queueItem = QueueItem(1, 2, b"hello", mailbox._adapter)
            await queueItem._runner()

    task = asyncio.ensure_future(runner())

    await sleep(0)
    # Make sure the first 9 minutes it's sending waiting messages
    for _ in range(9):
        mailbox._adapter.sendToNode.reset_mock()
        await sleep(0)
        mailbox._adapter.sendToNode.assert_called_once_with(
            1,
            Mailbox.Queue(
                last=False,
                operation=Mailbox.Queue.Operation.WAITING,
                queueHandle=2,
                mailboxEntry=b"hello",
            ),
        )
    # After 10 minutes there should be a ping instead
    mailbox._adapter.sendToNode.reset_mock()
    await sleep(0)
    mailbox._adapter.sendToNode.assert_called_once_with(
        1,
        Mailbox.Queue(
            last=False,
            operation=Mailbox.Queue.Operation.PING,
            queueHandle=2,
            mailboxEntry=b"hello",
        ),
    )
    task.cancel()
