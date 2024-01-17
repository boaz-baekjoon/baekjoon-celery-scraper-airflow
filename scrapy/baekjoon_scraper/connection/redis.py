import redis.asyncio as aioredis
import logging
from config.config import Config


class RedisDB:
    _REDIS_HOST = Config.REDIS_HOST
    _REDIS_PORT = int(Config.REDIS_PORT)
    _REDIS_DB = 0

    def __init__(self):
        self.client = None

    async def connect(self):
        try:
            self.client = aioredis.Redis(
                host=self._REDIS_HOST,
                port=self._REDIS_PORT,
                db=self._REDIS_DB,
                encoding="utf-8",
                decode_responses=True
            )
            # Redis 서버에 PING 명령을 보내 응답을 확인합니다.
            await self.client.ping()
            logging.info("Redis Connected.")
        except Exception as e:
            logging.error(f"Redis failed to connect: {e}")

    async def close(self):
        if self.client:
            await self.client.close()
            logging.info("Redis 커넥션 종료.")

    async def set(self, key: str, value: str):
        await self.client.set(key, value)

    async def get(self, key: str):
        return await self.client.get(key)

    async def lpush(self, key: str, value: str):
        await self.client.lpush(key, value)

    async def expire(self, key: str, time: int):
        await self.client.expire(key, time)

    async def delete(self, key: str):
        await self.client.delete(key)

    def pubsub(self):
        return self.client.pubsub()

    async def publish(self, channel: str, message: str):
        await self.client.publish(channel, message)

    async def get_all_session_keys(self):
        """Retrieve all session keys."""
        if self.client is None:
            raise Exception("Redis client is not connected")
        return await self.client.keys("user:session:*")


# Redis 디비 싱글톤 패턴
redis_client = RedisDB()
