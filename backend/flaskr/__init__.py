import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there. 
#     If you do not update the endpoints, the lab will not work - of no fault of your API code! 
#   - Make sure for each route that you're thinking through when to abort and with which kind of error 
#   - If you change any of the response body keys, make sure you update the frontend to correspond. 
def paginate_books(request, selection):
	page = request.args.get('page', 1, type=int)
	start = (page - 1) * BOOKS_PER_SHELF
	end = start + BOOKS_PER_SHELF

	formatted_books = [book.format() for book in selection]
	current_books = formatted_books[start:end]
	
	return current_books


def retrieve_books():
	books = Book.query.order_by(Book.id).all()
	formatted_books = paginate_books(request, books)
	
	if not formatted_books:
		abort(404)
	else:
		return jsonify({
			'success': True,
			'books': formatted_books,
			'total_books': len(Book.query.all())
		})


def add_books():
	body = request.get_json()
	search = body.get('search', None)

	try:		
		if search:
			selection = Book.query.order_by(Book.id).filter(Book.title.ilike('%{}%'.format(search)))
			current_books = paginate_books(request, selection)

			return jsonify({
				'success': True,
				'books': current_books,
				'total_books': len(selection.all())
			})
		else:
			if (not body["title"]) or (not body["author"]):
				abort(406)
			book = Book(title=body["title"], author=body["author"], rating=body["rating"])
			book.insert()
			selection = Book.query.order_by(Book.id).all()
			current_books = paginate_books(request, selection)

			return jsonify({
				'success': True,
				'created': book.id,
				'books': current_books,
				'total_books': len(Book.query.all())
			})

		# return retrieve_books()
	except:
		abort(422)


def update_books(book_id):
	body = request.get_json()

	try:
		book = Book.query.filter(Book.id == book_id).one_or_none()
		
		if book is None:
			abort(400)
		
		if 'rating' in body:
			book.rating = int(body["rating"])
		
		book.update()

		return jsonify({
			'success': True,
			'id': book.id
		})
	except:
		abort(400)


def delete_books(book_id):
	body = request.get_json()

	try:
		book = Book.query.filter(Book.id == book_id).one_or_none()
		
		if book is None:
			abort(404)
		
		book.delete()
		selection = Book.query.order_by(Book.id).all()
		current_books = paginate_books(request, selection)

		return jsonify({
			'success': True,
			'deleted': book_id,
			'books': current_books,
			'total_books': len(Book.query.all())
		})
	except:
		abort(422)

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__)
	setup_db(app)
	CORS(app)

	# CORS Headers 
	@app.after_request
	def after_request(response):
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
		response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
		return response

	# @TODO: Write a route that retrieves all books, paginated. 
	#         You can use the constant above to paginate by eight books.
	#         If you decide to change the number of books per page,
	#         update the frontend to handle additional books in the styling and pagination
	#         Response body keys: 'success', 'books' and 'total_books'
	# TEST: When completed, the webpage will display books including title, author, and rating shown as stars

	@app.route('/books', methods=['GET', 'POST'])
	def get_create_books():
		if request.method == 'GET':
			return retrieve_books()
		if request.method == 'POST':
			return add_books()

	# @TODO: Write a route that will update a single book's rating. 
	#         It should only be able to update the rating, not the entire representation
	#         and should follow API design principles regarding method and route.  
	#         Response body keys: 'success'
	# TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
	@app.route('/books/<int:book_id>', methods=['PATCH', 'DELETE'])
	def update_delete_books(book_id):
		if request.method == 'PATCH':
			return update_books(book_id)
		if request.method == 'DELETE':
			return delete_books(book_id)

	# @TODO: Write a route that will delete a single book. 
	#        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
	#        Response body keys: 'success', 'books' and 'total_books'

	# TEST: When completed, you will be able to delete a single book by clicking on the trashcan.


	# @TODO: Write a route that create a new book. 
	#        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
	# TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books. 
	#       Your new book should show up immediately after you submit it at the end of the page. 
	@app.errorhandler(404)
	def not_found(error):
		return jsonify({
			"success": False, 
			"error": 404,
			"message": "resource not found"
			}), 404

	@app.errorhandler(422)
	def unprocessable(error):
		return jsonify({
			"success": False,
			"error": 422,
			"message": "unprocessable"
			}), 422

	@app.errorhandler(400)
	def bad_request(error):
		return jsonify({
			"success": False, 
			"error": 400,
			"message": "bad request"
			}), 400
	
	@app.errorhandler(406)
	def bad_request(error):
		return jsonify({
			"success": False, 
			"error": 406,
			"message": "not acceptable"
			}), 406

	@app.errorhandler(405)
	def bad_request(error):
		return jsonify({
			"success": False, 
			"error": 405,
			"message": "method not allowed"
			}), 405
	
	return app

