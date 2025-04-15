import os, csv
from flask import Flask, redirect, render_template, jsonify, request, send_from_directory, flash, url_for
#from flask_cors import CORS
from sqlalchemy.exc import OperationalError, IntegrityError
from App.models import db, Book, Review, User
from datetime import timedelta

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    current_user,
    set_access_cookies,
    unset_jwt_cookies,
    current_user,
)


def create_app():
  app = Flask(__name__, static_url_path='/static')
  #CORS(app)
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
  app.config['DEBUG'] = True
  app.config['SECRET_KEY'] = 'MySecretKey'
  app.config['PREFERRED_URL_SCHEME'] = 'https'
  app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
  app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
  app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
  app.config["JWT_COOKIE_SECURE"] = True
  app.config["JWT_SECRET_KEY"] = "super-secret"
  app.config["JWT_COOKIE_CSRF_PROTECT"] = False
  app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
  app.app_context().push()
  return app


app = create_app()
db.init_app(app)

jwt = JWTManager(app)


@jwt.user_identity_loader
def user_identity_lookup(user):
  return user

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
  identity = jwt_data["sub"]
  return User.query.get(identity)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    flash("Your session has expired. Please log in again.")
    return redirect(url_for('login'))

# uncomment when models are implemented
def parse_books():
  with open('books.csv', encoding='unicode_escape') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
      book = Book(isbn=row['isbn'],
                  title=row['title'],
                  author=row['author'],
                  publication_year=int(row['pub_year']),
                  publisher=row['publisher'],
                  image=row['image_large'])
      db.session.add(book)
  db.session.commit()


def parse_reviews():
  with open('reviews.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
      review = Review(
        text=row['text'],
        rating=int(row['rating']),
        isbn=row['isbn'],
        user_id=row['user_id']
      )
      db.session.add(review)
    db.session.commit()


def create_users():
  rob = User(username="rob", password="robpass")
  bob = User(username="bob", password="bobpass")
  sally = User(username="sally", password="sallypass")
  pam = User(username="pam", password="pampass")
  chris = User(username="chris", password="chrispass")
  db.session.add_all([rob, bob])
  db.session.commit()


def initialize_db():
  db.drop_all()
  db.create_all()
  create_users()
  parse_books()
  parse_reviews()
  print('database intialized')


@app.route('/')
def login():
  initialize_db()
  return render_template('login.html')

#view routes
@app.route('/book/<isbn>/reviews')
@jwt_required()
def view_book_reviews(isbn):
  book = Book.query.filter_by(isbn=isbn).first()
  reviews = book.review

@app.route('/book/<string:book_isbn>')
def book_details(book_isbn):
  book = Book.query.filter_by(isbn=book_isbn).first()
  if not book:
    flash("Book not found.", "error")
    return redirect(url_for('home'))

  # Get all reviews for this book
  reviews = Review.query.filter_by(book_isbn=book_isbn).all()

  return render_template('index.html', books=Book.query.all(), selected_book=book, reviews=reviews)

@app.route('/login', methods=['POST'])
def login_action():
  username = request.form.get('username')
  password = request.form.get('password')
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    response = redirect(url_for('home'))
    access_token = create_access_token(identity=user.id)
    set_access_cookies(response, access_token)
    return response
  else:
    flash('Invalid username or password')
    return redirect(url_for('login'))


@app.route('/app')
@jwt_required()
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 8
    books = Book.query.paginate(page=page, per_page=per_page)

    selected_book_isbn = request.args.get('book_isbn')
    selected_book = Book.query.filter_by(isbn=selected_book_isbn).first() if selected_book_isbn else None
    
    return render_template('index.html', books=books, selected_book=selected_book, user=current_user)



@app.route('/logout')
def logout():
  response = redirect(url_for('login'))
  unset_jwt_cookies(response)
  flash('logged out')
  return response


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
