import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Book

class BookTestCase(unittest.TestCase):
    """This class represents the Bookshelf test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        """Create an app"""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_testing"
        self.database_path = "postgres://{}:{}@{}/{}".format('student', 'student','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
        """Executed after reach test"""
        pass

# @TODO: Write at least two tests for each endpoint - one each for success and error behavior.
#        You can feel free to write additional tests for nuanced functionality,
#        Such as adding a book without a rating, etc. 
#        Since there are four routes currently, you should have at least eight tests. 
# Optional: Update the book information in setUp to make the test database your own! 
    def test_get_books(self):
        res = self.client().get('/books')
        # get the data into json format
        data = json.loads(res.data)

        # Add assertions
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], "The result is False")
        self.assertTrue(data['total_books'], "The result is False")
        self.assertIsNotNone(data['books'], "The result is False")

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/books?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_get_book_search_with_results(self):
        res = self.client().post('/books', json={'search': 'boys'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_books'])
        self.assertEqual(len(data['books']), 1)

    def test_get_book_search_without_results(self):
        res = self.client().post('/books', json={'search': 'butter'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_books'], 0)
        self.assertEqual(len(data['books']), 0)

    def test_update_book_rating(self):
        res = self.client().patch('/books/7', json={'rating': 5})
        data = json.loads(res.data)

        # get the book with id = 8, to check it's rating        
        book = Book.query.filter(Book.id == 7).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(book.format()['rating'], 5)

    def test_405_for_failed_update(self):
        res = self.client().patch('/books/7')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_delete_book(self):
        res = self.client().delete('/books/9')
        data = json.loads(res.data)

        # try to get the book you deleted
        book = Book.query.filter(Book.id == 9).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 9)
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))
        # to verify that book you deleted is no longer exists
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

    def test_405_if_book_creation_not_allowed(self):
        res = self.client().post('/books/45', json=self.new_book)        
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()