from .database import db
from datetime import datetime
import json


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False)  # 'User' or 'AI'
    content = db.Column(db.Text, nullable=False) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    edit_count = db.Column(db.Integer, default=0)
    edits = db.Column(db.Text, nullable=True)
    
    chat = db.relationship('Chat', back_populates='messages')

    def to_dict(self):
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'edit_count': self.edit_count,
            'edits': json.loads(self.edits) if self.edits else []
        }
