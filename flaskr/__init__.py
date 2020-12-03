import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    # Create a method to paginate questions returned
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={'/': {'origins': '*'}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        # Get all categories and add to dictionary
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        # Abort 404 if no categories found
        if (len(categories_dict) == 0):
            abort(404)

        # Return data
        return jsonify({
            'success': True,
            'categories': categories_dict
        }), 200

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the
    bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        # Get all questions and paginate
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        # Get all categories and add to dictionary
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        # Abort 404 if no questions found
        if (len(current_questions) == 0):
            abort(404)

        # Return data
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_dict
        }), 200

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            # Get the question by id
            question = Question.query.filter_by(id=id).one_or_none()

            # Abort 404 if no questions found
            if question is None:
                abort(404)

            # Else, delete the question
            question.delete()

            # Return data
            return jsonify({
                'success': True,
                'deleted': id
            })

        except:
            # Abort if problem deleting question
            abort(422)

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        # Get json data from request
        data = request.get_json()

        # Assign individual data from json data into variables
        question = data.get('question', '')
        answer = data.get('answer', '')
        difficulty = data.get('difficulty', '')
        category = data.get('category', '')
        # current_questions = paginate_questions(request, selection)

        # Get all questions and paginate
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        # Get all categories and add to dictionary
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        # Validate to ensure no data is empty
        if ((question == '') or (answer == '') or
                (difficulty == '') or (category == '')):
            abort(422)

        try:
            # Create a new question instance
            question = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category)

            # Save the question
            question.insert()

            # Return a success message
            return jsonify({
                # 'success': True,
                # 'message': 'Question successfully created!'
                # 'questions': paginated,
                # 'total_questions': len(Question.query.all())

                'success': True,
                'message': 'Question successfully created!',
                'questions': current_questions,
                'total_questions': total_questions,
                'categories': categories_dict
            }), 201

        except Exception:
            # Return 422 status code if there is an error
            abort(422)

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        # Get search term from request data
        data = request.get_json()
        search_term = data.get('searchTerm', '')

        # Return 422 status code if empty search term is sent
        if search_term == '':
            abort(422)

        try:
            # Get all questions that has the search term substring
            questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            # If there are no questions for search term return 404
            if len(questions) == 0:
                abort(404)

            # Paginate the questions
            paginated_questions = paginate_questions(request, questions)

            # Return a response if successful
            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(Question.query.all())
            }), 200

        except Exception:
            # Abort 404 if there is an error
            abort(404)

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        # Get the category by id
        category = Category.query.filter_by(id=id).one_or_none()

        # Abort 400 if the category is not found
        if (category is None):
            abort(400)

        # Get the matching questions
        selection = Question.query.filter_by(category=category.id).all()

        # Paginate the selection
        paginated = paginate_questions(request, selection)

        # Return the results
        return jsonify({
            'success': True,
            'questions': paginated,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def get_random_quiz_question():
        # Load the request body
        body = request.get_json()

        # Get the previous questions
        previous = body.get('previous_questions')

        # Get the category
        category = body.get('quiz_category')

        # Abort 400 if there is no data found
        if ((category is None) or (previous is None)):
            abort(400)

        # Load all questions if "ALL" is selected
        if (category['id'] == 0):
            questions = Question.query.all()
        # Load questions for the given category
        else:
            questions = Question.query.filter_by(category=category['id']).all()

        # Get the total number of questions
        total = len(questions)

        # Pick a random question
        def get_random_question():
            return questions[random.randrange(0, len(questions), 1)]

        # Check to see if question has already been used
        def check_if_used(question):
            used = False
            for q in previous:
                if (q == question.id):
                    used = True

            return used

        # Get a random question
        question = get_random_question()

        # Check if it is used, execute until an unused question is found
        while (check_if_used(question)):
            question = get_random_question()

            # If all questions have been tried,
            # return without question (for less than 5 questions)
            if (len(previous) == total):
                return jsonify({
                    'success': True
                })

        # Return the question
        return jsonify({
            'success': True,
            'question': question.format()
        })

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    return app
