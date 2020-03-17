import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def pagination_questions(request, selection):
	page = request.args.get('page', 1, type=int)
	start = (page - 1)* QUESTIONS_PER_PAGE
	end = start + QUESTIONS_PER_PAGE

	questions = [question.format() for question in selection]
	current_questions = questions[start:end]

	return current_questions

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__)
	setup_db(app)
	
	'''
	@TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
	'''
	cors = CORS(app, resources={r"/api/*":{"origins": "*"}})

	'''
	@TODO: Use the after_request decorator to set Access-Control-Allow
	'''
	@app.after_request
	def after_request(response):
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
		response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
		return response

	'''
	@TODO: 
	Create an endpoint to handle GET requests 
	for all available categories.
	'''
	@app.route('/categories')
	def get_categories():
		categories = list(map(Category.format, Category.query.all()))
		result = {
			"success": True,
			"categories": categories
		}
		return jsonify(result)


	'''
	@TODO: 
	Create an endpoint to handle GET requests for questions, 
	including pagination (every 10 questions). 
	This endpoint should return a list of questions, 
	number of total questions, current category, categories. 

	TEST: At this point, when you start the application
	you should see questions and categories generated,
	ten questions per page and pagination at the bottom of the screen for three pages.
	Clicking on the page numbers should update the questions. 
	'''
	@app.route('/questions')
	def get_questions():
		selection = Question.query.order_by(Question.id).all()
		categories = list(map(Category.format,Category.query.all()))
		current_questions = pagination_questions(request, selection)

		if len(current_questions) == 0:
			abort(404)

		return jsonify({
			'success': True,
			'categories': categories,
			'questions': current_questions,
			'total_questions': len(Question.query.all()),
			'current_category': None,
			})

	'''
	@TODO: 
	Create an endpoint to DELETE question using a question ID. 

	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page. 
	'''
	@app.route('/questions/<int:question_id>', methods=['DELETE'])
	def delete_question(question_id):
		try:
			question = Question.query.filter(Question.id == question_id).one_or_none()

			if question is None:
				abort(404)

				question.delete()
				selection = Question.query.order_b(Question.id).all()
				current_questions = pagination_questions(request, selection)

				return jsonify({
					'success': True,
					'questions': current_questions,
					'total_questions': len(Question.query.all()),
					'deleted': question_id
					})

		except:
			abort(442)

	'''
	@TODO: 
	Create an endpoint to POST a new question, 
	which will require the question and answer text, 
	category, and difficulty score.

	TEST: When you submit a question on the "Add" tab, 
	the form will clear and the question will appear at the end of the last page
	of the questions list in the "List" tab.  
	'''
	@app.route('/questions', methods=["POST"])
	def add_question():
		body = request.get_json()

		new_question = body.get('question', None)
		new_answer = body.get('answer', None)
		new_category = body.get('category', None)
		new_difficulty = body.get('difficulty', None)

		try:
			question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
			question.insert()

			selection = Question.query.order_by(Question.id).all()
			current_questions = pagination_questions(request, selection)

			return jsonify({
				'success': True,
				'question':current_questions,
				'total_questions': len(Question.query.all()),
				'created':question.id
				})
		except:
			abort(442)
	'''
	@TODO: 
	Create a POST endpoint to get questions based on a search term. 
	It should return any questions for whom the search term 
	is a substring of the question. 

	TEST: Search by any phrase. The questions list will update to include 
	only question that include that string within their question. 
	Try using the word "title" to start. 
	'''
	@app.route('/serachQuestions', methods=['POST'])
	def search_questions():
		if request.data:
			page = 1
			if request.args.get('page'):
				page = int(request.args.get('page'))
			search = json.loads(request.data.decode('utf-8'))
			if 'searchTerm' in search:
				question_query = Question.query.filter(Question.question.like('%' + search['searchTerm'] + '%')).paginate(page, QUESTIONS_PER_PAGE,False)

				questions = list(map(Question.format, question_query.items))
				if len(questions) > 0:
					result = {
						"success": True,
						"questions": questions,
						"total_questions": question_query.total,
						"current_category": None
					}
					return jsonify(result)
				abort(404)
			abort(442)

	'''
	@TODO: 
	Create a GET endpoint to get questions based on category. 

	TEST: In the "List" tab / main screen, clicking on one of the 
	categories in the left column will cause only questions of that 
	category to be shown. 
	'''
	@app.route('/categories/<int:category_id>/questions')
	def question_by_category(category_id):
		category_data = Category.query.get(category_id)
		page = 1
		if request.args.get('page'):
			page = int(request.args.get('page'))
		categories = list(map(Category.format, Category.query.all()))
		question_query = Question.query.filter_by(category=category_id).paginate(
			page, QUESTIONS_PER_PAGE, False)
		questions = list(map(Question.format, question_query.items))
		if len(questions) > 0:
			result={
				"success": True,
				"questions": questions,
				"total_questions":question_query.total,
				"categories": categories,
				"current_category": Category.format(category_data)
			}
			return jsonify(result)
		abort(404)


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
	def question_by_quiz():
		if request.data:
			search_data = json.loads(request.data.decode('utf-8'))
			if (('quiz_category' in search_data 
						and 'id' in search_data['quiz_category'])
							and 'previous_questions' in search_data):
					question_query = Question.query.filter_by(
						category=search_data['quiz_category']['id']
					).filter(
						Question.id.notin_(search_data["previous_questions"])
					).all()
					lenght_of_question  = len(question_query)
					if lenght_of_question > 0:
						result = {
							"success": True,
							"question": Question.format(question_query[random.randrage(0, lenght_of_question)])
						}
					else:
						result = {
							"success": True, 
							"question": None
						}
					return jsonify(result)
			abort(404)
		abort(422)
	'''
	@TODO: 
	Create error handlers for all expected errors 
	including 404 and 422. 
	'''

	@app.errorhandler(422)
	def unprocessable(error):
		return jsonify({
			"success": False,
			"error": 422,
			"message": "unprocessable"
			}), 422

	@app.errorhandler(422)
	def not_found(error):
		return jsonify({
			"success": False,
			"error" : 404,
			"message": "Resource Not Found"
			}), 404

	
	return app

		