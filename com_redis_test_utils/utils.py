import asyncio
from contextlib import asynccontextmanager, contextmanager
from typing import Iterator

import aioredis
import docker


@contextmanager
def up_redis_container(host: str, port: int) -> Iterator[None]:
    docker_client = docker.from_env()

    container = docker_client.containers.run(
        image="redis:6-alpine",
        detach=True,
        ports={
            "6379/tcp": (host, port),
        },
    )
    try:
        yield
    finally:
        container.remove(force=True)
        docker_client.close()


@asynccontextmanager
async def redis_client_factory(address: str) -> aioredis.Redis:
    redis = await aioredis.create_redis_pool(address, minsize=0)
    await _wait_redis_setup(redis)
    try:
        yield redis
    finally:
        await redis.flushall()
        redis.close()
        await redis.wait_closed()


async def _wait_redis_setup(redis: aioredis.Redis) -> None:
    for _ in range(50):
        try:
            await redis.ping()
        except (ConnectionError, aioredis.ConnectionClosedError):
            await asyncio.sleep(0.05)
        else:
            return
    raise RuntimeError("Could not connect to the Redis")
