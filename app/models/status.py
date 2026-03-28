from pydantic import BaseModel


class UpdateStatusRequest(BaseModel):
    status: str
    resolution_note: str | None = None
