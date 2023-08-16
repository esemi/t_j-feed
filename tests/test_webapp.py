async def test_top_users_endpoint(app_client):
    response = await app_client.get('/')
    assert response.status_code == 200
    assert response.headers.get('content-type') == 'text/html; charset=utf-8'


async def test_top_users_export_endpoint(app_client):
    response = await app_client.get('/top/export')
    assert response.status_code == 200
    assert response.headers.get('content-type') == 'text/plain; charset=utf-8'


async def test_limit_param_invalid(app_client):
    response = await app_client.get('/?l=invalid')
    assert response.status_code == 200


async def test_limit_top_users(app_client):
    response = await app_client.get('/?l=1000')
    assert response.status_code == 200
