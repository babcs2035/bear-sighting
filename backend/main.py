import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

import crud
import database
import models
import schemas

load_dotenv()

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="クマ出没情報 API (Bear Sighting API)", version="0.1.0", root_path="/bear-sighting-api")


@app.get("/")
def read_root():
    """
    ルートエンドポイント
    """
    return {"message": "Welcome to the Bear Sighting API!"}


@app.get("/health")
def health_check():
    """
    ヘルスチェック用エンドポイント
    """
    return {"status": "ok"}


@app.get("/sightings", response_model=list[schemas.BearSightingRead])
def get_all_sightings(db: Session = Depends(database.get_db)):  # noqa: B008
    """
    （テスト用）DBに登録されている全ての出没情報を取得
    """
    sightings = crud.get_sightings(db)
    return sightings


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
