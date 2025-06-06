# tests/conftest.py
import pytest
from main import app as flask_app

@pytest.fixture
def app():
    # Enables testing mode
    flask_app.config.update({
        "TESTING": True
    })
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()
