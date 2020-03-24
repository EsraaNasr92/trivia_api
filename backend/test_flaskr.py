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
        res = self.client().delete('/questions/16')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)


    def test_404_delete_question(self):
        res = self.client().delete('/questions/90')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")
 
    def test_post_new_question(self):
        res = self.client().post(
            '/questions', json=
            {
                'question': 'Add New Question Test?',
                'answer': 'yes',
                'difficulty': 3,
                'category': 3
            })
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(len(data['questions']), 2)

    def test_404_get_questions_by_category(self):
        res = self.client().get('/categories/10/question')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_get_search_with_result(self):
        res = self.client().post('/search', json={'searchTerm': "Tom"})
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(type(data['total_questions']), int)
        self.assertTrue(data['current_category'])
        self.assertTrue(data['questions'])

    def test_get_search_without_result(self):
        res = self.client().post('/search', json={'searchTerm': "Esraa"})
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(type(data['total_questions']), int)

    def test_quizzes(self):
        res = self.client().post('/quizzes', json={"previous_questions": [15, 16, 17], "quiz_category": {'id': 1, 'type': 'Science'}})
        data = json.loads(res.data.decode('utf-8'))

        self.assertTrue(data['question'])

    def test_quizzes_wrong_category(self):
        res = self.client().post('/quizzes', json={"previous_questions": [15, 16, 17], "quiz_category": {'id': 9, 'type': 'Science'}})
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()