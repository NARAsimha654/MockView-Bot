# backend/question_router.py
import random
from utils import load_json

class QuestionRouter:
    def __init__(self, data_path):
        self.data_path = data_path 
        self.topics = list(load_json('topics.json').keys())
        self.loaded_questions = {}

    def _load_topic(self, topic):
        if topic not in self.loaded_questions:
            try:
                filepath = f"{self.data_path}/{topic}.json"
                self.loaded_questions[topic] = load_json(filepath)
            except FileNotFoundError:
                print(f"ERROR: Could not find question file for topic '{topic}' at path: {filepath}")
                return None
        return self.loaded_questions[topic]

    def get_question(self, topic, asked_ids=[]):
        questions_for_topic = self._load_topic(topic)
        if not questions_for_topic: return None
        available_questions = [q for q in questions_for_topic if q.get('id') not in asked_ids]
        if not available_questions: return None 
        return random.choice(available_questions)

    def find_question_by_tag(self, tag: str, excluded_ids=[]):
        """NEW: Searches all topics for a question matching a specific tag/skill."""
        tag = tag.lower()
        # Search topics in a random order to get variety
        random.shuffle(self.topics)
        for topic in self.topics:
            all_questions = self._load_topic(topic)
            if all_questions:
                for question in all_questions:
                    # Check if tag is in the question's tags and not already excluded
                    if tag in [t.lower() for t in question.get('tags', [])] and question.get('id') not in excluded_ids:
                        return question
        return None # Return None if no matching question is found