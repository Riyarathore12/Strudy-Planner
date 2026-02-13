import os
import json
import PyPDF2
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- UTILITIES ---
def extract_text_from_pdf(file):
    try:
        # PyPDF2 fix
        reader = PyPDF2.PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages[:3]])
        return text
    except Exception as e:
        print(f"PDF Error: {e}")
        return ""

def generate_advanced_plan(topics, total_hours, start_time_str, pdf_context=""):
    # Topic names extraction fix
    topic_names = [t['name'] for t in topics] if topics else ["Study PDF Content"]
    ai_results = []
    
    try:
        # --- YE WALA BLOCK REPLACE KARO ---
        prompt = f"""
        Analyze the following text extracted from a PDF and create a study plan.
        TEXT CONTENT: {pdf_context[:4000]}

        INSTRUCTIONS:
        1. Identify 3-4 important main topics/chapters from THIS specific text.
        2. For each topic, create a funny Mnemonic to remember it.
        3. Provide a 'deep_dive' explanation based ONLY on the text provided.
        4. Do NOT talk about 'What is a PDF'. Focus on the SUBJECT matter inside the text.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Study Planner AI. Return ONLY a JSON object with the key 'plan'. Structure: {'plan': [{'name': 'Topic Name', 'mnemonic': 'memory trick', 'points': 'key points', 'deep_dive': 'detailed info'}]}"
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        # --- END OF REPLACE ---
        
        data = json.loads(completion.choices[0].message.content)
        ai_results = data.get('plan', [])
    except Exception as e:
        print(f"AI Error: {e}")
        ai_results = []

    # Time Calculation Logic
    try:
        current_time = datetime.strptime(start_time_str, "%H:%M")
    except:
        current_time = datetime.strptime("09:00", "%H:%M")

    plan_list = []
    # Division by zero protection
    num_topics = len(topics) if topics else 1
    study_mins = (float(total_hours) * 60) / num_topics

    for i, t in enumerate(topics):
        res = ai_results[i] if i < len(ai_results) else {}
        end_time = current_time + timedelta(minutes=study_mins)
        plan_list.append({
            "name": t['name'],
            "difficulty": t['difficulty'],
            "slot": f"{current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}",
            "mnemonic": res.get('mnemonic', "Recall key logic"),
            "quick_notes": res.get('points', "Review core concepts"),
            "explanation": res.get('deep_dive', "Detailed study recommended.")
        })
        current_time = end_time
    
    return plan_list
# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')
def generate_topic_quiz(topic):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Return ONLY JSON: {'questions': [{'q': '?', 'options': ['a','b','c','d'], 'correct': 0}]}"},
                {"role": "user", "content": f"3 MCQs for: {topic}"}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content).get('questions', [])
    except:
        return []

@app.route('/generate', methods=['POST'])
def generate():
    subject = request.form.get('subject', 'General')
    hours = request.form.get('hours', '2')
    start_time = request.form.get('start_time', '09:00')
    
    pdf_text = ""
    if 'pdf_file' in request.files:
        pdf_file = request.files['pdf_file']
        if pdf_file.filename != '':
            pdf_text = extract_text_from_pdf(pdf_file)

    topic_names = request.form.getlist('topic_name[]')
    difficulties = request.form.getlist('difficulty[]')
    
    topics_list = []
    for i, name in enumerate(topic_names):
        if name.strip():
            topics_list.append({
                "name": name.strip(),
                "difficulty": difficulties[i] if i < len(difficulties) else "Medium"
            })

    if not topics_list:
        return "Please add at least one topic."

    # final_plan is now a LIST
    final_plan = generate_advanced_plan(topics_list, hours, start_time, pdf_text)
    
    # Render Template - Note: plan=final_plan (No ['plan'] index used!)
    return render_template('planner.html', 
                           plan=final_plan, 
                           subject=subject, 
                           hours=hours, 
                           success_chance="95%")

if __name__ == '__main__':
    app.run(debug=True)