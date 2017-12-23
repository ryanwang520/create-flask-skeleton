# flask-starter-kit
init for an flask app with my opinioned understanding

### features

1. simple validation
2. rest api friendly
3. basic jwt auth with different audience
4. sqalchemy integrated


### install pipenv

    pip install pipenv


### install requirements

    pipenv install

### running


1. add APP_SETTINGS={your actual yaml config path}  to your .env file, APP_SETTINGS=config.yaml is a good default choice.

2. add `FLASK_APP={{ app }}.main:app` and `FLASK_DEBUG=1`  to your .env file

3. flask initdb

4. pip install -e .

5. python setup.py test

3. `pipenv run flask run` or `pipenv shell && flask run`


