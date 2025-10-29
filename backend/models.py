from sqlalchemy import Column, DateTime, Float, Integer, String

from database import Base


class BearSighting(Base):
    """
    クマ出没情報のデータベーステーブル定義
    """

    # テーブル名
    __tablename__ = "bear_sightings"

    # --- カラム定義 ---

    # ID (自動採番)
    id = Column(Integer, primary_key=True, index=True)

    # 場所 (LLMによる抽出)
    prefecture = Column(String, index=True)
    city = Column(String, index=True)

    # 緯度・経度 (Geocodingによる特定)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # 概要 (LLMによる要約)
    summary = Column(String)

    # newsapiからの元データ
    source_url = Column(String, unique=True, index=True)
    image_url = Column(String, nullable=True)
    published_at = Column(DateTime, index=True)
