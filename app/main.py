from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from app.config import ENV, REDIS_HOST, REDIS_PORT
from app.models import RootResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для жизненного цикла приложения
    При запуске создаёт подключение к redis
    При завершении приложения закрывает подключение к redis
    """
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )
    app.state.redis_client = redis_client
    await FastAPILimiter.init(redis_client)  # Подключаемся к Redis для лимита запросов

    yield

    await redis_client.close()
    await redis_client.wait_closed()


app = FastAPI(
    docs_url=None if ENV != 'test' else '/docs',
    redoc_url=None if ENV != 'test' else '/redoc',
    lifespan=lifespan
)

rate_limit = RateLimiter(times=10, seconds=60)


@app.get(
    '/',
    response_model=RootResponse,
    dependencies=[Depends(rate_limit)]
)
async def root() -> RootResponse:
    """
    Возвращает статус и версию сервиса
    """
    return RootResponse(status='OK', version='1.0')
