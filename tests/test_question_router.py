# tests/test_question_router.py
import pytest
from unittest.mock import patch
from backend.question_router import QuestionRouter

# Mock data simulating the JSON files
MOCK_TOPICS = {
    "dsa": ["Arrays", "Trees"],
    "cpp": ["STL", "Pointers"]
}

MOCK_DSA_QUESTIONS = [
    {"id": "dsa-001", "question": "What is an array?", "answer": "...", "difficulty": "easy", "tags": ["Arrays"]},
    {"id": "dsa-002", "question": "What is a binary tree?", "answer": "...", "difficulty": "medium", "tags": ["Trees"]}
]

MOCK_CPP_QUESTIONS = [
    {"id": "cpp-001", "question": "What is std::vector?", "answer": "...", "difficulty": "easy", "tags": ["STL"]}
]

@pytest.fixture
def mock_load_json():
    """Pytest fixture to mock the load_json utility."""
    def _load_json_side_effect(filepath):
        if 'topics.json' in filepath:
            return MOCK_TOPICS
        if 'dsa.json' in filepath:
            return MOCK_DSA_QUESTIONS
        if 'cpp.json' in filepath:
            return MOCK_CPP_QUESTIONS
        raise FileNotFoundError(f"Mock file not found: {filepath}")

    # Patch the load_json function in the question_router module
    with patch('backend.question_router.load_json', side_effect=_load_json_side_effect) as mock:
        yield mock

def test_router_initialization(mock_load_json):
    """Test that the QuestionRouter initializes correctly."""
    router = QuestionRouter('../data/questions')
    assert "dsa" in router.questions
    assert "cpp" in router.questions
    assert router.topic_files["dsa"] == "../data/questions/dsa.json"

def test_get_question_valid_topic(mock_load_json):
    """Test retrieving a question from a valid topic."""
    router = QuestionRouter('../data/questions')
    question = router.get_question('dsa')
    
    assert question is not None
    assert question['id'].startswith('dsa-')
    assert 'question' in question

def test_get_question_avoids_asked_ids(mock_load_json):
    """Test that get_question does not return questions that have already been asked."""
    router = QuestionRouter('../data/questions')
    
    # Ask the first DSA question
    asked_ids = ["dsa-001"]
    question = router.get_question('dsa', asked_ids)
    
    assert question is not None
    # The only remaining question should be dsa-002
    assert question['id'] == "dsa-002"

def test_get_question_no_more_questions(mock_load_json):
    """Test that get_question returns None when all questions for a topic have been asked."""
    router = QuestionRouter('../data/questions')
    
    # Mark all DSA questions as asked
    asked_ids = ["dsa-001", "dsa-002"]
    question = router.get_question('dsa', asked_ids)
    
    assert question is None

def test_get_question_invalid_topic(mock_load_json):
    """Test retrieving a question from a topic that does not exist."""
    router = QuestionRouter('../data/questions')
    question = router.get_question('python') # This topic is not in our mock data
    
    assert question is None