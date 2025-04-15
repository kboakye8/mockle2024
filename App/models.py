from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)

  #relationships
  review = db.relationship('Review', backref='user', lazy=True)


  def __init__(self, username, password):
    self.username= username
    self.set_password(password)

  def set_password(self, password):
    self.password = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password, password)

    
class Book(db.Model):
  __tablename__ = 'book'
  isbn = db.Column(db.String, primary_key=True)
  author = db.Column(db.String(80), nullable=False)
  publication_year = db.Column(db.Integer(), nullable=False)
  publisher = db.Column(db.String(80), nullable=False)
  image = db.Column(db.String(255))
  title = db.Column(db.String(80), nullable=False)
  
  review = db.relationship('Review', backref='book', lazy=True)

  def add_review(self, user, text, rating):
    if not text or rating<1 or rating > 5:
      raise ValueError("Invalid review content or rating.")
    
    review = Review(text=text, book_isbn= self.isbn, user_id = user.id, rating=rating)

    db.session.add(review)
    db.session.commit()
    return review

  def delete_review(self, review):
    db.session.delete(review)
    db.session.commit()

  
class Review(db.Model):
  __tablename__ = 'review'
  id = db.Column(db.Integer, primary_key=True)
  book_isbn = db.Column(db.String, db.ForeignKey('book.isbn'), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  text = db.Column(db.Text, nullable=False)
  rating = db.Column(db.Integer, nullable=False)
