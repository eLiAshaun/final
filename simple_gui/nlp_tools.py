"""
nlp_tools.py

Simple NLP utilities for Final Project:
- extract_keywords_yake(messages)
- summarize_with_sumy(messages)

The preferred implementation uses YAKE and Sumy when those packages are
installed in the project virtual environment. The fallback implementation uses
only the Python standard library, so /keywords and /summary still work during
demo if a dependency is missing.
"""

from collections import Counter
import re
from typing import List


STOP_WORDS = {
    "about", "after", "again", "also", "and", "are", "because", "been",
    "before", "being", "between", "both", "but", "can", "could", "does",
    "each", "for", "from", "had", "has", "have", "here", "into", "its",
    "just", "like", "more", "most", "need", "not", "our", "out", "over",
    "should", "some", "than", "that", "the", "their", "them", "then",
    "there", "these", "they", "this", "through", "too", "use", "used",
    "using", "want", "was", "were", "what", "when", "where", "which",
    "while", "who", "will", "with", "would", "you", "your",
}


def _join_messages(messages: List[str]) -> str:
    return "\n".join(m.strip() for m in messages if m and m.strip())


def _word_counts(text: str) -> Counter:
    words = re.findall(r"[A-Za-z][A-Za-z']{2,}", text.lower())
    useful_words = [word for word in words if word not in STOP_WORDS]
    return Counter(useful_words)


def _fallback_keywords(messages: List[str], top_k: int = 5) -> List[str]:
    text = _join_messages(messages)
    if not text:
        return []

    words = re.findall(r"[A-Za-z][A-Za-z']{2,}", text.lower())
    useful_words = [word for word in words if word not in STOP_WORDS]
    word_counts = Counter(useful_words)
    phrase_counts = Counter()
    for first, second in zip(words, words[1:]):
        if first in STOP_WORDS or second in STOP_WORDS:
            continue
        phrase_counts[first + " " + second] += 1

    candidates = []
    for phrase, count in phrase_counts.items():
        candidates.append((count * 2, phrase))
    for word, count in word_counts.items():
        candidates.append((count, word))

    keywords = []
    seen = set()
    for _, keyword in sorted(candidates, reverse=True):
        marker = keyword.lower()
        if marker in seen:
            continue
        if any(marker in existing or existing in marker for existing in seen):
            continue
        keywords.append(keyword)
        seen.add(marker)
        if len(keywords) >= top_k:
            break
    return keywords


def _split_sentences(text: str) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def _fallback_summary(messages: List[str], sentences_count: int = 3) -> List[str]:
    text = _join_messages(messages)
    if not text:
        return []

    sentences = _split_sentences(text)
    if len(sentences) <= sentences_count:
        return sentences

    counts = _word_counts(text)
    scored = []
    for index, sentence in enumerate(sentences):
        words = re.findall(r"[A-Za-z][A-Za-z']{2,}", sentence.lower())
        score = sum(counts[word] for word in words if word in counts)
        scored.append((score, index, sentence))

    chosen = sorted(scored, reverse=True)[:sentences_count]
    return [sentence for _, _, sentence in sorted(chosen, key=lambda item: item[1])]


# ---------------------------
# Keyword extraction with YAKE
# ---------------------------

def extract_keywords_yake(messages: List[str], top_k: int = 5) -> List[str]:
    """
    Extract top_k keywords from a list of chat messages.
    """
    if not messages:
        return []

    text = _join_messages(messages)
    if not text:
        return []

    try:
        import yake

        kw_extractor = yake.KeywordExtractor(
            lan="en",
            n=2,
            top=top_k,
            features=None,
        )

        keywords = kw_extractor.extract_keywords(text)
        keywords_sorted = sorted(keywords, key=lambda x: x[1])
        return [kw for kw, score in keywords_sorted[:top_k]]
    except Exception:
        return _fallback_keywords(messages, top_k)


# ---------------------------
# Summarization with Sumy
# ---------------------------

def summarize_with_sumy(messages: List[str], sentences_count: int = 3) -> List[str]:
    """
    Generate a short extractive summary from chat messages.
    """
    if not messages:
        return []

    text = _join_messages(messages)
    if not text:
        return []

    try:
        import nltk

        for resource in ("punkt", "punkt_tab"):
            try:
                nltk.data.find(f"tokenizers/{resource}")
            except LookupError:
                try:
                    nltk.download(resource, quiet=True)
                except Exception:
                    pass

        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.luhn import LuhnSummarizer

        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LuhnSummarizer()

        summary_sentences = summarizer(parser.document, sentences_count)
        summary = [str(sentence) for sentence in summary_sentences]
        return summary or _fallback_summary(messages, sentences_count)
    except Exception:
        return _fallback_summary(messages, sentences_count)

# ---------------------------
# Small demo (optional)
# ---------------------------

if __name__ == "__main__":
    demo_history = [
        "Hi everyone, welcome to the chat system project discussion.",
        "We need to design the client-server architecture first.",
        "I think we should implement the GUI using Tkinter.",
        "What do you think about adding an AI chatbot feature to the system?",
        "We can also support file transfer and emojis as extra features.",
        "Later we should write clear documentation and a project guideline for users.",
    ]

    print("=== /keywords demo ===")
    print(extract_keywords_yake(demo_history))

    print("\n=== /summary demo ===")
    print(summarize_with_sumy(demo_history))
