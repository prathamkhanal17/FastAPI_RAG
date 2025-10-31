import redis.asyncio as redis
import json
import uuid

class RedisMemory:
    def __init__(self, redis_client: redis.Redis, ttl_seconds: int = 86400 * 7):
        self.redis = redis_client
        self.ttl = ttl_seconds

    def _key(self, conv_id: str):
        return f"conv:{conv_id}"

    async def create_conversation_id(self) -> str:
        return str(uuid.uuid4())

    async def append_message(self, conv_id: str, role: str, text: str):
        entry = json.dumps({"role": role, "text": text})
        await self.redis.rpush(self._key(conv_id), entry)
        await self.redis.expire(self._key(conv_id), self.ttl)

    async def get_messages(self, conv_id: str):
        data = await self.redis.lrange(self._key(conv_id), 0, -1)
        return [json.loads(d) for d in data] if data else []

    async def clear(self, conv_id: str):
        await self.redis.delete(self._key(conv_id))


async def get_redis_memory(redis_url: str = "redis://localhost:6379/0") -> RedisMemory:
    r = redis.from_url(redis_url, decode_responses=True)
    return RedisMemory(r)
