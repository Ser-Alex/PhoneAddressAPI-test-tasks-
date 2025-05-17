from pydantic import BaseModel


class RootResponse(BaseModel):
    status: str
    version: str
