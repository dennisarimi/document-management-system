# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=False) # BLOB field to store file data
    # file_extension = db.Column(db.String(10), nullable=True)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    
    # upload functionality
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # delete functionality
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'category': self.category,
            'upload_date': self.upload_date.strftime('%d-%m-%Y %H:%M:%S')
        }