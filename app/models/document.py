from .database import db
from datetime import datetime
from sqlalchemy import UniqueConstraint

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(50), nullable=False, default="user")  

    user = db.relationship('User', back_populates='documents')

    __table_args__ = (
        UniqueConstraint('id', 'source', name='uq_document_id_source'),  
    )

  