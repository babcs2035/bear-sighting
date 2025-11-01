import os
from datetime import datetime, timedelta

import httpx
from dotenv import load_dotenv
from sqlalchemy.orm import Session

import crud
import geocoding
import llm
import schemas

load_dotenv()

# --- 1. NewsAPI Configuration ---
# User-defined endpoint (API key sent in headers).
# Search query q='クマ'.
# Source domains=web.nhk.
# Start date from=1 day ago.
# Sort order sortBy=publishedAt.
BASE_NEWS_API_URL = "https://newsapi.org/v2/everything"

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
if NEWS_API_KEY is None:
    raise ValueError("NEWS_API_KEY is not set in environment variables.")  # 🚨 Raise an error if the API key is missing.


def fetch_news_from_api() -> list[dict]:
    """
    Fetch bear-related articles from NHK using NewsAPI.
    """
    # Target articles from "yesterday" onwards.
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    params = {
        "q": "クマ",
        "domains": "web.nhk",
        "from": yesterday,
        "sortBy": "publishedAt",
    }
    headers = {"Authorization": f"Bearer {NEWS_API_KEY}"}

    try:
        with httpx.Client() as client:
            response = client.get(BASE_NEWS_API_URL, params=params, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx, 5xx).

            data = response.json()
            return data.get("articles", [])

    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error while requesting NewsAPI: {e}")
        return []
    except Exception as e:
        print(f"⚠️ Unexpected error while requesting NewsAPI: {e}")
        return []


def process_and_save_articles(db: Session):
    """
    [Main Logic]
    Fetch articles → Analyze with LLM → Geocode → Save to DB.
    """
    print(f"--- {datetime.now()} | Scheduled job started ---")

    # 1. Fetch articles.
    articles = fetch_news_from_api()
    if not articles:
        print("No articles retrieved.")
        return

    print(f"Retrieved {len(articles)} articles. Starting analysis...")

    saved_count = 0
    for article in articles:
        url = article.get("url")
        if not url:
            continue

        # 2. Check for duplicates in the DB (by URL).
        existing = crud.get_sighting_by_url(db, source_url=url)
        if existing:
            continue  # Skip if the article already exists in the DB.

        # 3. Analyze with LLM (classification + extraction).
        title = article.get("title", "")
        description = article.get("description", "")
        print(f"🧠 Analyzing with LLM: {title}, {url}")

        llm_result = llm.analyze_article_with_llm(title, description)

        if not llm_result or not llm_result.is_sighting:
            # LLM determined it is not a sighting or analysis failed.
            continue

        # 4. Geocoding.
        coordinates = geocoding.get_coordinates_for_location(llm_result.prefecture, llm_result.city)

        # 5. Prepare schema for DB saving.
        try:
            # Convert NewsAPI's "publishedAt" (str) to a datetime object.
            published_dt = datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00"))

            sighting_data = schemas.BearSightingCreate(
                prefecture=llm_result.prefecture,
                city=llm_result.city,
                summary=llm_result.summary or "No summary available",
                latitude=coordinates[0] if coordinates else None,
                longitude=coordinates[1] if coordinates else None,
                source_url=url,
                image_url=article.get("urlToImage"),
                published_at=published_dt,
            )

            # 6. Save to DB.
            crud.create_sighting(db, sighting=sighting_data)
            saved_count += 1
            print(f"✅ Successfully saved: {title}")

        except Exception as e:
            print(f"❌ Error while preparing or saving to DB: {e}")

    print(f"--- Scheduled job completed | {saved_count} new records saved ---")
