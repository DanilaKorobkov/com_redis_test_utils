# pylint: disable=redefined-outer-name

import asyncio
from typing import AsyncIterator, Final, Iterator

import aioredis
import pytest
from aiohttp.test_utils import unused_port

from .utils import redis_client_factory, up_redis_container

pytest_plugins: Final = ("aiohttp.pytest_plugin",)


@pytest.fixture(scope="session")
def com_redis_url() -> Iterator[str]:
    host, port = "127.0.0.1", unused_port()
    with up_redis_container(host, port):
        yield f"redis://{host}:{port}"


@pytest.fixture
async def com_redis_client(
    com_redis_url: str,
    loop: asyncio.AbstractEventLoop,
) -> AsyncIterator[aioredis.Redis]:
    assert loop.is_running()

    async with redis_client_factory(com_redis_url) as redis:
        yield redis
