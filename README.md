This package is a demonstration of a basic SQL-backed application with the following features
1. database integration with SQLModel and sqlite
2. JWT bearer token authentication/authorization
3. opentelemetry for
  * automatic tracelog for all http operations and sql queries
  * traceable python logs

To use:
1. python3 -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. fastapi dev
5. open a browser to http://localhost:8000/docs