from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class History(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    original = db.Column(
        db.Text,
        nullable=False
    )

    translated = db.Column(
        db.Text,
        nullable=False
    )