from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class ExamPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    total_hours = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('exam_plan.id'))
    name = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))