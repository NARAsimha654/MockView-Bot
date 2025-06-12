// frontend/script.js
document.addEventListener('DOMContentLoaded', () => {
    // --- ELEMENT SELECTORS ---
    const topicListContainer = document.getElementById('topic-list');
    const welcomeView = document.getElementById('welcome-view');
    const chatView = document.getElementById('chat-view');
    const summaryView = document.getElementById('summary-view');
    const chatWindow = document.getElementById('chat-window');
    const answerInput = document.getElementById('answer-input');
    const submitBtn = document.getElementById('submit-answer-btn');
    const endInterviewBtn = document.getElementById('end-interview-btn');
    const themeToggle = document.getElementById('theme-toggle');
    const jdInput = document.getElementById('jd-input');
    const startCustomBtn = document.getElementById('start-custom-btn');
    const micBtn = document.getElementById('mic-btn');
    const speakerToggle = document.getElementById('speaker-toggle');
    const personaBtns = document.querySelectorAll('.persona-btn');

    const API_URL = 'http://127.0.0.1:5001';
    const ANSWERED_IDS_KEY = 'mockview_answered_ids';

    // --- STATE MANAGEMENT ---
    let isAwaitingAnswer = false;
    let currentQuestionId = null;
    let currentQuestionText = "";
    let sessionHistory = [];
    let isMuted = false;
    let isRecording = false;
    let selectedPersona = 'Neutral'; // Default persona

    // --- THEME SWITCHER LOGIC ---
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        document.body.classList.add(currentTheme);
        if (currentTheme === 'dark-mode') themeToggle.checked = true;
    }
    themeToggle.addEventListener('change', function() {
        if (this.checked) { document.body.classList.add('dark-mode'); localStorage.setItem('theme', 'dark-mode'); } 
        else { document.body.classList.remove('dark-mode'); localStorage.setItem('theme', 'light-mode'); }
    });

    // --- BROWSER SPEECH APIS ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = true; recognition.interimResults = true;
        recognition.onresult = (event) => { let final_transcript = ''; for (let i = event.resultIndex; i < event.results.length; ++i) { final_transcript += event.results[i][0].transcript; } answerInput.value = final_transcript; };
        recognition.onerror = (event) => { console.error("Speech recognition error:", event.error); if (event.error === 'not-allowed') alert("Microphone permission was denied. Please allow it in your browser settings."); isRecording = false; micBtn.classList.remove('recording'); };
        recognition.onend = () => { isRecording = false; micBtn.classList.remove('recording'); };
    } else { if(micBtn) micBtn.style.display = 'none'; }
    const stripHtml = (html) => { const doc = new DOMParser().parseFromString(html, 'text/html'); return doc.body.textContent || ""; }
    const speak = (text) => { if (isMuted || typeof speechSynthesis === "undefined") return; speechSynthesis.cancel(); const cleanText = stripHtml(text); const utterance = new SpeechSynthesisUtterance(cleanText); speechSynthesis.speak(utterance); };

    // --- LOCALSTORAGE & UI HELPERS ---
    const getAnsweredIdsFromStorage = () => JSON.parse(localStorage.getItem(ANSWERED_IDS_KEY)) || [];
    const addAnsweredIdToStorage = (id) => { if (id && id.startsWith('dynamic-')) return; const answeredIds = getAnsweredIdsFromStorage(); if (id && !answeredIds.includes(id)) { answeredIds.push(id); localStorage.setItem(ANSWERED_IDS_KEY, JSON.stringify(answeredIds)); } };
    const addMessage = (text, sender, className = '') => { const messageDiv = document.createElement('div'); messageDiv.classList.add('message', `${sender}-message`); if (className) messageDiv.classList.add(className); messageDiv.innerHTML = text; chatWindow.appendChild(messageDiv); chatWindow.scrollTop = chatWindow.scrollHeight; if (sender === 'bot') speak(text); return messageDiv; };
    const displaySummary = () => { let averageScore = 0; let finalMessage = "<h1>Interview Ended</h1><p>You didn't answer any questions.</p><button id='restart-interview-btn'>Practice Another Topic</button>"; if (sessionHistory.length > 0) { averageScore = Math.round(sessionHistory.reduce((acc, cur) => acc + cur.score, 0) / sessionHistory.length); finalMessage = `<h1>Interview Complete!</h1><div class="score-circle">${averageScore}%</div><p>You answered ${sessionHistory.length} question(s) with an average score of ${averageScore}%.</p><div><button id="restart-interview-btn">Practice Another Topic</button><button id="download-report-btn" class="download-report-button">Download Report</button></div>`; } summaryView.innerHTML = finalMessage; document.getElementById('restart-interview-btn').addEventListener('click', resetToHome); const downloadBtn = document.getElementById('download-report-btn'); if (downloadBtn) { downloadBtn.addEventListener('click', async () => { downloadBtn.textContent = 'Generating...'; downloadBtn.disabled = true; try { const response = await fetch(`${API_URL}/generate-report`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ history: sessionHistory, summary: { count: sessionHistory.length, average_score: averageScore } }), credentials: 'include' }); if (!response.ok) throw new Error('Report generation failed.'); const blob = await response.blob(); const url = window.URL.createObjectURL(blob); const a = document.createElement('a'); a.style.display = 'none'; a.href = url; a.download = 'MockView_Report.pdf'; document.body.appendChild(a); a.click(); window.URL.revokeObjectURL(url); a.remove(); } catch (error) { console.error('Failed to download report:', error); alert('Could not download report.'); } finally { downloadBtn.textContent = 'Download Report'; downloadBtn.disabled = false; } }); }};
    const endTheInterview = () => { isAwaitingAnswer = false; if(isRecording) recognition.stop(); chatView.classList.add('hidden'); displaySummary(); summaryView.classList.remove('hidden'); speak(summaryView.textContent); };
    const resetToHome = () => { summaryView.classList.add('hidden'); chatView.classList.add('hidden'); welcomeView.classList.remove('hidden'); chatWindow.innerHTML = ''; sessionHistory = []; document.querySelectorAll('.topic-item, .persona-btn').forEach(item => item.classList.remove('active')); document.querySelector('.persona-btn[data-persona=\"Neutral\"]').classList.add('active'); selectedPersona = 'Neutral'; };
    
    // --- CORE API FUNCTIONS ---
    const fetchTopics = async () => { try { const response = await fetch(`${API_URL}/topics`,{credentials:'include'}); const topics = await response.json(); topicListContainer.innerHTML = ''; topics.forEach(topic => { const topicItem = document.createElement('div'); topicItem.className = 'topic-item'; topicItem.textContent = topic.toUpperCase(); topicItem.addEventListener('click', () => { document.querySelectorAll('.topic-item').forEach(item => item.classList.remove('active')); topicItem.classList.add('active'); startInterview(topic); }); topicListContainer.appendChild(topicItem); }); } catch (error) { console.error('Failed to fetch topics:', error); topicListContainer.innerHTML = '<p class="error">Could not load topics.</p>'; } };
    const startInterview = async (topic) => { sessionHistory = []; chatWindow.innerHTML = ''; try { const globally_answered_ids = getAnsweredIdsFromStorage(); await fetch(`${API_URL}/start`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic, globally_answered_ids, persona: selectedPersona}),credentials:'include'}); welcomeView.classList.add('hidden'); summaryView.classList.add('hidden'); chatView.classList.remove('hidden'); endInterviewBtn.classList.remove('hidden'); addMessage(`Great! Let's start with <strong>${topic.toUpperCase()}</strong>.`,'bot'); askQuestion(); } catch (error) { console.error('Failed to start interview:', error); } };
    const startCustomInterview = async (jd_text) => { sessionHistory = []; chatWindow.innerHTML = ''; try { const response = await fetch(`${API_URL}/start-custom-interview`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jd_text, persona: selectedPersona}),credentials:'include'}); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Failed to start custom interview.'); welcomeView.classList.add('hidden'); summaryView.classList.add('hidden'); chatView.classList.remove('hidden'); endInterviewBtn.classList.remove('hidden'); addMessage(`Excellent! I've analyzed the job description and created a custom interview for you. Let's begin.`,'bot'); askQuestion(); } catch (error) { console.error('Failed to start custom interview:', error); alert(`Error: ${error.message}`); } finally { startCustomBtn.textContent = 'Start Custom Interview'; startCustomBtn.disabled = false; } };
    const askQuestion = async () => { isAwaitingAnswer = false; currentQuestionId = null; currentQuestionText = ""; try { const response = await fetch(`${API_URL}/ask`,{credentials:'include'}); if (!response.ok) throw new Error(`Server responded with ${response.status}`); const data = await response.json(); if (data.status === 'complete') { endTheInterview(); } else if (data.status === 'question') { currentQuestionId = data.id; currentQuestionText = data.question; const questionHTML = `<div class="question-container"><span><strong>Question:</strong> ${currentQuestionText}</span><button class="hint-button" id="hint-btn-${currentQuestionId}">💡 Get a Hint</button></div>`; const messageElement = addMessage(questionHTML,'bot'); isAwaitingAnswer = true; const hintBtn = messageElement.querySelector(`#hint-btn-${currentQuestionId}`); if (hintBtn) { hintBtn.addEventListener('click', async () => { hintBtn.textContent = 'Getting hint...'; hintBtn.disabled = true; try { const hintResponse = await fetch(`${API_URL}/hint`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:currentQuestionText}),credentials:'include'}); const hintData = await hintResponse.json(); addMessage(`<strong>Hint:</strong> ${hintData.hint}`,'bot','hint-message'); } catch (e) { console.error("Hint fetch failed:", e); } }, { once: true }); } } } catch (error) { console.error('Failed to ask question:', error); } };
    const submitAnswer = async () => { const answer = answerInput.value.trim(); if (!answer || !isAwaitingAnswer) return; if (isRecording) { recognition.stop(); } isAwaitingAnswer = false; addMessage(answer, 'user'); answerInput.value = ''; addMessage('<i>Evaluating your answer...</i>','bot'); try { const response = await fetch(`${API_URL}/answer`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answer}),credentials:'include'}); const result = await response.json(); addAnsweredIdToStorage(currentQuestionId); sessionHistory.push({question:currentQuestionText,userAnswer:answer,score:result.score,feedback:result.feedback,modelAnswer:result.model_answer}); const feedbackHTML = `<strong>Feedback (Score: ${result.score}%)</strong>: ${result.feedback}<br><br><strong>Model Answer</strong>: ${result.model_answer}<div class="feedback-actions"><button class="explanation-button" id="explain-btn-${currentQuestionId}">🎓 Explain Concept</button><button class="next-question-button" id="next-q-btn-${currentQuestionId}">Next Question →</button></div>`; const feedbackMessageElement = addMessage(feedbackHTML,'bot','feedback-message'); const explainBtn = feedbackMessageElement.querySelector(`#explain-btn-${currentQuestionId}`); if (explainBtn) { explainBtn.addEventListener('click', async () => { explainBtn.textContent = 'Thinking...'; explainBtn.disabled = true; try { const explainResponse = await fetch(`${API_URL}/explain`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:currentQuestionText,answer:result.model_answer}),credentials:'include'}); const explainData = await explainResponse.json(); addMessage(`<strong>Deeper Dive:</strong><br>${explainData.explanation.replace(/\n/g,'<br>')}`,'bot','explanation-message'); } catch(e) { console.error("Explanation fetch failed:", e); } }, { once: true }); } const nextQuestionBtn = feedbackMessageElement.querySelector(`#next-q-btn-${currentQuestionId}`); if(nextQuestionBtn) { nextQuestionBtn.addEventListener('click', () => { askQuestion(); }, { once: true }); } } catch (error) { console.error('Failed to submit answer:', error); } };

    // --- EVENT LISTENERS ---
    personaBtns.forEach(btn => { btn.addEventListener('click', () => { personaBtns.forEach(pBtn => pBtn.classList.remove('active')); btn.classList.add('active'); selectedPersona = btn.dataset.persona; }); });
    speakerToggle.addEventListener('click', () => { isMuted = !isMuted; speakerToggle.classList.toggle('muted', isMuted); speakerToggle.textContent = isMuted ? '🔇' : '🔊'; if (!isMuted) speak("Voice enabled."); else speechSynthesis.cancel(); });
    if (micBtn) { micBtn.addEventListener('click', () => { if (isRecording) { recognition.stop(); } else { if (isAwaitingAnswer) { answerInput.value = ''; recognition.start(); } } }); }
    endInterviewBtn.addEventListener('click', endTheInterview);
    submitBtn.addEventListener('click', submitAnswer);
    answerInput.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitAnswer(); } });
    startCustomBtn.addEventListener('click', () => { const jdText = jdInput.value.trim(); if (!jdText) { alert("Please paste a job description first."); return; } startCustomBtn.textContent = 'Analyzing...'; startCustomBtn.disabled = true; startCustomInterview(jdText); });

    // --- INITIAL LOAD ---
    fetchTopics();
});