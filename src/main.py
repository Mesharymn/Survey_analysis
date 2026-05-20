import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA_FILE = 'data/sample_survey.csv'
REPORTS_DIR = Path('reports')
CHARTS_DIR = Path('charts')

REPORTS_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)


def load_data():
    return pd.read_csv(DATA_FILE)


def generate_summary(df):
    summary = []

    summary.append(f'Total Responses: {len(df)}\n')

    for column in df.columns:
        summary.append(f'--- {column.upper()} ---')

        counts = df[column].value_counts()

        for value, count in counts.items():
            percentage = (count / len(df)) * 100
            summary.append(f'{value}: {count} ({percentage:.1f}%)')

        summary.append('')

    return '\n'.join(summary)


def save_report(content):
    report_path = REPORTS_DIR / 'survey_summary.txt'

    with open(report_path, 'w') as file:
        file.write(content)

    print(f'Report saved to: {report_path}')


def generate_charts(df):
    for column in df.columns:
        if df[column].dtype == 'object':
            counts = df[column].value_counts()

            plt.figure(figsize=(6, 4))
            counts.plot(kind='bar')
            plt.title(f'{column} Distribution')
            plt.xlabel(column)
            plt.ylabel('Count')
            plt.tight_layout()

            chart_path = CHARTS_DIR / f'{column}.png'
            plt.savefig(chart_path)
            plt.close()

            print(f'Chart saved: {chart_path}')


def main():
    print('Loading survey data...')

    df = load_data()

    print('Generating summary...')

    summary = generate_summary(df)

    print(summary)

    save_report(summary)

    print('Generating charts...')

    generate_charts(df)

    print('Analysis complete.')


if __name__ == '__main__':
    main()
