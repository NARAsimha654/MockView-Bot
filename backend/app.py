from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask_question():
    # Dummy implementation
    return jsonify({"question_id": "dummy_id", "question_text": "This is a dummy question?"})

@app.route('/answer', methods=['POST'])
def submit_answer():
    # Dummy implementation
    return jsonify({"result": "dummy_correct/incorrect", "explanation": "This is a dummy explanation."})

@app.route('/topics', methods=['GET'])
def get_topics():
    # Dummy implementation
    return jsonify({"topics": ["dummy_topic1", "dummy_topic2"]})

if __name__ == '__main__':
    app.run(debug=True)
