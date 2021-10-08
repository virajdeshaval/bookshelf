import os
import unittest
import json

from flaskr import create_app
from models import setup_db, Book
from flask_sqlalchemy import SQLAlchemy

class BookTestCase(unittest.TestCase):
    """This class represents the Bookshelf test case"""

    def setUp(self):
        # Created app
        self.app = create_app()
        # Setup client
        self.client = self.app.test_client
        # Set database name. Use different database for test so we never
        # manipulate PROD data
        self.database_name = "bookshelf_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('student', 'student','localhost:5432', self.database_name)
        # Create a database setup
        setup_db(self.app, self.database_path)

        # Create new book object
        self.new_book = {
            'title': 'Anansi Boys',
            'author': 'Neil Gaiman',
            'rating': 5
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        pass

    # 'name' is important
    # 1. starts with test
    # 2. followed by method name
    # 3. books should be paginated so, 'paginated_books'
    def test_get_paginated_books(self):
        # save response by using the client to get the endpoint
        res = self.client().get('/books')
        # load the data using json.loads
        data = json.loads(res.data)

        # Few things to be checked now.
        # 1. status_code = 200
        # 2. Success value of body = True
        # 3. Use assert true to check if there are total_books in data
        # 4. Use assert true to check if there are books in list
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))
    
    # I want to test '404 is sent beyond a valid page
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/books?page=1000', json={'rating': 1})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_update_book_rating(self):
        res = self.client().patch('/books/8', json={'rating': 1})
        data = json.loads(res.data)
        book = Book.query.filter(Book.id == 8).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(book.format()['rating'], 1)
        

    def test_400_for_failed_update(self):
        res = self.client().patch('/books/8')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')
    
    def test_delete_book(self):
        res = self.client().delete('/books/10')
        data = json.loads(res.data)

        book = Book.query.filter(Book.id == 10).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 10)
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))
        self.assertEqual(book, None)
        

    def test_422_if_book_does_not_exist(self):
        res = self.client().delete('/books/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
    
    def test_create_new_book(self):
        res = self.client().post('/books', json=self.new_book)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['books']))
    
    # def test_405_if_book_creation_not_allowed(self):
    #     res = self.client().post('/books/45', json=self.new_book)
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 405)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'method not allowed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()