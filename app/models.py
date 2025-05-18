from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    """
    Модель ответа для корневого эндпоинта API ('/')
    """
    status: str
    version: str


class DataRequest(BaseModel):
    """
    Модель для запроса записи или обновления данных
    по номеру телефона и адресу
    """
    phone: str = Field(..., example="89090000000")
    address: str = Field(..., example="г. Москва, ул. Примерная, д. 1")
