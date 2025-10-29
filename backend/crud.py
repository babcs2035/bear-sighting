from sqlalchemy.orm import Session

import models
import schemas


# -------------------------------------------------
# CREATE (作成)
# -------------------------------------------------
def create_sighting(db: Session, sighting: schemas.BearSightingCreate) -> models.BearSighting:
    """
    クマの出没情報（Pydanticスキーマ）を受け取り、
    DBモデルに変換してデータベースに保存する
    """

    # Pydanticモデル (.model_dump()) から SQLAlchemyモデル (models.BearSighting) を作成
    db_sighting = models.BearSighting(**sighting.model_dump())

    db.add(db_sighting)  # DBセッションに追加
    db.commit()  # データベースにコミット (書き込み)
    db.refresh(db_sighting)  # DBから最新の状態 (自動採番されたidなど) を取得

    return db_sighting


# -------------------------------------------------
# READ (読み取り)
# -------------------------------------------------
def get_sighting_by_url(db: Session, source_url: str) -> models.BearSighting | None:
    """
    情報源のURLをキーに、出没情報を1件取得する
    (重複登録を防ぐために使用)
    """
    return db.query(models.BearSighting).filter(models.BearSighting.source_url == source_url).first()


def get_sightings(db: Session) -> list[models.BearSighting]:
    """
    出没情報の一覧を取得する (ページネーション対応)
    """
    return db.query(models.BearSighting).all()
