import argparse
from pathlib import Path

import arabic_reshaper
import matplotlib.pyplot as plt
import pandas as pd
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

DEFAULT_DATA_FILE = 'data/sample_survey.csv'
REPORTS_DIR = Path('reports')
CHARTS_DIR = Path('charts')
FONT_DIR = Path('fonts')
ARABIC_FONT_PATH = FONT_DIR / 'DejaVuSans.ttf'

REPORTS_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)
FONT_DIR.mkdir(exist_ok=True)

# Configure matplotlib for Unicode support
plt.rcParams['font.family'] = 'DejaVu Sans'


def format_arabic_text(text):
    """Format Arabic text for proper RTL display."""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except Exception:
        return str(text)


if ARABIC_FONT_PATH.exists():
    pdfmetrics.registerFont(TTFont('Arabic', str(ARABIC_FONT_PATH)))


def load_data(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f'File not found: {file_path}')

    if path.suffix.lower() == '.csv':
        return pd.read_csv(path)

    if path.suffix.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(path)

    raise ValueError('Unsupported file type. Please use CSV, XLSX, or XLS files.')


def generate_summary(df):
    summary = []

    summary.append('Survey Analysis Report / تقرير تحليل الاستبيان')
    summary.append('=' * 50)
    summary.append(f'Total Responses / إجمالي الردود: {len(df)}')
    summary.append(f'Total Columns / عدد الأعمدة: {len(df.columns)}')
    summary.append('')

    for column in df.columns:
        formatted_column = format_arabic_text(column)
        summary.append(f'--- {formatted_column} ---')

        if pd.api.types.is_numeric_dtype(df[column]):
            summary.append(f'Average / المتوسط: {df[column].mean():.2f}')
            summary.append(f'Minimum / الحد الأدنى: {df[column].min()}')
            summary.append(f'Maximum / الحد الأعلى: {df[column].max()}')
            summary.append('')

        counts = df[column].value_counts(dropna=False)

        for value, count in counts.items():
            formatted_value = format_arabic_text(value)
            percentage = (count / len(df)) * 100
            summary.append(f'{formatted_value}: {count} ({percentage:.1f}%)')

        summary.append('')

    return '\n'.join(summary)


def save_text_report(content):
    report_path = REPORTS_DIR / 'survey_summary.txt'

    with open(report_path, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f'Text report saved to: {report_path}')


def save_pdf_report(content):
    pdf_path = REPORTS_DIR / 'survey_summary.pdf'
    document = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    styles = getSampleStyleSheet()

    if ARABIC_FONT_PATH.exists():
        styles['Normal'].fontName = 'Arabic'

    story = []

    for line in content.split('\n'):
        if line.strip() == '':
            story.append(Spacer(1, 8))
        else:
            story.append(Paragraph(line, styles['Normal']))

    document.build(story)

    print(f'PDF report saved to: {pdf_path}')


def generate_charts(df):
    for column in df.columns:
        if df[column].nunique(dropna=True) <= 20:
            counts = df[column].value_counts()

            if counts.empty:
                continue

            labels = [format_arabic_text(label) for label in counts.index]

            plt.figure(figsize=(8, 5))
            plt.bar(labels, counts.values)
            plt.title(format_arabic_text(f'{column} Distribution'))
            plt.xlabel(format_arabic_text(column))
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            safe_column_name = ''.join(char if char.isalnum() else '_' for char in str(column))
            chart_path = CHARTS_DIR / f'{safe_column_name}.png'
            plt.savefig(chart_path)
            plt.close()

            print(f'Chart saved: {chart_path}')


def parse_args():
    parser = argparse.ArgumentParser(description='Analyze survey data from CSV or Excel files with Arabic support.')
    parser.add_argument(
        '--file',
        default=DEFAULT_DATA_FILE,
        help='Path to survey file. Supports .csv, .xlsx, and .xls files.'
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print('Loading survey data...')
    df = load_data(args.file)

    print('Generating summary...')
    summary = generate_summary(df)

    print(summary)

    save_text_report(summary)
    save_pdf_report(summary)

    print('Generating charts...')
    generate_charts(df)

    print('Analysis complete.')


if __name__ == '__main__':
    main()
