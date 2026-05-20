import pandas as pd


def load_google_maps_reviews(file_path):
    """Load Google Maps review exports as survey-style data."""

    df = pd.read_csv(file_path)

    supported_columns = {
        'review_text': None,
        'rating': None,
        'author_name': None,
        'time': None,
        'latitude': None,
        'longitude': None,
    }

    for column in df.columns:
        normalized = column.lower().strip()

        if 'review' in normalized or 'comment' in normalized:
            supported_columns['review_text'] = column

        elif 'rating' in normalized or 'stars' in normalized:
            supported_columns['rating'] = column

        elif 'author' in normalized or 'user' in normalized or 'name' in normalized:
            supported_columns['author_name'] = column

        elif 'time' in normalized or 'date' in normalized:
            supported_columns['time'] = column

        elif normalized in ['latitude', 'lat']:
            supported_columns['latitude'] = column

        elif normalized in ['longitude', 'lng', 'lon']:
            supported_columns['longitude'] = column

    transformed = pd.DataFrame()

    if supported_columns['review_text']:
        transformed['feedback'] = df[supported_columns['review_text']]

    if supported_columns['rating']:
        transformed['rating'] = df[supported_columns['rating']]

    if supported_columns['author_name']:
        transformed['author'] = df[supported_columns['author_name']]

    if supported_columns['time']:
        transformed['date'] = df[supported_columns['time']]

    if supported_columns['latitude']:
        transformed['latitude'] = df[supported_columns['latitude']]

    if supported_columns['longitude']:
        transformed['longitude'] = df[supported_columns['longitude']]

    return transformed
