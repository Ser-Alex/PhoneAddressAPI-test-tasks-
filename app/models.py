from pydantic import BaseModel


class RootResponse(BaseModel):
    """
    Модель ответа для корневого эндпоинта API ('/')
    """
    status: str
    version: str
