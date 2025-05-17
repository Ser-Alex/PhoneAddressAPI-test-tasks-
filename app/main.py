import logging
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter


from app.config import ENV, REDIS_HOST, REDIS_PORT
from app.models import RootResponse, WriteDataRequest


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для жизненного цикла приложения
    При запуске создаёт подключение к redis
    При завершении приложения закрывает подключение к redis
    """
    logger.info("Starting up application")
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )
    app.state.redis_client = redis_client
    await FastAPILimiter.init(redis_client)  # Подключаемся к Redis для лимита запросов
    logger.info("Redis connection established and rate limiter initialized.")

    yield

    await redis_client.close()
    await redis_client.wait_closed()
    logger.info("Redis connection closed successfully.")


app = FastAPI(
    docs_url=None if ENV != 'test' else '/docs',
    redoc_url=None if ENV != 'test' else '/redoc',
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware для логирования HTTP-запросов и ответов
    """
    logger.info(f"Incoming request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"Unhandled error: {e}")
        raise

    logger.info(f"Response status: {response.status_code}")
    return response


rate_limit = RateLimiter(times=10, seconds=60)  # ограничение - не более 10 запросов в 60 секунд



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


@app.post('/write_data', dependencies=[Depends(rate_limit)])
async def post_write_data(
        data: WriteDataRequest,
        request: Request
):
    """
    Сохраняет или обновляет адрес по номеру телефона в redis
    """
    redis_client = request.app.state.redis_client
    await redis_client.set(data.phone, data.address)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Данные успешно сохранены"}
    )


@app.get(
    '/write_data',
    response_model=WriteDataRequest,
    dependencies=[Depends(rate_limit)]
)
async def get_write_data(phone: str, request: Request):
    """
    Получает адрес по номеру телефона из redis
    """
    redis_client = request.app.state.redis_client
    address = await redis_client.get(phone)
    if address is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Данные не найдены"}
        )
    return WriteDataRequest(phone=phone, address=address)
