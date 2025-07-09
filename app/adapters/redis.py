import json
from typing import TypeVar, cast

import redis.asyncio
import redis.asyncio.sentinel

from app.config import config

from .logger import logger

T = TypeVar("T")  # Define a generic type


class RedisConnectionManager:
    """Redis Connection Manager."""

    def __init__(self, host: str, port: int, master_set: str) -> None:  # noqa: D107
        self.host = host
        self.port = port
        self.master_set = master_set
        self._connection: redis.asyncio.Redis | None = None

    async def initialize(self, *, use_local_redis: bool = False) -> None:
        """Connect to Redis."""
        if self._connection is None:
            if use_local_redis:
                logger.warning("😅 Using local redis. This should not happen in prod.")
                self._connection = redis.asyncio.Redis(host=self.host, port=self.port)
            else:
                sentinel_client = redis.asyncio.sentinel.Sentinel([(self.host, self.port)])
                self._connection = sentinel_client.master_for(self.master_set)
            await self._connection.echo("🎃 New redis connection CS")

    async def close(self) -> None:
        """Close the connection to Redis."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def get_connection(self) -> redis.asyncio.Redis:
        """Return the connection to Redis.

        Returns:
            redis.asyncio.Redis: The Redis connection instance.
        """
        if self._connection is None:
            await self.initialize(use_local_redis=config.USE_LOCAL_REDIS)
        return cast("redis.asyncio.Redis", self._connection)

    async def set_value(self, key: str, value: dict, expire: int | None = None) -> None:
        """Store a dictionary in Redis with an optional expiration time.

        Raises:
            ConnectionError: If Redis connection is closed.
        """
        if not self._connection:
            msg = "Failed to set value in Redis, when connection is closed."
            raise ConnectionError(msg)

        value_json = json.dumps(value)  # Convert dictionary to JSON string
        if expire:
            await self._connection.set(key, value_json, ex=expire)
        else:
            await self._connection.set(key, value_json)

    async def get_value(self, key: str, _type: type[T]) -> T | None:
        """Retrieve a dictionary from Redis.

        Returns:
            T | None: The retrieved value of type T, or None if not found.

        Raises:
            ConnectionError: If Redis connection is closed.
        """
        if not self._connection:
            msg = "Failed to set value in Redis, when connection is closed."
            raise ConnectionError(msg)

        value_json = await self._connection.get(key)
        if value_json:
            return json.loads(value_json)  # Convert JSON string back to dictionary
        return None

    async def set_val(self, *, key: str, value: int | str | bool, expire: int | None = None) -> None:
        """Store a value in Redis with an optional expiration time in seconds.

        Raises:
            ConnectionError: If Redis connection is closed.
        """
        if not self._connection:
            msg = "Failed to set value in Redis, when connection is closed."
            raise ConnectionError(msg)

        if expire:
            await self._connection.set(key, value, ex=expire)
        else:
            await self._connection.set(key, value)

    async def get_val(self, key: str) -> bytes | None:
        """Retrieve a value from Redis.

        Returns:
            bytes | None: The retrieved value as bytes, or None if not found.

        Raises:
            ConnectionError: If Redis connection is closed.
        """
        if not self._connection:
            msg = "Failed to get value from Redis, when connection is closed."
            raise ConnectionError(msg)

        cache_value = await self._connection.get(key)
        return cache_value or None
