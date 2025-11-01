from datetime import datetime

from pydantic import BaseModel


# Corresponds to the flat structure of the DB model (models.py).
class BearSightingBase(BaseModel):
    prefecture: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    summary: str
    source_url: str
    image_url: str | None = None
    published_at: datetime


# Same as the base for now, but can be extended in the future.
class BearSightingCreate(BearSightingBase):
    pass


# Schema for returning data read from the DB (includes id).
class BearSightingRead(BearSightingBase):
    id: int

    class Config:
        # Enable automatic conversion from ORM (SQLAlchemy model) to Pydantic model.
        from_attributes = True
