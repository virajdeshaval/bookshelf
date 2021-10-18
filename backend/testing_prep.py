# Import all dependencies
import unittest
import json
from flaskr import create_app
from models import setup_db

# Create Test Case based on resource
class BooksTestCase(unittest.TestCase):
    def setup(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "test_db"
        self.database_path = "postgres://{}/{}".format("localhost:5432", self.database_name)

        setup_db(self.app, self.database_path)
    
    def tearDown(self):
        pass
    
    def test_given_behaviour(self):
        res = self.client().get('/')

        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()