import pytest


@pytest.fixture(autouse=True)
def mocked_grabber(mocker):
    mocker.patch('tj_feed.grabber.scrapper._request', return_value=dict())


def test_top_users_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.template.name == 'top.html'
    assert response.headers.get('content-type') == 'text/html; charset=utf-8'


def test_top_users_export_endpoint(client):
    response = client.get('/top/export')
    assert response.status_code == 200
    assert response.headers.get('content-type') == 'text/plain; charset=utf-8'


def test_limit_param_invalid(client):
    response = client.get('/?l=invalid')
    assert response.status_code == 200


def test_limit_top_users(client):
    response = client.get('/?l=1000')
    assert response.status_code == 200
