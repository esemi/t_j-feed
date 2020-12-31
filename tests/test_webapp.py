import pytest


@pytest.fixture(autouse=True)
def mocked_grabber(mocker):
    mocker.patch('tj_feed.grabber.scrapper._fetch_page', return_value=dict())


def test_index_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.template.name == 'index.html'


def test_feed_endpoint(client):
    response = client.get('/feed')
    assert response.status_code == 200
    assert response.headers.get('content-type') == 'text/plain; charset=utf-8'


def test_limit_param_invalid(client):
    response = client.get('/?l=invalid')
    assert response.status_code == 200


def test_limit_comments(client):
    response = client.get('/?l=1000')
    assert response.status_code == 200
