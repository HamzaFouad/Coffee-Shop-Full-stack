import os
from flask import Flask, request, jsonify, abort, redirect, url_for
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.exceptions import Unauthorized

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

class Color:
  PURPLE = '\033[95m'
  CYAN = '\033[96m'
  DARKCYAN = '\033[36m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  END = '\033[0m'


OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
NOT_PROCESSABLE = 422
UNAUTHORIZED = 401

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

# db_drop_and_create_all()

# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  

## ROUTES
@app.route('/', methods=['GET'])
def home():
  print(f'{Color.GREEN}Application restarted!{Color.END}')
  print(f'{Color.GREEN}And running on http://127.0.0.1:5000/{Color.END}')
  return 'Empty HOME Directory'

@app.route('/drinks', methods=['GET'])
def get_drinks():
  drinks = Drink.query.all()

  return jsonify({
      'success': True,
      'drinks': [drink.short() for drink in drinks]
  }), OK


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
  drinks = Drink.query.all()

  return jsonify({
    'drinks': [drink.short() for drink in drinks],
    'success': True
  }), OK


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):
  body = request.get_json()
  title = body.get('title', None)
  recipe = body.get('recipe', None)

  if None in (title, recipe):
    print(f'{Color.RED}Failed to POST a drink: There is a None Value.\ntitle:{title}, recipe:{recipe}{Color.END}')
    abort(BAD_REQUEST)

  try:
    created_drink = Drink(
      title = title,
      recipe = json.dumps(recipe)
    )
    created_drink.insert()
    return jsonify({
      'success': True,
      'drinks': [created_drink.long()]
    }), OK
  except Exception as e:
    print(f'{Color.RED}EXCEPTION ERROR WHEN POSTING:\n{e}{Color.END}')
    abort(BAD_REQUEST)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drink(jwt, id):
  '''
  Modify either the title of the drink, recipe or both.
  '''
  drink = Drink.query.get(id)
  if drink is None:
    print(f'{Color.RED}Failed to PATCH the drink: Error "drink is None"{Color.END}')
    abort(NOT_FOUND)
  
  body = request.get_json()

  if body is None:
    print(f'{Color.RED}Failed to PATCH the drink: Error "body is None"{Color.END}')
    abort(BAD_REQUEST)
  
  title = body.get('title', None)
  recipe = body.get('recipe', None)
  
  if title is None:
    title = drink.title
  
  if recipe is None:
    recipe = json.loads(drink.recipe)

  if None in (title, recipe):
    print(f'{Color.RED}Failed to PATCH the drink: There is a None Value.\ntitle:{title}, recipe:{recipe}"{Color.END}')
    abort(BAD_REQUEST)
  
  try:
    drink.title = title
    drink.recipe = json.dumps(recipe)
    drink.update()
    return jsonify({
      'success': True,
      'drinks': [drink.long()]
    }), OK
  except Exception as e:
    print(f'{Color.RED}EXCEPTION ERROR WHEN PATCHING:\n{e}{Color.END}')
    abort(BAD_REQUEST)
  

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
  drink = Drink.query.get(id)
  
  if drink is None:
    print(f'{Color.RED}Failed to DELETE the drink: Error "drink is None"{Color.END}')
    abort(NOT_FOUND)

  try:
    drink.delete()
    return jsonify({
      'success': True,
      'delete': drink.id
    }), OK
  except Exception as e:
    print(f'{Color.RED}EXCEPTION ERROR WHEN DELETING:\n{e}{Color.END}')
    abort(BAD_REQUEST)


## Error Handling
@app.errorhandler(BAD_REQUEST)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": BAD_REQUEST,
        "message": "BAD REQUEST"
    }), BAD_REQUEST

@app.errorhandler(NOT_FOUND)
def not_found(error):
  return jsonify({
    "success": False, 
    "error": NOT_FOUND,
    "message": "RESOURCE NOT FOUND"
    }), NOT_FOUND

@app.errorhandler(NOT_PROCESSABLE)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": NOT_PROCESSABLE,
        "message": "NOT PROCESSABLE"
    }), NOT_PROCESSABLE
