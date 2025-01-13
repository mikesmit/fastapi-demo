from .jwt_decoder import JWTDecoder

# Based on the auth0 article: https://auth0.com/blog/build-and-secure-fastapi-server-with-auth0/

optional_auth = JWTDecoder(auto_error=False)
'''
Checks the bearer token, if the bearer token is not valid or does not exist, returns None
'''

auth = JWTDecoder()
'''
Checks the bearer token. If it is not valid throws an HTTPException, otherwise returns the token.
'''

    