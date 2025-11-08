from http import HTTPStatus
from freezegun import freeze_time
import json

def test_autenticacao_jwt(client, add_user_bob):

    response = client.post(url='/auth/token',
                      data={
                              "username": add_user_bob.email,
                              "password": add_user_bob.clean_password
                          }
                      )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'


def test_autenticacao_jwt_username_errado(client, add_user_bob):

    response = client.post(url='/auth/token',
                      data={
                              "username": "wrong_user_name",
                              "password": add_user_bob.clean_password
                          }
                      )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == "email or password not found"


def test_autenticacao_jwt_password_errado(client, add_user_bob):

    response = client.post(url='/auth/token',
                      data={
                              "username": add_user_bob.email,
                              "password": "wrong_password"
                          }
                      )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == "email or password not found"


def test_token_expirado(client, add_user_bob):
    with freeze_time("2024-01-01 12:00:00"):
        response = client.post(url='/auth/token',
                        data={
                                "username": add_user_bob.email,
                                "password": add_user_bob.clean_password
                            }
                        )

        assert response.status_code == HTTPStatus.OK
        assert 'access_token' in response.json()
        assert response.json()['token_type'] == 'bearer'

    with freeze_time("2024-01-01 12:31:00"):
        id_usuario_existente = add_user_bob.id
        response = client.put(
            url=f'/usuario/{id_usuario_existente}',
            headers={'Authorization': f'Bearer {response.json()['access_token']}'},
            data=json.dumps(
                {
            "username": "test",
            "email": "test@example.com",
            "password": "test"
            }
            )
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json()['detail'] == "Could not validate credentials"
    
def test_refresh_token(client, get_token):

    response = client.post(url='/auth/refresh_token',
                           headers={'Authorization': f'Bearer {get_token}'}
                      )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'

def test_token_expirado_no_refresh_token(client, add_user_bob):
    with freeze_time("2024-01-01 12:00:00"):
        response = client.post(url='/auth/token',
                        data={
                                "username": add_user_bob.email,
                                "password": add_user_bob.clean_password
                            }
                        )

        assert response.status_code == HTTPStatus.OK
        assert 'access_token' in response.json()
        assert response.json()['token_type'] == 'bearer'

    with freeze_time("2024-01-01 12:31:00"):
        id_usuario_existente = add_user_bob.id
        response = client.post(url='/auth/refresh_token',
                           headers={'Authorization': f'Bearer {response.json()['access_token']}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json()['detail'] == "Could not validate credentials"