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
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    """
    Test for get_all_categories: Tests for the status code, if success is true, if categories is returned and the length of the returned categories
    """
    def test_get_all_categories(self):

        # Make the request and process the response
        response = self.client().get('/categories')
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)


    """
    Tests test_get_paginated_questions: Tests that question pagination is successful
    """
    def test_get_paginated_questions(self):

        # Get the response and load the data
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # Check for the total_questions and that the questions return data
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    """
    Tests test_404_request_beyond_valid_page: Tests that question pagination failure 404 is successful
    """
    def test_404_request_beyond_valid_page(self):

        # Send a request with bad page data and then load response
        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')


    """
    Tests test_create_new_question: Tests that a question can be created and is successful
    """
    def test_create_new_question(self):

        # Create variable for mock data to use as payload for post request
        mock_data_question_success = {
            'question': 'This is a question',
            'answer': 'This is a answer',
            'difficulty': 1,
            'category': 1,
        }

        # Creates the new question and loads the response data
        response = self.client().post('/questions', json=mock_data_question_success)
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully created!')
        

    """
    Tests test_422_if_question_creation_fails: Tests that  when a question is created and fails, an appropriate error response is delivered
    """
    def test_422_if_question_creation_fails(self):

        # Create variable for mock question data to use as payload for failed delete request
        mock_data_question_fail = {
            'question': '',
            'answer': '',
            'difficulty': 1,
            'category': 1,
        }

        # make request and process response
        response = self.client().post('/questions', json=mock_data_question_fail)
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    """
    Tests test_successful_question_delete: Tests that  when a question is deleted and is successful that it returns appropriate response
    """
    def test_successful_question_delete(self):

        # Create variable for mock question data to use as payload for successful delete request
        mock_question_id = Question(
            question='This is a mock test question.',
            answer='This is a mock test answer.',
            difficulty=1,
            category='1')

        # Insert the mock question into the database
        mock_question_id.insert()

        # Return the ID of the mock question
        return Question.id

        # Delete the mock question and process response
        response = self.client().delete(
            '/questions/{}'.format(mock_question_id))
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Question successfully deleted")

    """
    Tests test_delete_question_with_invalid_id: Tests that  when a question is deleted that does not exist, an appropriate error response is delivered
    """
    def test_delete_question_with_invalid_id(self):

        # This tests an invalid id was entered
        response = self.client().delete('/questions/asdfasdfasdf')
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    """
    Tests test_search_questions: Tests that  when a search term is entered it returns a successful response if it exists in the database
    """
    def test_search_questions(self):

        # Make the request and process the response
        response = self.client().post('/questions/search', json={'searchTerm': 'largest lake in Africa'})
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    """
    Tests test_empty_search_term_response: Tests for an empty search term is entered it returns the appropriate error code
    """
    def test_empty_search_term_response(self):
        
        # Initiate an empty search request and process response
        response = self.client().post('/questions/search', json={'searchTerm': ''})
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    """
    Tests test_search_term_not_found: Tests for a search term value that does not exist in the database and returns the appropriate error code
    """
    def test_search_term_not_found(self):

        # Initiate a search request for something that does not exist in the database and process response
        response = self.client().post('/questions/search', json={'searchTerm': 'asdfasdfasdf'})
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    """
    Tests test_get_questions_by_category: Tests to retrieve the questions for a given category
    """
    def test_get_questions_by_category(self):

        # Initiate a request for the Science category with an ID of 1
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

       # Check the status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    """
    Tests test_if_questions_by_category_fails: Tests to retrieve the questions for a given category that does not exist and return the appropriate error
    """
    def test_if_questions_by_category_fails(self):

        # Send request with a category ID of 111, which does not exist
        response = self.client().get('/categories/111/questions')
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    """
    Tests test_play_quiz_questions: Tests the trivia game with quiz questions
    """
    def test_play_quiz_questions(self):
        
        # Make the request and process the response
        response = self.client().post('/quizzes', json={'previous_questions': [5, 9], 'quiz_category': { 'type': 'History', 'id': 4}})
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        # Ensures the returned question is in the correct category
        self.assertEqual(data['question']['category'], 4)

        # Ensures that the questions from a previous quiz are not returned
        self.assertNotEqual(data['question']['id'], 5)
        self.assertNotEqual(data['question']['id'], 9)

    """
    Tests test_no_data_to_play_quiz: Tests the trivia game with no data returned from the application
    """
    def test_no_data_to_play_quiz(self):

        # Process the response from the request without sending data
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        # Check the status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()