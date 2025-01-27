from .database import db
from datetime import datetime

class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(255), nullable=True) 
    started_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship('Message', back_populates='chat', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            "name": self.name,
            'started_at': self.started_at.strftime('%Y-%m-%d %H:%M:%S')
        }
