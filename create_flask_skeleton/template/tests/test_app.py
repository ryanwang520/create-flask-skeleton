from {{ app }}.app import create_app
import pytest


@pytest.fixture(scope="module")
def app():
    config = {
        "TESTING": True,
    }

    app = create_app(config=config)

    with app.app_context():
        # init_db(app)
        yield app


@pytest.fixture(scope="module")
def client(request, app):
    client = app.test_client()

    client.__enter__()
    request.addfinalizer(lambda: client.__exit__(None, None, None))

    return client


def test_home(client):
    rv = client.post("/test", json={"a": 12})
    assert rv.is_json
    assert rv.json["a"] == 12


def test_home_bad(client):
    rv = client.post("/test", json={"a": "str"})
    assert rv.is_json
    assert rv.status_code == 400
