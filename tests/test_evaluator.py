# tests/test_evaluator.py
import pytest
from backend.evaluator import Evaluator

@pytest.fixture
def evaluator():
    """Returns an Evaluator instance for testing."""
    return Evaluator()

def test_evaluation_high_score(evaluator):
    """Test a scenario where the user's answer is very good."""
    model_answer = "Vector is a dynamic array with contiguous memory. List is a doubly-linked list."
    user_answer = "A vector stores elements in contiguous memory like a dynamic array, while a list is essentially a doubly-linked list."
    
    feedback, score = evaluator.evaluate(user_answer, model_answer)
    
    assert score >= 80
    assert "Excellent" in feedback

def test_evaluation_medium_score(evaluator):
    """Test a scenario where the user's answer is partially correct."""
    model_answer = "Smart pointers automate memory management, preventing leaks. Examples are unique_ptr and shared_ptr."
    user_answer = "Smart pointers are for memory management, like unique_ptr."
    
    feedback, score = evaluator.evaluate(user_answer, model_answer)
    
    assert 50 <= score < 80
    assert "Good start" in feedback

def test_evaluation_low_score(evaluator):
    """Test a scenario where the user's answer is mostly incorrect."""
    model_answer = "Normalization reduces data redundancy in a relational database."
    user_answer = "It is something about making data fast."
    
    feedback, score = evaluator.evaluate(user_answer, model_answer)
    
    assert score < 50
    assert "missing some key concepts" in feedback

def test_evaluation_is_case_insensitive_and_ignores_punctuation(evaluator):
    """Test that text normalization works as expected."""
    model_answer = "SQL's DELETE is a DML command; TRUNCATE is DDL."
    user_answer = "sql delete is a dml command, truncate is ddl!!"
    
    feedback, score = evaluator.evaluate(user_answer, model_answer)
    
    # Should be a perfect match after normalization
    assert score >= 80 

def test_evaluation_with_empty_user_answer(evaluator):
    """Test an empty answer submission."""
    model_answer = "Anything"
    user_answer = ""
    
    feedback, score = evaluator.evaluate(user_answer, model_answer)
    
    assert score == 0