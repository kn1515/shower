from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class File(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   theme  = db.Column(db.String, nullable=False)
   author = db.Column(db.String, nullable=False)
   stars = db.Column(db.Integer, nullable=False)
   filename = db.Column(db.String, unique=True, nullable=False)
   filesize = db.Column(db.Integer, nullable=False)
   imgnum = db.Column(db.Integer, nullable=False)
   upload_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

   def __repr__(self):
       return '<File %r>' % self.filename
