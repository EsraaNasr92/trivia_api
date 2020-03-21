import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy


from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres:159753@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.post_data = {
            'question': 'Test question',
            'answer': 'test answer',
            'difficulty': 2,
            'category': 4
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    def test_404_get_paginated_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_delete_question(self):
        res = self.client().delete('/questions/4')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)


    def test_404_delete_question(self):
        res = self.client().delete('/questions/90')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")
 

    def test_add_question(self):

        result = self.client().post('/questions', json=self.post_data)
        data = json.loads(result.data.decode('utf-8'))

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data[["created"]])
        sel.assertTrue(len(data["questions"]))

    def test_422_post_new_question(self):
        post_data = {
            'question': 'a',
            'answer': 'a',
            'category': '1', 
            'difficulty':'1'
        }
        res = self.client().post('/questions/45', json=post_data)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
 
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()