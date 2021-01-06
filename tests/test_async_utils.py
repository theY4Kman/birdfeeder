import asyncio

import pytest

from birdfeeder import async_utils


async def ok_coroutine():
    await asyncio.sleep(0)


async def bad_coroutine():
    raise RuntimeError("boom")


def test_should_inspect():
    assert async_utils.SHOULD_INSPECT is False


def test_get_callers():
    callers = async_utils.get_callers()
    assert isinstance(callers, list)
    assert callers[0][1] == 'test_async_utils'
    assert callers[0][2] == 'test_get_callers'


@pytest.mark.asyncio
async def test_safe_ensure_future_1():
    await async_utils.safe_ensure_future(ok_coroutine())


@pytest.mark.asyncio
async def test_safe_ensure_future_2():
    async_utils.SHOULD_INSPECT = True
    # Should log unhandled exception with callers
    await async_utils.safe_ensure_future(bad_coroutine())


@pytest.mark.asyncio
async def test_safe_gather_1():
    await async_utils.safe_gather(ok_coroutine())


@pytest.mark.asyncio
async def test_safe_gather_2():
    with pytest.raises(RuntimeError, match="boom"):
        await async_utils.safe_gather(bad_coroutine())


@pytest.mark.asyncio
async def test_wait_til_next_tick():
    await async_utils.wait_til_next_tick(seconds=0.001)
