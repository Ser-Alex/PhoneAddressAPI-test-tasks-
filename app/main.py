from fastapi import FastAPI

from app.config import ENV
from app.models import RootResponse

app = FastAPI(
    docs_url=None if ENV != 'test' else '/docs',
    redoc_url=None if ENV != 'test' else '/redoc'
)


@app.get('/', response_model=RootResponse)
async def root() -> RootResponse:
    """
    Возвращает статус и версию сервиса
    """
    return RootResponse(status='OK', version='1.0')
