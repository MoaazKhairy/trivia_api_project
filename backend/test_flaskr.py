import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

########## create test class for unit testing #########
class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client      # setup the client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', '1234','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 3,
            'category': 3
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

    # # must start function name with 'test_' then descriptive name to method
    def test_get_pagination_questions(self):    ##test in success method about case of pagination of question
        res = self.client().get('/questions')      # set response that when client send get request to server
        data = json.loads(res.data)         # take data part from response as json format
        self.assertEqual(res.status_code, 200)      # access status code from Json Data to make equal assertion that equal 200 or not
        self.assertEqual(data['success'], True)     # check success argument that success
        self.assertTrue(data['current_category'])    # check if existed in response
        self.assertTrue(data['total_questions'])    # check if existed in response

    def test_404_sent_request_beyond_valid(self):   ##test in failed method about case of query parameter of page that not existed
        res = self.client().get('/questions?page=100')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_get_all_catagoris(self):   ##test in success method about case of query all categories
        res = self.client().get('/categories')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])

    def test_404_get_request_non_existing_category(self):
        res = self.client().get('/categories/100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        res=self.client().delete('/questions/10')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)

    def test_422_delete_request_not_valid(self):    ## not valid due to it is request delete not existed item
        res=self.client().delete('/questions/100')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)

    def test_405_create_question_beyond_not_valid(self):    ##that not allowed to post new question that existed in db already
        res = self.client().post('/questions/1', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "method not allowed")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()