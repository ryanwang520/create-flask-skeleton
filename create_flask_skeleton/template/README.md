# flask-starter-kit
Init for a flask app with minimal boilerplate

### features

1. simple validation
2. rest api friendly
3. Basic jwt auth with different audience
4. Sqalchemy integrated


### install poetry

    pip(x) install poetry


### install requirements

    poetry install

### running


1. Add APP_SETTINGS={your actual yaml config path}  to your .env file, APP_SETTINGS=config.yaml is a good default choice.

2. Add `FLASK_APP={{ app }}.main:app` and `FLASK_DEBUG=1`  to your .env file

3. Run `flask ishell`


5. Run tests `poetry run pytest tests`

3. Run server `poetry run flask run` or `poetry shell && flask run`


