import aioredis


async def test__com_redis_client__get_set(
    com_redis_client: aioredis.Redis,
) -> None:
    expected = "value"
    await com_redis_client.set("key", expected)

    assert await com_redis_client.get("key", encoding="utf-8") == expected
