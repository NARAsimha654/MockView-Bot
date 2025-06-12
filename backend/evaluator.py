# backend/evaluator.py
import os
import json
import google.generativeai as genai
from utils import normalize_text

# Configure Gemini API key when the module is loaded
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
except Exception as e:
    print(f"Could not configure Gemini API: {e}")

# NEW: Helper function to get persona instructions
def _get_persona_prompt(persona: str):
    """Returns the system prompt instruction based on the selected persona."""
    if persona == 'Friendly':
        return "You are an AI interviewer acting as a friendly and encouraging teammate. Your tone should be collaborative and positive. When giving feedback, start with what the user did well before giving constructive criticism."
    elif persona == 'Strict':
        return "You are an AI interviewer acting as a strict, direct senior engineer. You value accuracy and conciseness. Your feedback should be technical, precise, and to-the-point. Do not use conversational filler."
    else: # Neutral
        return "You are an AI interviewer. Your tone should be professional, neutral, and objective."

class Evaluator:
    # No changes to __init__ needed

    def _evaluate_with_keywords(self, user_answer, model_answer):
        # This function is unchanged
        user_words = set(normalize_text(user_answer).split())
        model_words = set(normalize_text(model_answer).split())
        if not model_words: return "Cannot evaluate as model answer is empty.", 0
        common_words = user_words.intersection(model_words)
        score = (len(common_words) / len(model_words)) * 100
        if score >= 80: feedback = "Excellent! Your answer is very comprehensive."
        elif score >= 50: feedback = "Good start. You've covered the main points, but you could add more detail."
        else: feedback = "Your answer seems to be missing some key concepts. Compare it with the model answer."
        return feedback, round(score)

    def _evaluate_with_gemini(self, user_answer, model_answer, question, persona):
        """Evaluates the user's answer using the Gemini API and a specific persona."""
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Get the persona-specific instructions
        persona_instruction = _get_persona_prompt(persona)
        
        prompt = f"""
        {persona_instruction}

        You are evaluating a user's answer to a technical interview question.

        **The Question:**
        "{question}"
        
        **The Ideal Model Answer:**
        "{model_answer}"
        
        **The User's Answer:**
        "{user_answer}"
        
        **Your Tasks:**
        1.  **Score:** Provide a numerical score from 0 to 100 based on the technical accuracy, completeness, and clarity of the user's answer compared to the model answer.
        2.  **Feedback:** Provide concise, constructive feedback based on your assigned persona. Explain what was good and what could be improved.

        **Return your response as a valid JSON object with two keys: "score" (an integer) and "feedback" (a string).**
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        result = json.loads(response.text)
        print(f"Gemini evaluation successful (Persona: {persona}).")
        return result["feedback"], result["score"]

    def evaluate(self, user_answer, model_answer, question, use_llm=False, persona='Neutral'):
        """
        Evaluates the user's answer, now accepting a persona.
        """
        if use_llm:
            try:
                # Pass the persona to the Gemini evaluation method
                return self._evaluate_with_gemini(user_answer, model_answer, question, persona)
            except Exception as e:
                print(f"Gemini evaluation failed: {e}. Falling back to keyword matching.")
                return self._evaluate_with_keywords(user_answer, model_answer)
        
        return self._evaluate_with_keywords(user_answer, model_answer)