import json
from http import HTTPStatus


def test_post_novo_romancista(client, get_token):
    response = client.post(
        url='/romancista/',
        headers={'Authorization': f'Bearer {get_token}'},
        data=json.dumps({
            'nome': 'test'
            }
        )
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'nome': 'test'}


def test_post_romancista_ja_criado(client, get_token, add_romancista_patrick):
    response = client.post(
        url='/romancista/',
        headers={'Authorization': f'Bearer {get_token}'},
        data=json.dumps({
            'nome': add_romancista_patrick.nome
            }
        )
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": f'{add_romancista_patrick.nome} já consta no MADR'}


def test_delete_romancista(client, get_token, add_romancista_patrick):
    response = client.delete(
        url=F'/romancista/{add_romancista_patrick.id}',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': "Romancista deletada no MADR"}


def test_delete_romancista_nao_existente(client, get_token, add_romancista_patrick):
    response = client.delete(
        url=F'/romancista/{add_romancista_patrick.id + 1}',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': "Romancista não consta no MADR"}


def test_atualiza_romancista(client, get_token, add_romancista_patrick):
    response = client.patch(
        url=f'/romancista/{add_romancista_patrick.id}',
        headers={'Authorization': f'Bearer {get_token}'},
        data=json.dumps({
            'nome': 'test'
            }
        )
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'nome': 'test'}


def test_atualiza_romancista_nao_encontrado(client, get_token, add_romancista_patrick):
    response = client.patch(
        url=f'/romancista/{add_romancista_patrick.id + 1}',
        headers={'Authorization': f'Bearer {get_token}'},
        data=json.dumps({
            'nome': 'test'
            }
        )
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': "Romancista não consta no MADR"}


def test_atualiza_romancista_com_conflito(
        client,
        get_token,
        add_romancista_patrick,
        add_romancista_dan
    ):
    response = client.patch(
        url=f'/romancista/{add_romancista_patrick.id}',
        headers={'Authorization': f'Bearer {get_token}'},
        data=json.dumps({
            'nome': 'dan'
            }
        )
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": 'dan já consta no MADR'}


def test_get_romancista_por_id(client, get_token, add_romancista_patrick):
    response = client.get(
        url=f'/romancista/{add_romancista_patrick.id}',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': add_romancista_patrick.id, 'nome': add_romancista_patrick.nome}


def test_get_romancista_nao_encontrado(client, get_token, add_romancista_patrick):
    response = client.get(
        url=f'/romancista/{add_romancista_patrick.id + 1}',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': "Romancista não consta no MADR"}


def test_query_romancista(client, get_token, add_romancista_patrick):
    response = client.get(
        url='/romancista/?nome=p',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'romancistas': [{'id': add_romancista_patrick.id, 'nome': add_romancista_patrick.nome}]}
