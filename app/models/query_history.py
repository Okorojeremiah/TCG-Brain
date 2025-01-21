from .database import db
from datetime import datetime


class QueryHistory(db.Model):
    __tablename__ = 'query_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query_text = db.Column(db.Text, nullable=False)
    response_text = db.Column(db.Text, nullable=True)
    session_id = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'query_text': self.query_text,
            'response_text': self.response_text,
            'session_id': self.session_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') 
        }
        
    