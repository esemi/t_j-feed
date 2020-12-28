from starlette.testclient import TestClient

from app import webapp


def test_html_feed_endpoint():
    with TestClient(webapp) as client:
        response = client.get('/')
        assert response.status_code == 200


def test_limit_param_invalid():
    with TestClient(webapp) as client:
        response = client.get('/?l=invalid')
        assert response.status_code == 200


def test_limit_comments():
    with TestClient(webapp) as client:
        response = client.get('/?l=1000')
        assert response.status_code == 200
