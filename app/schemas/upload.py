from pydantic import BaseModel


class UploadOut(BaseModel):
    id: str
    url: str
    mime: str
    size: int
