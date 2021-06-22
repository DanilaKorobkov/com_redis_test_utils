# pylint: disable=redefined-outer-name, unused-argument

import asyncio
from typing import AsyncIterator, Final, Iterator

import aioredis
import pytest
from aiohttp.test_utils import unused_port
from yarl import URL

from .utils import (
    RedisConfig,
    redis_client_upped,
    redis_docker_container_upped,
)

pytest_plugins: Final = ("aiohttp.pytest_plugin",)


@pytest.fixture(scope="session")
def com_redis_config() -> RedisConfig:
    return RedisConfig(
        host="127.0.0.1",
        port=unused_port(),
        min_size=1,
        max_size=1,
    )


@pytest.fixture(scope="session")
def com_redis_url(com_redis_config: RedisConfig) -> Iterator[URL]:
    with redis_docker_container_upped(com_redis_config):
        yield com_redis_config.get_url()


@pytest.fixture
async def com_redis_client(
    com_redis_url: URL,
    com_redis_config: RedisConfig,
    loop: asyncio.AbstractEventLoop,
) -> AsyncIterator[aioredis.Redis]:
    assert loop.is_running()

    async with redis_client_upped(com_redis_config) as redis:
        yield redis
