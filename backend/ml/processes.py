import re
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

STOPWORDS = set(["the", "a", "an", "and", "or", "in", "on", "at", "for", "with", "to"])

def clean_text(text):
    text = re.sub(r"[^a-zA-Z ]", "", text)
    text = text.lower()
    words = text.split()
    words = [word for word in words if word not in STOPWORDS]
    return " ".join(words)

def process_resume(text):
    cleaned_text = clean_text(text)
    return cleaned_text