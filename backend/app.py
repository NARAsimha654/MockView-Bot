# backend/app.py
import os
import io
import time
import json
import random
from datetime import datetime
import google.generativeai as genai
from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from weasyprint import HTML

from question_router import QuestionRouter
from evaluator import Evaluator
from utils import get_available_topics

# --- SETUP AND INITIALIZATION ---
load_dotenv(dotenv_path="../.env")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-super-secret-key-that-should-be-changed'
CORS(app, origins="http://127.0.0.1:5500", supports_credentials=True)
question_router = QuestionRouter('../data/questions') 
evaluator = Evaluator()

# --- HELPER FUNCTIONS ---

def _get_persona_prompt(persona: str):
    """NEW: Returns the system prompt instruction based on the selected persona."""
    if persona == 'Friendly':
        return "You are an AI assistant acting as a friendly and encouraging teammate. Your tone should be collaborative and positive."
    elif persona == 'Strict':
        return "You are an AI assistant acting as a strict, direct senior engineer. You value accuracy and conciseness. Your response should be technical and to-the-point."
    else: # Neutral
        return "You are a helpful AI assistant. Your tone should be professional and neutral."

def _extract_skills_from_jd(jd_text: str):
    """Calls Gemini to extract skills from a job description."""
    try:
        print("Attempting to extract skills from JD...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        From the following job description, extract the 5 to 7 most important technical skills, programming languages, and key concepts.
        Return them as a valid JSON list of strings. Do not include soft skills. Job Description: "{jd_text}"
        """
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(response_mime_type="application/json"))
        skills = json.loads(response.text)
        print(f"Extracted skills: {skills}")
        return skills
    except Exception as e:
        print(f"Error extracting skills from JD: {e}")
        return []

def _get_dynamic_question(topic: str, persona: str = 'Neutral'):
    """Calls Gemini to generate a single, new question on the fly."""
    try:
        print(f"Attempting to dynamically generate a question for topic: {topic}")
        persona_instruction = _get_persona_prompt(persona)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        {persona_instruction}
        Generate a single, new, medium-difficulty technical interview question about '{topic}'.
        The question should be unique and not a simple definition.
        Return your response as a valid JSON object with two keys: "question" and "answer".
        The "answer" should be concise and accurate (2-4 sentences).
        """
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(response_mime_type="application/json"))
        data = json.loads(response.text)
        return {"id": f"dynamic-{int(time.time())}", "question": data["question"], "answer": data["answer"], "difficulty": "dynamic", "tags": [topic]}
    except Exception as e:
        print(f"Error generating dynamic question: {e}")
        return None

def _get_ai_hint(question: str, persona: str = 'Neutral'):
    """Calls Gemini API to generate a hint for a given question."""
    try:
        print(f"Attempting to generate a hint for question: {question[:30]}...")
        persona_instruction = _get_persona_prompt(persona)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        {persona_instruction}
        The user is stuck on the following technical interview question: "{question}"
        Your task is to provide a single, concise, one-sentence hint that guides the user toward the main concept, but does NOT give away the answer.
        """
        response = model.generate_content(prompt)
        print("Hint generated successfully.")
        return response.text
    except Exception as e:
        print(f"Error generating hint: {e}")
        return "Sorry, I couldn't generate a hint at this time."

def _get_ai_explanation(question: str, answer: str, persona: str = 'Neutral'):
    """Calls Gemini API to generate a detailed explanation of a concept."""
    try:
        print(f"Attempting to generate an explanation for question: {question[:30]}...")
        persona_instruction = _get_persona_prompt(persona)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Act as a patient and knowledgeable computer science tutor, with the personality of a {persona} interviewer.
        A user has just seen the answer to an interview question and wants to understand the core concept better.
        The question was: "{question}"
        The correct answer provided was: "{answer}"
        Your task is to explain the underlying concept in a simple, easy-to-understand way, matching your persona. Use an analogy if it helps.
        """
        response = model.generate_content(prompt)
        print("Explanation generated successfully.")
        return response.text
    except Exception as e:
        print(f"Error generating explanation: {e}")
        return "Sorry, I couldn't generate an explanation at this time."

# --- ROUTES ---

@app.route('/topics', methods=['GET'])
def list_topics():
    topics = get_available_topics('../data/questions')
    return jsonify(list(topics.keys()))

@app.route('/start', methods=['POST'])
def start_interview():
    data = request.json
    session.pop('interview_mode', None)
    session['persona'] = data.get('persona', 'Neutral') # Store persona
    session['topic'] = data.get('topic')
    session['globally_answered_ids'] = data.get('globally_answered_ids', [])
    session['asked_ids'] = []
    return jsonify({"message": f"Interview started for topic: {session['topic']}"})

@app.route('/start-custom-interview', methods=['POST'])
def start_custom_interview():
    data = request.json
    session['persona'] = data.get('persona', 'Neutral') # Store persona
    jd_text = data.get('jd_text')
    if not jd_text: return jsonify({"error": "Job description not provided"}), 400
    skills = _extract_skills_from_jd(jd_text)
    if not skills: return jsonify({"error": "Could not extract skills from the job description."}), 400
    custom_questions = []
    for skill in skills:
        question = question_router.find_question_by_tag(skill, excluded_ids=[q['id'] for q in custom_questions])
        if question: custom_questions.append(question)
    while len(custom_questions) < 5 and len(custom_questions) < len(skills):
        skill_to_use = random.choice(skills); dyn_question = _get_dynamic_question(skill_to_use, session['persona'])
        if dyn_question: custom_questions.append(dyn_question)
    if not custom_questions: return jsonify({"error": "Could not generate a custom interview."}), 400
    session['interview_mode'] = 'custom'; session['custom_questions'] = custom_questions; session['custom_question_index'] = 0
    return jsonify({"message": f"Custom interview created based on skills: {', '.join(skills)}"})

@app.route('/hint', methods=['POST'])
def get_hint():
    data = request.get_json(); question = data.get('question')
    if not question: return jsonify({"error": "Question not provided"}), 400
    hint = _get_ai_hint(question, session.get('persona', 'Neutral'))
    return jsonify({"hint": hint})

@app.route('/explain', methods=['POST'])
def get_explanation():
    data = request.get_json(); question = data.get('question'); answer = data.get('answer')
    if not question or not answer: return jsonify({"error": "Question and answer not provided"}), 400
    explanation = _get_ai_explanation(question, answer, session.get('persona', 'Neutral'))
    return jsonify({"explanation": explanation})

@app.route('/ask', methods=['GET'])
def ask_question():
    if 'topic' not in session and 'interview_mode' not in session: return jsonify({"error": "Session not started"}), 400
    persona = session.get('persona', 'Neutral')
    if session.get('interview_mode') == 'custom':
        q_index = session.get('custom_question_index', 0); q_list = session.get('custom_questions', [])
        if q_index >= len(q_list): return jsonify({"status": "complete", "message": "Congratulations! You've finished your custom interview."})
        question_data = q_list[q_index]; session['custom_question_index'] = q_index + 1
    else:
        topic = session['topic']; all_excluded_ids = list(set(session.get('asked_ids', [])).union(set(session.get('globally_answered_ids', []))))
        question_data = question_router.get_question(topic, all_excluded_ids)
        if not question_data: question_data = _get_dynamic_question(topic, persona)
        if not question_data: return jsonify({"status": "complete", "message": f"Congratulations! You've finished all available questions for the {topic.upper()} topic."})
    
    session['asked_ids'].append(question_data['id']); session['current_answer'] = question_data['answer']; session['current_question'] = question_data['question']; session.modified = True
    return jsonify({"status": "question", "id": question_data['id'], "question": question_data['question'], "difficulty": question_data['difficulty']})

@app.route('/answer', methods=['POST'])
def handle_answer():
    if 'current_answer' not in session: return jsonify({"error": "No active question"}), 400
    data = request.json; user_answer = data.get('answer'); model_answer = session['current_answer']; question = session['current_question']
    persona = session.get('persona', 'Neutral')
    if not user_answer: return jsonify({"error": "No answer provided"}), 400
    feedback, score = evaluator.evaluate(user_answer, model_answer, question, use_llm=True, persona=persona)
    del session['current_answer']; del session['current_question']; session.modified = True
    return jsonify({"feedback": feedback, "score": score, "model_answer": model_answer})
    
@app.route('/generate-report', methods=['POST'])
def generate_report():
    data = request.get_json(); history = data.get('history', []); summary = data.get('summary', {})
    question_blocks_html = ""
    for i, item in enumerate(history): question_blocks_html += f"""<div class="question-block"><h3>Question {i+1}:</h3><p>{item.get('question', 'N/A')}</p><p><strong>Your Score:</strong> {item.get('score', 'N/A')}%</p><p><strong>Feedback:</strong> {item.get('feedback', 'N/A')}</p><div class="model-answer"><strong>Model Answer:</strong> {item.get('modelAnswer', 'N/A')}</div></div>"""
    html_string = f"""
    <html><head><style>body {{ font-family: sans-serif; color: #333; }} h1 {{ color: #2b6cb0; border-bottom: 2px solid #2b6cb0; padding-bottom: 10px; }} h2 {{ color: #2c5282; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px;}} .summary-card {{ background-color: #edf2f7; padding: 20px; border-radius: 8px; margin-bottom: 30px; text-align: center; }} .question-block {{ margin-bottom: 25px; border-left: 3px solid #cbd5e0; padding-left: 15px; page-break-inside: avoid; }} .model-answer {{ background-color: #f7fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 5px; margin-top: 10px; }} p {{ line-height: 1.6; }} strong {{ color: #4a5568; }}</style></head>
    <body><h1>Interview Report Card</h1> <p>Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p><div class="summary-card"><h2>Performance Summary</h2><p><strong>Questions Answered:</strong> {summary.get('count', 'N/A')}</p><p><strong>Average Score:</strong> {summary.get('average_score', 'N/A')}%</p></div><h2>Detailed Breakdown</h2>{question_blocks_html}</body></html>
    """
    pdf = HTML(string=html_string).write_pdf()
    return send_file(io.BytesIO(pdf), mimetype='application/pdf', as_attachment=True, download_name='MockView_Report.pdf')

if __name__ == '__main__':
    app.run(debug=True, port=5001)