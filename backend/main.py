from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

import crud
import database
import models
import schemas
import services

load_dotenv()

models.Base.metadata.create_all(bind=database.engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Scheduler setup ---
    print("🕒 Adding scheduler job (runs daily).")
    scheduler.add_job(
        run_sighting_job,
        trigger=IntervalTrigger(days=1),  # Runs daily.
        id="sighting_job",
        replace_existing=True,
    )

    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Bear Sighting API", version="0.1.0", root_path="/bear-sighting-api", lifespan=lifespan)


@app.get("/")
def read_root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to the Bear Sighting API!"}


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}


@app.get("/sightings", response_model=list[schemas.BearSightingRead])
def get_all_sightings(db: Session = Depends(database.get_db)):  # noqa: B008
    """
    (For testing) Retrieve all bear sightings from the database.
    """
    sightings = crud.get_sightings(db)
    return sightings


def run_sighting_job():
    """
    Execute services.process_and_save_articles.
    """
    db: Session = database.SessionLocal()  # Create a new DB session.
    try:
        services.process_and_save_articles(db)
    except Exception as e:
        print(f"❌ Error during scheduled job execution: {e}")
    finally:
        db.close()


scheduler = AsyncIOScheduler()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
