import click, csv
from flask import Flask
from flask.cli import with_appcontext
from App import app, Book, Review, initialize_db


@app.cli.command("init")
def initialize():
  initialize_db()


@app.cli.command("list-books")
def list_books():
  books = Book.query.all()
  print(books)