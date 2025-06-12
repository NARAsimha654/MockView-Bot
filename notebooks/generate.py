# notebooks/generate.py
import google.generativeai as genai
import os
import json
import argparse
from dotenv import load_dotenv

# --- SETUP ---

def setup_api():
    """Load environment variables and set up the Gemini API key."""
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API key not found. Make sure it's in a .env file as GEMINI_API_KEY.")
    
    genai.configure(api_key=api_key)
    print("Gemini API key configured successfully.")

# --- CORE FUNCTIONS ---

def generate_questions(topic: str, num_questions: int, difficulty: str) -> list | None:
    """
    Generates interview questions for a given topic using the Gemini API.
    """
    print(f"Generating {num_questions} questions for topic: '{topic}' with Gemini...")

    topic_prefix = topic.split()[0].lower().replace('+', 'p')

    # Configure the model - gemini-1.5-flash is fast and capable
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Instructions for the model
    prompt = f"""
    Generate exactly {num_questions} technical interview questions about '{topic}'.
    
    For each question, provide:
    1. A unique 'id' starting with the prefix '{topic_prefix}-' followed by a three-digit number.
    2. The 'question' itself.
    3. A concise, accurate 'answer' (around 2-4 sentences).
    4. A 'difficulty' level, which should be '{difficulty}'.
    5. A list of 'tags' including '{topic}'.

    Return the output as a valid JSON object containing a single key "questions"
    which holds a list of the question objects. Do not include any text, markdown formatting,
    or ```json ``` wrappers before or after the JSON object itself.
    """

    try:
        # Generate content with specific generation config for JSON output
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        generated_data = json.loads(response.text)
        return generated_data.get("questions") # Extract the list
    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        # Sometimes the model might still wrap the JSON in markdown, let's try to fix it
        try:
            print("Attempting to fix potential JSON formatting issues...")
            fixed_text = response.text.strip().replace('```json', '').replace('```', '')
            generated_data = json.loads(fixed_text)
            return generated_data.get("questions")
        except Exception as fix_e:
            print(f"Could not fix JSON: {fix_e}")
            return None


def save_questions(output_filename: str, new_questions: list):
    """Saves generated questions to the data directory."""
    filepath = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions', output_filename)
    
    print(f"Preparing to save questions to {filepath}...")
    try:
        with open(filepath, 'r') as f:
            existing_questions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_questions = []

    existing_questions.extend(new_questions)

    with open(filepath, 'w') as f:
        json.dump(existing_questions, f, indent=2)
        
    print(f"Successfully saved {len(new_questions)} new questions to {filepath}")


# --- MAIN EXECUTION BLOCK ---
def main():
    parser = argparse.ArgumentParser(description="Generate interview questions using the Gemini API.")
    parser.add_argument("topic", type=str, help="The topic for the interview questions.")
    parser.add_argument("--num_questions", "-n", type=int, default=3, help="Number of questions to generate.")
    parser.add_argument("--difficulty", "-d", type=str, default="medium", choices=["easy", "medium", "hard"])
    parser.add_argument("--output_file", "-o", type=str, help="Output JSON file name.")
    args = parser.parse_args()
    
    output_file = args.output_file or f"{args.topic.split()[0].lower().replace('+', 'p')}.json"

    try:
        setup_api()
        questions = generate_questions(args.topic, args.num_questions, args.difficulty)
        if questions:
            print("\n--- Generated Questions ---")
            print(json.dumps(questions, indent=2))
            print("-------------------------\n")
            if input("Save these questions? (y/n): ").lower() == 'y':
                save_questions(output_file, questions)
        else:
            print("Failed to generate questions.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()