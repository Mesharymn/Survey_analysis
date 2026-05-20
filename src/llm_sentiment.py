"""Optional LLM-based sentiment analysis.

The project can run without this module by using the rule-based sentiment engine.
To enable LLM analysis, set OPENAI_API_KEY in your environment and run:

    python src/main.py --sentiment-method llm
"""

import json
import os
from typing import Any, Dict

from openai import OpenAI

DEFAULT_LLM_RESULT = {
    "sentiment": "Neutral / محايد",
    "confidence": 0,
    "topics": [],
    "summary": "LLM analysis unavailable.",
    "language": "Unknown",
}


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


def analyze_sentiment_llm(text: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """Analyze one customer comment using an LLM and return a normalized dict."""

    client = get_client()

    if client is None:
        return DEFAULT_LLM_RESULT.copy()

    prompt = f"""
Analyze the following customer feedback.

Return ONLY valid JSON. Do not include markdown.

Rules:
- Support Arabic, English, and mixed Arabic-English text.
- Understand Saudi/Gulf Arabic expressions when possible.
- Consider negation, for example: "not bad" or "مو سيء".
- Extract practical business topics such as price, waiting time, staff, location, cleanliness, product availability, service speed, app experience, or delivery.

Feedback:
{text}

JSON format:
{{
  "sentiment": "Positive / إيجابي | Negative / سلبي | Neutral / محايد",
  "confidence": 0,
  "topics": [],
  "summary": "",
  "language": "Arabic | English | Mixed | Other"
}}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)

        return {
            "sentiment": parsed.get("sentiment", "Neutral / محايد"),
            "confidence": parsed.get("confidence", 0),
            "topics": parsed.get("topics", []),
            "summary": parsed.get("summary", ""),
            "language": parsed.get("language", "Unknown"),
        }

    except Exception as error:
        result = DEFAULT_LLM_RESULT.copy()
        result["summary"] = f"LLM analysis failed: {error}"
        return result
