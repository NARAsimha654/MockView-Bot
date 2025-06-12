# MockView-Bot 🤖

**MockView-Bot** is a smart, customizable mock interview chatbot designed to help students and job seekers prepare for technical interviews. Powered by the **Gemini API**, it offers a dynamic, interactive, and personalized practice experience that goes far beyond simple question-and-answer lists.

---

## 🚀 Features

### 🧠 Intelligent Interview Engine

- **Multiple Topics:** Covers core computer science areas like **DSA**, **C++**, **DBMS**, **Operating Systems**, and **System Design**.
- **Dynamic Questions:** Infinite supply of questions! When the pre-set bank is exhausted, the AI generates fresh ones.
- **Persistent Memory:** Uses browser `localStorage` to remember previously answered questions for a unique session each time.

### ✨ AI-Powered Learning Tools

- **Instant AI Feedback:** Get technical accuracy feedback and a score for each answer.
- **Mentor Mode (AI Personas) 🎓:** Choose your interviewer—**Friendly Teammate**, **Strict Senior Engineer**, or **Neutral Professional**.
- **AI-Generated Hints 💡:** Request subtle hints when stuck without spoiling the solution.
- **"Explain This Concept" Deeper Dives:** Click to get detailed, beginner-friendly explanations with analogies.

### 🎙️ Realistic Simulation

- **Voice Input & Output:** Use your voice to answer and hear questions for verbal communication practice.
- **User-Paced Flow:** Move forward only when you're ready—no pressure, just practice.

### 🧪 Personalization & Reporting

- **Custom JD-Based Interviews:** Paste any job description and get tailored interview questions based on required skills.
- **PDF Report Cards 📜:** Download a professional report after each session with your answers, scores, and AI feedback.

### 🎨 Professional User Experience

- **Modern UI:** Clean, multi-panel interface for a smooth experience.
- **Dark Mode 🌙:** Comfortable practice with a beautiful dark theme.
- **Extensible:** Add more pre-set questions via JSON or generate with the included script.

---

## 📁 Project Structure

```
MockView-Bot/
│
├── backend/
│   ├── app.py          # Flask server entry point
│   ├── evaluator.py    # Logic to evaluate answers
│   └── ...
│
├── data/
│   └── questions/      # Question banks per topic
│
├── frontend/
│   ├── index.html      # Main web page
│   ├── styles.css
│   └── script.js
│
└── ...
```

---

## 🛠️ Setup and Installation

### ✅ Prerequisites

- Python 3.8+
- pip (Python package manager)
- A modern web browser (Chrome or Edge recommended for best Web Speech API support)
- A code editor with Live Server support (like VS Code)

---

### 1. Clone the Repository & Set Up Environment

```bash
git clone <your-repo-url>
cd MockView-Bot

# Create and activate a virtual environment
# Windows:
python -m venv venv
venv\Scripts\activate

# macOS/Linux:
# python3 -m venv venv
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. PDF Generation Setup (WeasyPrint)

The PDF report card feature uses `WeasyPrint`, which requires some system-level dependencies.

📚 **WeasyPrint Installation Guide:** [https://weasyprint.readthedocs.io/en/stable/install.html](https://weasyprint.readthedocs.io/en/stable/install.html)

**For Windows users:**

- Download the GTK3 installer from the guide.
- Make sure you choose the version (32-bit or 64-bit) matching your Python installation.

### 3. Add Your Gemini API Key

Create a `.env` file in the root directory and add your Gemini API key:

```ini
# .env
GEMINI_API_KEY="your-api-key-here"
```

### 4. Run the Application

#### ✅ Start the Backend Server

```bash
cd backend
python app.py
```

Server runs at `http://127.0.0.1:5001`. Keep this terminal window open while using the app.

#### ✅ Start the Frontend (Live Server)

1. Open `MockView-Bot` in VS Code.
2. Right-click on `frontend/index.html` and choose "Open with Live Server".
3. Your app will launch in a browser at an address like `http://127.0.0.1:5500`.

---

### 💡 Contribute

Want to add more question topics or personas? Fork the repo, create a new feature branch, and submit a PR!

### 📜 License

MIT License. Feel free to use and modify this project for personal and educational use.

---

Made with 💻 by Narasimha Shastry B K
