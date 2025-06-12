# backend/utils.py
import json
import re
import os

def load_json(filepath):
    """Loads a JSON file from the given path."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return None

def normalize_text(text):
    """
    Normalizes text by converting to lowercase, removing punctuation,
    and stripping extra whitespace.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text) # Remove punctuation
    text = text.strip()
    return text

def get_available_topics(questions_dir_path):
    """
    Scans the questions directory to find available topic files (e.g., cpp.json).
    """
    topics = {}
    for filename in os.listdir(questions_dir_path):
        if filename.endswith('.json'):
            topic_name = filename.split('.')[0]
            topics[topic_name] = f"{questions_dir_path}/{filename}"
    return topics