from datetime import datetime

from pydantic import BaseModel


# DBモデル (models.py) のフラットな構造に対応
class BearSightingBase(BaseModel):
    prefecture: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    summary: str
    source_url: str
    image_url: str | None = None
    published_at: datetime


# 今はベースと同じだが、将来的に分割可能
class BearSightingCreate(BearSightingBase):
    pass


# DBから読み取ったデータ (idを含む) を返すためのスキーマ
class BearSightingRead(BearSightingBase):
    id: int

    class Config:
        # ORM (SQLAlchemyモデル) から Pydanticモデルへの自動変換を有効化
        from_attributes = True
