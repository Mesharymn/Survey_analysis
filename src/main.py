import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

DEFAULT_DATA_FILE = 'data/sample_survey.csv'
REPORTS_DIR = Path('reports')
CHARTS_DIR = Path('charts')

REPORTS_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)


def load_data(file_path):
    """Load survey data from CSV or Excel file."""
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

    summary.append('Survey Analysis Report')
    summary.append('=' * 24)
    summary.append(f'Total Responses: {len(df)}')
    summary.append(f'Total Questions/Columns: {len(df.columns)}')
    summary.append('')

    for column in df.columns:
        summary.append(f'--- {column.upper()} ---')

        if pd.api.types.is_numeric_dtype(df[column]):
            summary.append(f'Average: {df[column].mean():.2f}')
            summary.append(f'Minimum: {df[column].min()}')
            summary.append(f'Maximum: {df[column].max()}')
            summary.append('')

        counts = df[column].value_counts(dropna=False)

        for value, count in counts.items():
            percentage = (count / len(df)) * 100
            summary.append(f'{value}: {count} ({percentage:.1f}%)')

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

            plt.figure(figsize=(8, 5))
            counts.plot(kind='bar')
            plt.title(f'{column} Distribution')
            plt.xlabel(column)
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            safe_column_name = ''.join(char if char.isalnum() else '_' for char in column)
            chart_path = CHARTS_DIR / f'{safe_column_name}.png'
            plt.savefig(chart_path)
            plt.close()

            print(f'Chart saved: {chart_path}')


def parse_args():
    parser = argparse.ArgumentParser(description='Analyze survey data from CSV or Excel files.')
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
