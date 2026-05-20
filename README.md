# Survey Analysis Toolkit

A small Python tool I built to explore survey results, customer comments, and Google Maps-style review exports without opening a spreadsheet every time.

The goal is simple: drop in a CSV or Excel file, run one command, and get a basic report with summaries, charts, sentiment/context signals, and exports that are easy to review.

## What it does

- Reads survey data from `.csv`, `.xlsx`, or `.xls`
- Generates a text summary report
- Exports a PDF report
- Creates simple charts for columns with limited answer options
- Supports Arabic and English text
- Adds basic sentiment detection for open-ended comments
- Extracts repeated keywords from free-text answers
- Includes a loader for Google Maps review-style exports

## Why this project exists

I wanted a lightweight analytics project that is practical enough for real feedback files, but still simple enough to understand and improve. It is not meant to replace BI tools or advanced NLP platforms. It is more like a quick first-pass analysis tool.

## Project structure

```text
Survey_analysis-/
├── data/
│   ├── sample_survey.csv
│   └── google_maps_reviews_sample.csv
├── src/
│   ├── main.py
│   └── google_maps_reviews.py
├── reports/
├── charts/
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone https://github.com/Mesharymn/Survey_analysis-.git
cd Survey_analysis-
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

## Basic usage

Run the included sample file:

```bash
python src/main.py
```

Run a specific CSV file:

```bash
python src/main.py --file data/sample_survey.csv
```

Run an Excel file:

```bash
python src/main.py --file data/my_survey.xlsx
```

## Example survey format

```csv
name,age_group,satisfaction,service_quality,recommend,feedback
Ali,18-24,5,Excellent,Yes,"The service was fast and helpful"
Sara,25-34,2,Poor,No,"الخدمة بطيئة والتجربة غير واضحة"
```

## Google Maps review format

The helper file `src/google_maps_reviews.py` can normalize review exports with columns such as:

```csv
author_name,rating,review_text,latitude,longitude,time
Ali,5,"Excellent service",24.5247,39.5692,2026-05-20
Sara,2,"الخدمة بطيئة",24.4709,39.6122,2026-05-21
```

## Outputs

After running the script, outputs are saved locally:

```text
reports/survey_summary.txt
reports/survey_summary.pdf
reports/sentiment_details.csv
charts/*.png
```

Generated files are ignored by Git so the repository stays clean.

## Arabic support notes

Arabic text is handled using:

- `arabic-reshaper`
- `python-bidi`
- UTF-8 exports

For the best Arabic PDF output, place an Arabic-supporting TTF font inside:

```text
fonts/DejaVuSans.ttf
```

The font file is not included in the repository.

## Current limitations

- Sentiment analysis is dictionary-based, not a machine learning model
- Arabic sentiment is basic and should be improved with more vocabulary
- PDF styling is intentionally simple
- Charts are generated only for columns with a small number of unique values
- Google Maps support currently expects exported review/comment data, not live scraping

## Ideas for future improvement

- Streamlit dashboard
- Interactive map report
- Better Arabic sentiment dictionary
- Topic clustering for comments
- Cleaner PDF design
- Google Places API integration
- Unit tests

## Tech stack

- Python
- pandas
- matplotlib
- reportlab
- openpyxl
- arabic-reshaper
- python-bidi
- folium
