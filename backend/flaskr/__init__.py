import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.orm.exc import NoResultFound


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
	#cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

	'''
	@TODO: Use the after_request decorator to set Access-Control-Allow
	'''
	@app.after_request
	def after_request(response):
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
		response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
		response.headers.add('Access-Control-Allow-Origins', '*')
		return response

	'''
	@TODO: 
	Create an endpoint to handle GET requests 
	for all available categories.
	'''
	@app.route('/categories')
	def get_categories():
		try:
			categories = Category.query.all()
			# Format categories to match front-end
			categories_dict = {}
			for category in categories:
				categories_dict[category.id] = category.type
				# return successful response
			return jsonify({
				'success': True,
				'categories': categories_dict
			}), 200
		except Exception:
			abort(404)


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

			categories_dict = {}
			for category in categories:
				categories_dict[category.id] = category.type

		return jsonify({
			'success': True,
			'categories': categories,
			'questions': current_questions,
			'total_questions': len(Question.query.all()),
			'current_category': None,
			}),200

	'''
	@TODO: 
	Create an endpoint to DELETE question using a question ID. 

	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page. 
	'''
	@app.route('/questions/<int:question_id>', methods=['DELETE'])
	def delete_question(question_id):
		try:
			question = Question.query.filter(Question.id == question_id).one()

			question.delete()
			selection = Question.query.order_by(Question.id).all()
			current_questions = pagination_questions(request, selection)
			return jsonify({
				'success': True,
				'deleted': question_id,
				'questions': current_questions,
				'total_questions': len(Question.query.all())
			}),200
		except NoResultFound:
			abort(404)
		except:
			abort(422)

	'''
	@TODO: 
	Create an endpoint to POST a new question, 
	which will require the question and answer text, 
	category, and difficulty score.

	TEST: When you submit a question on the "Add" tab, 
	the form will clear and the question will appear at the end of the last page
	of the questions list in the "List" tab.  
	'''
	@app.route('/questions', methods=['POST'])

	def add_question():
		body = request.get_json()

		new_question = body.get('question', None)
		new_answer = body.get('answer', None)
		new_category = body.get('category', None)
		new_difficulty = body.get('difficulty', None)

		try:
			question = Question(
				question=new_question,
				answer=new_answer,
				difficulty=new_difficulty,
				category=new_category)
			
			question.insert()
			
			selection = Question.query.order_by(Question.id).all()
			current_questions = pagination_questions(request, selection)

			return jsonify({
				'success': True,
				'created':question.id,
				'question':current_questions,
				'total_questions': len(Question.query.all())
			}), 200
		except: 
			#print("\nerror => {}\n".format(error)) 
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
	@app.route('/search', methods=['POST'])
	def search_questions():
		body = request.get_json()
		search = body.get('searchTerm', None)
		try:
			if search:
				questions =  Question.query.order_by(Question.id).filter(
					Question.question.ilike('%{}%'.format(search)))
				current_category = [question.category for question in questions]
				return jsonify({
					"questions": [question.format() for question in questions.all()],
					"total_questions": len(questions.all()),
					"current_category": current_category
				})
			else:
				abort(404)
		except:
			abort(404)

	'''
	@TODO: 
	Create a GET endpoint to get questions based on category. 

	TEST: In the "List" tab / main screen, clicking on one of the 
	categories in the left column will cause only questions of that 
	category to be shown. 
	'''
	@app.route('/categories/<int:category_id>/questions',methods=['GET'])
	def question_by_category(category_id):
		try:
			questions = Question.query.order_by(Question.id).filter_by(category=category_id)
			current_category = [question.category for question in questions]

			return jsonify({
				"questions": [question.format() for question in questions.all()],
				"total_questions": len(questions.all()),
				"current_category": current_category
			})
		except:
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
	def get_quiz_question():
		body = request.get_json()
		previous_questions = body.get('previous_questions', [])
		quiz_category = body.get('quiz_category', None)
		try:
			if quiz_category:
				if quiz_category['id'] == 0:
					selections = Question.query.all()
				else:
					selections = Question.query.filter_by(category=quiz_category['id']).all()
			options =  [question.format() for question in selections if question.id not in previous_questions]
			if len(options) == 0:
				return jsonify({
					'question': False
				})
			result = random.choice(options)
			return jsonify({
				'question': result
			})
		except:
			abort(500)
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

	@app.errorhandler(404)
	def not_found(error):
		return jsonify({
			"success": False,
			"error" : 404,
			"message": "Resource Not Found"
			}), 404

	
	return app

		