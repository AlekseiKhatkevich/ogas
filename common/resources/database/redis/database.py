from contextlib import aclosing, asynccontextmanager
from typing import Iterable, Protocol

import redis.asyncio as redis
from dishka import Provider, Scope, make_container, provide
from redis.asyncio.client import Redis

from common import settings

__al__ = (
    'redis_container',
    'RedisDAO',
)


class RedisDAO(Protocol):
    pass


class RedisDAOImpl(RedisDAO):
    def __init__(self, client: Redis):
        self.client = client

    @property
    @asynccontextmanager
    async def connection(self):
        async with aclosing(self.client) as conn:
            yield conn


service_provider = Provider(scope=Scope.APP)
service_provider.provide(RedisDAOImpl, provides=RedisDAO)


class ClientProvider(Provider):
    @provide(scope=Scope.APP)
    def new_client(self) -> Iterable[Redis]:
        client = redis.from_url(settings.REDIS_DSN.unicode_string())
        yield client
        client.close()


redis_container = make_container(service_provider, ClientProvider())
