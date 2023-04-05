import pytest
from starlette.testclient import TestClient

from tj_feed.app import webapp


@pytest.fixture()
def client():
    with TestClient(webapp) as test_client:
        yield test_client
