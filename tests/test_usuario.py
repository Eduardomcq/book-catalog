import json
from http import HTTPStatus


def test_post_novo_usuario(client):
    response = client.post(
        url="/usuario/",
        data=json.dumps({
        "username": "teste",
        "email": "teste@example.com",
        "password": "teste"
        })
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['username'] == "teste"
    assert response.json()['email'] == "teste@example.com"
    assert response.json()['id'] == 1


def test_post_conflito_usuario(client, add_user_bob):
    response = client.post(
        url="/usuario/",
        data=json.dumps({
        "username": "bob",
        "email": "teste@example.com",
        "password": "teste"
        })
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == "Username already created"


def test_post_conflito_email(client, add_user_bob):
    response = client.post(
        url="/usuario/",
        data=json.dumps({
        "username": "test",
        "email": "bob@example.com",
        "password": "teste"
        })
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == "Email already created"


def test_atualiza_usuario(client, add_user_bob, get_token):
    id_usuario_existente = add_user_bob.id
    response = client.put(
        url=f'/usuario/{id_usuario_existente}',
        headers={'Authorization': f'Bearer {get_token}'},
        data=json.dumps(
            {
        "username": "test",
        "email": "test@example.com",
        "password": "test"
        }
        )
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['id'] == 1
    assert response.json()['username'] == 'test'
    assert response.json()['email'] == 'test@example.com'


def test_atualiza_usuario_usuario_nao_encontrado(client, get_token):
    response = client.put(
        url=f'/usuario/{2}',
        headers={'Authorization': f'Bearer {get_token}'},
        data=json.dumps(
            {
        "username": "test",
        "email": "test@example.com",
        "password": "test"
        }
        )
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()['detail'] == 'Not enought permission'


def test_atualiza_usuario_conflito_usuario(
        client, add_user_bob, add_user_mark, get_token):
    response = client.put(
        url=f'/usuario/{add_user_bob.id}',
        headers={'Authorization': f'Bearer {get_token}'},
        data=json.dumps(
            {
        "username": "mark",
        "email": "test@example.com",
        "password": "test"
        }
        )
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == 'Email or Username already exists'


def test_deleta_usuario(client, add_user_bob, get_token):
    if_usuario_bob = add_user_bob.id
    response = client.delete(
        url=f'/usuario/{if_usuario_bob}',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['message'] == 'Account deleted'


def test_deleta_usuario_usuario_nao_encontrado(client, get_token):
    response = client.delete(
        url=f'/usuario/{2}',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()['detail'] == 'Not enought permission'
