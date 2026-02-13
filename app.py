import os
import pdfplumber
from flask import Flask, render_template, request, jsonify, session
# Import lines check karein
from planner import generate_advanced_plan, generate_topic_quiz, extract_text_from_pdf

app = Flask(__name__)
app.secret_key = 'bhaitensionmatlo'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/plan')
def plan_page():
    current_plan = session.get('plan', []) 
    
    # Agar data nahi hai toh msg dikhao
    if not current_plan:
        return "Bhai, pehle topics dalo ya PDF upload karo! <a href='/'>Wapas Jao</a>"
        
    return render_template('plan.html', 
                           plan=current_plan, 
                           subject=session.get('subject', 'My Study Plan'),
                           hours=session.get('hours', '1'),
                           success_chance="95%")

                      

@app.route('/generate', methods=['POST'])
def generate():
    subject = request.form.get('subject', 'General Study')
    hours = request.form.get('hours', '1')
    start_time = request.form.get('start_time', '09:00')

    names = request.form.getlist('topic_name[]')
    diffs = request.form.getlist('difficulty[]')
    
    topics_data = [{'name': n, 'difficulty': d} for n, d in zip(names, diffs) if n.strip()]

    if not topics_data:
        return "Please add the Topic!"

    # PDF text pass karne ki zaroorat nahi hai ab
    result = generate_advanced_plan(topics_data, hours, start_time)

    return render_template('plan.html', plan=result, subject=subject, hours=hours, success_chance="95%")

@app.route('/get_quiz', methods=['POST'])
def get_quiz():
    data = request.get_json()
    topic = data.get('topic')
    return jsonify(generate_topic_quiz(topic))

if __name__ == '__main__':
    app.run(debug=True)