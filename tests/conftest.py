import pytest
from starlette.config import environ
from starlette.testclient import TestClient

from app import webapp

environ['TESTING'] = 'TRUE'


@pytest.fixture()
def client():
    with TestClient(webapp) as test_client:
        yield test_client


@pytest.fixture()
def mocked_grabber(mocker):
    mocker.patch('app.grabber.fetch_last_comments', return_value=[])
