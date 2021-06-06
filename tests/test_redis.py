import aioredis


async def test__redis_client__get_set(redis_client: aioredis.Redis) -> None:
    expected = "value"

    await redis_client.set("key", expected)
    real = await redis_client.get("key", encoding="utf-8")

    assert real == expected
