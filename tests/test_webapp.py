

def test_index_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.template.name == 'index.html'


def test_limit_param_invalid(client):
    response = client.get('/?l=invalid')
    assert response.status_code == 200


def test_limit_comments(client):
    response = client.get('/?l=1000')
    assert response.status_code == 200
