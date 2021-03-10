import os
import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from flask import abort, request


AUTH0_DOMAIN = os.getenv('YOUR_AUTH0_DOMAIN', 'authtutorial.eu.auth0.com')
API_AUDIENCE = os.getenv('YOUR_API_IDENTIFIER', 'image')
ALGORITHMS = ['RS256']

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

'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
  def __init__(self, error_description, status_code):
    self.error_description = error_description
    self.status_code = status_code


def get_token_auth_header():
  '''
  returns token
  '''

  if 'Authorization' not in request.headers:
    abort(401)

  auth_header = request.headers['Authorization']
  header_parts = auth_header.split(' ')

  if len(header_parts) !=2:
    abort(401)
  elif header_parts[0].lower() != 'bearer':
    abort(401)

  return header_parts[1]


def check_permissions(permission, payload):
  '''
    @INPUTS
      permission: string permission (i.e. 'post:drink')
      payload: decoded jwt payload
    @returns
      True if permissions are available
  '''
  if 'permissions' not in payload:
    raise AuthError({
      'status_code': 'invalid_claims',
      'error_description': 'Permissions not included in JWT.'
      }, 400)

  if permission not in payload['permissions']:
    raise AuthError({
      'status_code': 'unauthorized',
      'error_description': 'Permission not found.'
      }, 403)
  return True


def verify_decode_jwt(token):
  # GET THE PUBLIC KEY FROM AUTH0
  jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
  jwks = json.loads(jsonurl.read())
  unverified_header = jwt.get_unverified_header(token)
  rsa_key = {}
  if 'kid' not in unverified_header:
      raise AuthError({
          'status_code': 'invalid_header',
          'error_description': 'Authorization malformed.'
      }, 401)

  for key in jwks['keys']:
      if key['kid'] == unverified_header['kid']:
          rsa_key = {
              'kty': key['kty'],
              'kid': key['kid'],
              'use': key['use'],
              'n': key['n'],
              'e': key['e']
          }  
  if rsa_key:
      try:
        # USE THE KEY TO VALIDATE THE JWT
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer='https://' + AUTH0_DOMAIN + '/'
        )
        return payload

      except jwt.ExpiredSignatureError:
          raise AuthError({
              'status_code': 'token_expired',
              'error_description': 'Token expired.'
          }, 401)
      except jwt.JWTClaimsError:
          raise AuthError({
              'status_code': 'invalid_claims',
              'error_description': 'Incorrect claims. Please, check the audience and issuer.'
          }, 401) 
      except Exception:
          raise AuthError({
              'status_code': 'invalid_header',
              'error_description': 'Unable to parse authentication token.'
          }, 400)
  
  raise AuthError({
              'status_code': 'invalid_header',
              'error_description': 'Unable to find the appropriate key.'
          }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except Exception as e:
                print(f'{Color.RED}Cannot verify the decoded jwt - Exception message:\n{e}{Color.END}')
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator