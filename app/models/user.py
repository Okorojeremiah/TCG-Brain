from .database import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    job_role = db.Column(db.String(50), nullable=False)
    session_id = db.Column(db.String(36), nullable=True)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)  
    documents = db.relationship('Document', back_populates='user')
    
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "job_role": self.job_role,
            "is_superuser": self.is_superuser
        }
