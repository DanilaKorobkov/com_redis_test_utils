import asyncio
from contextlib import asynccontextmanager, contextmanager
from typing import Iterator

import aioredis
import attr
import docker
from yarl import URL


@attr.s(auto_attribs=True, slots=True, frozen=True)
class RedisConfig:
    host: str
    port: int
    min_size: int
    max_size: int

    def get_url(self) -> URL:
        return URL.build(
            scheme="redis",
            host=self.host,
            port=self.port,
        )


@contextmanager
def redis_docker_container_upped(config: RedisConfig) -> Iterator[None]:
    docker_client = docker.from_env()

    container = docker_client.containers.run(
        image="redis:6-alpine",
        detach=True,
        ports={
            "6379/tcp": (config.host, config.port),
        },
    )
    try:
        yield
    finally:
        container.remove(force=True)
        docker_client.close()


@asynccontextmanager
async def redis_client_upped(config: RedisConfig) -> aioredis.Redis:
    redis = await _wait_redis_setup(config)
    try:
        yield redis
    finally:
        await redis.flushall()
        redis.close()
        await redis.wait_closed()


async def _wait_redis_setup(config: RedisConfig) -> aioredis.Redis:
    for _ in range(50):
        try:
            redis = await aioredis.create_redis_pool(
                address=str(config.get_url()),
                minsize=config.min_size,
                maxsize=config.max_size,
                encoding="utf-8",
            )
            await redis.ping()
        except (ConnectionError, aioredis.ConnectionClosedError):
            await asyncio.sleep(0.05)
        else:
            return redis
    raise RuntimeError("Could not connect to the Redis")
