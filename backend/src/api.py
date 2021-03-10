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
  print('\n\n\n\n\n\n\n')
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
    

# Manager Token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjUyWjE0eUNFaGdoVzFnV1BuclVkdCJ9.eyJpc3MiOiJodHRwczovL2F1dGh0dXRvcmlhbC5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjA0NzA2YzkwZGM4NWIwMDY4MjQ5ZmY4IiwiYXVkIjoiaW1hZ2UiLCJpYXQiOjE2MTUzMzgwNzMsImV4cCI6MTYxNTM3NDA3MywiYXpwIjoiY0VNNmVrazhiUXByUTVGVEJEZnRpVndicWljOUZZOUQiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpkcmlua3MiLCJnZXQ6ZHJpbmtzLWRldGFpbCIsInBhdGNoOmRyaW5rcyIsInBvc3Q6ZHJpbmtzIl19.g6IV7Y8S6RvrCTxH1qK5oEaaXghXC8uYwP-Nq0ZkMWYEjtVajAPR7gZa2BYhPzjZlGY8JXj1QRZHCzdCF1k_t_pdh0qtOoCbvPKE79PUKSBlR96mucvE01rd3UL6lO7kCasmPlHb6H8wP8PevRhvSTuceud4yo0zu81xdMbIDOZL-Xg20d_TaNJ0fph0xnmonMJBBqykRYiemAbEAbx_P6MEnGaIcieuSfzXj85Viy5lqhjT9a2eH12FhVVtXQIlQz3FDQkrYXLqmfjAKy3qbCDXkRDdiQLJuK_P1VMHcosmwY0WzssaqClgrVnfAjuW7alamP3vC7Bjt3bmAeXLLQ
# Barista Token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjUyWjE0eUNFaGdoVzFnV1BuclVkdCJ9.eyJpc3MiOiJodHRwczovL2F1dGh0dXRvcmlhbC5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjA0ODUxNzkwZGM4NWIwMDY4MjU1OWVhIiwiYXVkIjoiaW1hZ2UiLCJpYXQiOjE2MTUzNTI5NTcsImV4cCI6MTYxNTM4ODk1NywiYXpwIjoiY0VNNmVrazhiUXByUTVGVEJEZnRpVndicWljOUZZOUQiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDpkcmlua3MtZGV0YWlsIl19.dRvUHYWOWWvQtMWHwvbHK1OSkIt2FEL2vrhqkR_fBO7sLL0u-s6IzK1rstpups3XE05d2V3rzUs_3bXYOcymX7a7kvm9_10vxpHMZ6lHFrYCuy2hqFCkUAs0hWV0v4zsNvTisPkM4skpzzGmBXOSwkTKTW5HWnsAPHxLCpFYb9BBMPrsox54VZyBptgZ7DYqSB4C93w5ydgcksC4sjziD6-x3bVhC52jcswr7hzoR2gbkKJh76aifKT8yxg4Ozl7TiFMME23MDO72RmLgLPGxLfLnN9kZX3PDsU9AsEmmwuiwKG1t-04PF3VgKHTFUb2hLFNvTcuAWAQHsJY_cJc0A
# https://authtutorial.eu.auth0.com/authorize?audience=image&response_type=token&client_id=cEM6ekk8bQprQ5FTBDftiVwbqic9FY9D&redirect_uri=https://localhost.com:8100/
