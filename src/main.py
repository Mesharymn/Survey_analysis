import argparse
import re
from collections import Counter
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

plt.rcParams['font.family'] = 'DejaVu Sans'

POSITIVE_WORDS = {
    'good', 'great', 'excellent', 'amazing', 'fast', 'easy', 'helpful', 'clear',
    'satisfied', 'happy', 'love', 'best', 'useful', 'professional', 'smooth',
    'جيد', 'جيدة', 'ممتاز', 'ممتازة', 'رائع', 'رائعة', 'سريع', 'سريعة',
    'سهل', 'سهلة', 'مفيد', 'مفيدة', 'واضح', 'واضحة', 'راضي', 'راضية',
    'سعيد', 'سعيدة', 'احترافي', 'احترافية', 'جميل', 'جميلة', 'أفضل'
}

NEGATIVE_WORDS = {
    'bad', 'poor', 'slow', 'difficult', 'hard', 'confusing', 'expensive', 'late',
    'problem', 'issue', 'weak', 'angry', 'unhappy', 'worst', 'unclear',
    'سيء', 'سيئة', 'ضعيف', 'ضعيفة', 'بطيء', 'بطيئة', 'صعب', 'صعبة',
    'مشكلة', 'مشاكل', 'غالي', 'غالية', 'متأخر', 'متأخرة', 'غير واضح',
    'معقد', 'معقدة', 'أسوأ', 'زعلان', 'زعلانة'
}

STOP_WORDS = {
    'the', 'and', 'for', 'with', 'this', 'that', 'was', 'were', 'very', 'from',
    'have', 'has', 'had', 'not', 'you', 'your', 'our', 'their', 'they', 'are',
    'في', 'من', 'على', 'الى', 'إلى', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'كانت',
    'كان', 'انه', 'أن', 'إن', 'او', 'أو', 'لكن', 'جدا', 'كل', 'ما', 'لا', 'نعم'
}


def format_arabic_text(text):
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


def tokenize_text(text):
    words = re.findall(r'[\w\u0600-\u06FF]+', str(text).lower())
    return [word for word in words if word not in STOP_WORDS and len(word) > 2]


def detect_sentiment(text):
    words = tokenize_text(text)
    positive_score = sum(1 for word in words if word in POSITIVE_WORDS)
    negative_score = sum(1 for word in words if word in NEGATIVE_WORDS)

    if positive_score > negative_score:
        return 'Positive / إيجابي'
    if negative_score > positive_score:
        return 'Negative / سلبي'
    return 'Neutral / محايد'


def is_open_text_column(series):
    if not pd.api.types.is_object_dtype(series):
        return False

    text_values = series.dropna().astype(str)

    if text_values.empty:
        return False

    average_words = text_values.apply(lambda value: len(str(value).split())).mean()
    unique_ratio = text_values.nunique() / len(text_values)

    return average_words >= 3 or unique_ratio > 0.6


def analyze_sentiment_and_context(df):
    results = []
    sentiment_rows = []

    results.append('Sentiment & Context Analysis / تحليل المشاعر والسياق')
    results.append('=' * 60)

    open_text_columns = [column for column in df.columns if is_open_text_column(df[column])]

    if not open_text_columns:
        results.append('No open-text response columns detected / لم يتم اكتشاف أعمدة نصية مفتوحة')
        results.append('')
        return '\n'.join(results), pd.DataFrame()

    for column in open_text_columns:
        values = df[column].dropna().astype(str)
        sentiments = values.apply(detect_sentiment)
        sentiment_counts = sentiments.value_counts()

        results.append(f'--- {format_arabic_text(column)} ---')
        results.append(f'Text Responses Analyzed / الردود النصية المحللة: {len(values)}')

        for sentiment, count in sentiment_counts.items():
            percentage = (count / len(values)) * 100
            results.append(f'{format_arabic_text(sentiment)}: {count} ({percentage:.1f}%)')

        all_words = []
        for value in values:
            all_words.extend(tokenize_text(value))

        common_words = Counter(all_words).most_common(10)

        if common_words:
            results.append('Top Context Keywords / أهم الكلمات المتكررة:')
            for word, count in common_words:
                results.append(f'- {format_arabic_text(word)}: {count}')

        positive_examples = values[sentiments == 'Positive / إيجابي'].head(2).tolist()
        negative_examples = values[sentiments == 'Negative / سلبي'].head(2).tolist()

        if positive_examples:
            results.append('Positive Examples / أمثلة إيجابية:')
            for example in positive_examples:
                results.append(f'- {format_arabic_text(example)}')

        if negative_examples:
            results.append('Negative Examples / أمثلة سلبية:')
            for example in negative_examples:
                results.append(f'- {format_arabic_text(example)}')

        results.append('')

        for value, sentiment in zip(values, sentiments):
            sentiment_rows.append({
                'column': column,
                'response': value,
                'sentiment': sentiment,
            })

    return '\n'.join(results), pd.DataFrame(sentiment_rows)


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

    sentiment_summary, sentiment_df = analyze_sentiment_and_context(df)
    summary.append(sentiment_summary)
    save_sentiment_details(sentiment_df)

    return '\n'.join(summary)


def save_sentiment_details(sentiment_df):
    if sentiment_df.empty:
        return

    output_path = REPORTS_DIR / 'sentiment_details.csv'
    sentiment_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f'Sentiment details saved to: {output_path}')


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


def generate_sentiment_charts(sentiment_df):
    if sentiment_df.empty:
        return

    for column in sentiment_df['column'].unique():
        column_data = sentiment_df[sentiment_df['column'] == column]
        counts = column_data['sentiment'].value_counts()
        labels = [format_arabic_text(label) for label in counts.index]

        plt.figure(figsize=(8, 5))
        plt.bar(labels, counts.values)
        plt.title(format_arabic_text(f'Sentiment for {column}'))
        plt.xlabel('Sentiment')
        plt.ylabel('Count')
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()

        safe_column_name = ''.join(char if char.isalnum() else '_' for char in str(column))
        chart_path = CHARTS_DIR / f'sentiment_{safe_column_name}.png'
        plt.savefig(chart_path)
        plt.close()

        print(f'Sentiment chart saved: {chart_path}')


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

    sentiment_summary, sentiment_df = analyze_sentiment_and_context(df)
    generate_sentiment_charts(sentiment_df)

    print('Analysis complete.')


if __name__ == '__main__':
    main()
