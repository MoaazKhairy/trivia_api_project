import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,PATCH,POST,DELETE,OPTIONS')
        return response
  
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        return jsonify({         
            'success': True,
            'total_categories': len(categories),
            'categories': {category.id: category.type for category in categories}
        })


    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        if (len(questions) == 0):
            abort(404)
        current_questions = paginate_questions(request, questions)
        if (len(current_questions) == 0):
            abort(404)
        else:
            try:
                current_categories = [question['category'] for question in current_questions]
                categerois = Category.query.order_by(Category.id).all()
                categerois = [cat.type for cat in categerois]
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(questions),
                    'current_category': current_categories,
                    'categories': categerois
                })
            except Exception:
                abort(422)
    
    @app.route('/questions/<int:question_id>')
    def retrieve_questions(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()   # select question by id which return one element or none
        if question is None:  # if none abort not found this id question
            abort(404)
        else:   # if existed return json format of this question only
            return jsonify ({
                'success': True,
                'question': question.format()   # format() method gives good format output
            })

            
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            print(question)
            if question is None:
                abort(404)
            
            question.delete()
            questions = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, questions)
            return jsonify({
            'success': True,
            'question': current_question,
            'number of questions': len(questions),
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
            'success': True,
            'created': question.id,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
            })
        except:
            abort(422)
   

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        try:
            if search_term:
                search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
                if len(search_results) == 0:    # in case of none will give resource not found
                    abort(422)
                return jsonify({
                    'success': True,
                    'questions': [question.format() for question in search_results],
                    'total_questions': len(search_results),
                    'current_category': None
                })
            abort(422)
        except:
            abort(422)
   

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        try:
            questions = Question.query.filter(Question.category == str(category_id)).all()
            if questions == []:    # in case of none will give resource not found
                abort(404)

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
        except:
            abort(404)
    
    @app.route('/quizzes', methods=['POST'])
    def do_quiz():
        try:
            body = request.get_json()
            
            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)
                
            quiz_category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if quiz_category['type'] == 'click':
                available_questions = Question.query.filter(
                Question.id.notin_((previous_questions))).all()
            else:
                available_questions = Question.query.filter_by(category=quiz_category['id']).filter(Question.id.notin_((previous_questions))).all()

            new_question = available_questions[random.randrange(0, len(available_questions))].format() if len(available_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })
        except:
            abort(422)
    
    
    ######## error handling ##########
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }),404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }),422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad_request"
        }),400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }),405

    return app

    