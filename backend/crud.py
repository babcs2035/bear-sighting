from sqlalchemy.orm import Session

import models
import schemas


# -------------------------------------------------
# CREATE
# -------------------------------------------------
def create_sighting(db: Session, sighting: schemas.BearSightingCreate) -> models.BearSighting:
    """
    Accepts bear sighting data (Pydantic schema),
    converts it to a DB model, and saves it to the database.
    """

    # Create an SQLAlchemy model (models.BearSighting) from the Pydantic model (.model_dump()).
    db_sighting = models.BearSighting(**sighting.model_dump())

    db.add(db_sighting)  # Add to the DB session.
    db.commit()  # Commit (write) to the database.
    db.refresh(db_sighting)  # Refresh to get the latest state (e.g., auto-generated ID).

    return db_sighting


# -------------------------------------------------
# READ
# -------------------------------------------------
def get_sighting_by_url(db: Session, source_url: str) -> models.BearSighting | None:
    """
    Retrieve a single sighting by its source URL.
    (Used to prevent duplicate entries.)
    """
    return db.query(models.BearSighting).filter(models.BearSighting.source_url == source_url).first()


def get_sightings(db: Session) -> list[models.BearSighting]:
    """
    Retrieve a list of all bear sightings. (Pagination support can be added.)
    """
    return db.query(models.BearSighting).all()
