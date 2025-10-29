import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI(
    title="クマ出没情報 API (Bear Sighting API)",
    version="0.1.0",
    root_path="/bear-sighting-api",
)


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
