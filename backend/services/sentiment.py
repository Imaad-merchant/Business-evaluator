from textblob import TextBlob

# Financial keyword sentiment modifiers
POSITIVE_KEYWORDS = {
    "record revenue": 0.3,
    "beat expectations": 0.25,
    "strong growth": 0.25,
    "raised guidance": 0.3,
    "upgrade": 0.2,
    "bullish": 0.2,
    "outperform": 0.2,
    "new partnership": 0.15,
    "expansion": 0.15,
    "profit surge": 0.3,
    "dividend increase": 0.2,
    "stock buyback": 0.15,
    "all-time high": 0.2,
    "breakthrough": 0.2,
    "innovation": 0.1,
}

NEGATIVE_KEYWORDS = {
    "bankruptcy": -0.5,
    "lawsuit": -0.2,
    "fraud": -0.4,
    "investigation": -0.3,
    "recall": -0.25,
    "downgrade": -0.2,
    "bearish": -0.2,
    "miss expectations": -0.25,
    "lowered guidance": -0.3,
    "layoffs": -0.2,
    "restructuring": -0.15,
    "debt default": -0.4,
    "sec investigation": -0.35,
    "delisting": -0.4,
    "supply chain": -0.1,
    "recession": -0.15,
    "sell-off": -0.2,
    "plunge": -0.25,
    "crash": -0.3,
    "warning": -0.15,
}


def analyze_sentiment(text: str) -> dict:
    if not text:
        return {"score": 0.0, "label": "neutral", "confidence": 0.0}

    # TextBlob baseline
    blob = TextBlob(text)
    base_score = blob.sentiment.polarity  # -1 to 1

    # Apply financial keyword modifiers
    text_lower = text.lower()
    modifier = 0.0

    for keyword, weight in POSITIVE_KEYWORDS.items():
        if keyword in text_lower:
            modifier += weight

    for keyword, weight in NEGATIVE_KEYWORDS.items():
        if keyword in text_lower:
            modifier += weight  # weight is already negative

    # Combine: base contributes 60%, keywords 40%
    final_score = (base_score * 0.6) + (modifier * 0.4)
    final_score = max(-1.0, min(1.0, final_score))

    # Label
    if final_score > 0.1:
        label = "positive"
    elif final_score < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return {
        "score": round(final_score, 3),
        "label": label,
        "confidence": round(abs(final_score), 3),
        "base_score": round(base_score, 3),
        "keyword_modifier": round(modifier, 3),
    }


def analyze_articles(articles: list[dict]) -> dict:
    if not articles:
        return {
            "overall_score": 0.0,
            "overall_label": "neutral",
            "article_count": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "articles": [],
        }

    scored_articles = []
    total_score = 0.0
    positive = 0
    negative = 0
    neutral = 0

    for article in articles:
        text = f"{article.get('title', '')} {article.get('summary', '')}"
        sentiment = analyze_sentiment(text)

        scored_article = {**article, "sentiment": sentiment}
        scored_articles.append(scored_article)

        total_score += sentiment["score"]
        if sentiment["label"] == "positive":
            positive += 1
        elif sentiment["label"] == "negative":
            negative += 1
        else:
            neutral += 1

    avg_score = total_score / len(articles)
    if avg_score > 0.1:
        overall_label = "positive"
    elif avg_score < -0.1:
        overall_label = "negative"
    else:
        overall_label = "neutral"

    return {
        "overall_score": round(avg_score, 3),
        "overall_label": overall_label,
        "article_count": len(articles),
        "positive_count": positive,
        "negative_count": negative,
        "neutral_count": neutral,
        "articles": scored_articles,
    }
