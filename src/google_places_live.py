"""Fetch recent Google Places reviews through the official Places API.

This module intentionally uses Google's API instead of scraping Google Maps pages.
You need a Google Maps Platform API key with Places API access enabled.

Environment variable required:
    GOOGLE_MAPS_API_KEY

Example:
    python src/google_places_live.py --place-id YOUR_PLACE_ID
"""

import argparse
import os
from pathlib import Path

import pandas as pd
import requests

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def fetch_place_reviews(place_id, api_key, language="en"):
    params = {
        "place_id": place_id,
        "fields": "name,rating,user_ratings_total,reviews,geometry",
        "language": language,
        "key": api_key,
    }

    response = requests.get(PLACES_DETAILS_URL, params=params, timeout=20)
    response.raise_for_status()

    payload = response.json()

    if payload.get("status") != "OK":
        raise RuntimeError(f"Google Places API error: {payload.get('status')} - {payload.get('error_message')}")

    result = payload.get("result", {})
    place_name = result.get("name")
    location = result.get("geometry", {}).get("location", {})
    reviews = result.get("reviews", [])

    rows = []

    for review in reviews:
        rows.append({
            "place_name": place_name,
            "author_name": review.get("author_name"),
            "rating": review.get("rating"),
            "review_text": review.get("text"),
            "relative_time_description": review.get("relative_time_description"),
            "time": review.get("time"),
            "latitude": location.get("lat"),
            "longitude": location.get("lng"),
            "source": "Google Places API",
        })

    return pd.DataFrame(rows)


def save_reviews(df, output_file):
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch Google Places reviews using the official API.")
    parser.add_argument("--place-id", required=True, help="Google Place ID for the business/location.")
    parser.add_argument("--language", default="en", help="Review language preference, e.g. en or ar.")
    parser.add_argument(
        "--output",
        default="data/google_places_live_reviews.csv",
        help="CSV output path for fetched reviews.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        raise EnvironmentError("Missing GOOGLE_MAPS_API_KEY environment variable.")

    reviews_df = fetch_place_reviews(args.place_id, api_key, args.language)

    if reviews_df.empty:
        print("No reviews returned by the API for this place.")
        return

    output_path = save_reviews(reviews_df, args.output)
    print(f"Saved {len(reviews_df)} reviews to {output_path}")


if __name__ == "__main__":
    main()
