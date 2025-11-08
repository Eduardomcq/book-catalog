import json
from http import HTTPStatus
import pytest

from book_catalog.models.livro import Livro

def test_post_novo_livro(client, get_token, add_romancista_patrick):
    response = client.post(
        url='/livro/',
        headers={'Authorization': f'Bearer {get_token}'},
        data = json.dumps(
            {'ano': 2007,
            'titulo': 'nome do vento',
            'romancista_id': add_romancista_patrick.id}
        )
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 
                               'titulo': 'nome do vento', 
                               'ano':2007, 
                               'romancista_id':add_romancista_patrick.id}
    
@pytest.mark.asyncio    
async def test_post_liro_ja_existente(client, get_token, add_romancista_patrick, session):

    livro = Livro(
        ano= 2007,
        titulo= 'nome do vento',
        romancista_id= add_romancista_patrick.id
    )

    session.add(livro)
    await session.commit()
    await session.refresh(livro)

    response = client.post(
        url='/livro/',
        headers={'Authorization': f'Bearer {get_token}'},
        data = json.dumps(
            {'ano': 2007,
            'titulo': 'nome do vento',
            'romancista_id': add_romancista_patrick.id}
        )
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': f"nome do vento já consta no MADR"}

def test_post_liro_romancista_nao_existente(client, get_token):

    response = client.post(
        url='/livro/',
        headers={'Authorization': f'Bearer {get_token}'},
        data = json.dumps(
            {'ano': 2007,
            'titulo': 'nome do vento',
            'romancista_id': 1}
        )
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': "Romancista não cadastrado"}


@pytest.mark.asyncio    
async def test_delete_liro(client, get_token, add_romancista_patrick, session):

    livro = Livro(
        ano= 2007,
        titulo= 'nome do vento',
        romancista_id= add_romancista_patrick.id
    )

    session.add(livro)
    await session.commit()
    await session.refresh(livro)

    response = client.delete(
        url=f'/livro/{livro.id}',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Livro deletado no MADR"}


def test_delete_liro_nao_existente(client, get_token):

    response = client.delete(
        url=f'/livro/1',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': "Livro não consta no MADR"}


@pytest.mark.asyncio    
async def test_patch_liro_ja_existente(client, get_token, add_romancista_patrick, session):

    livro = Livro(
        ano= 2011,
        titulo= 'nome do vento',
        romancista_id= add_romancista_patrick.id
    )

    session.add(livro)
    await session.commit()
    await session.refresh(livro)

    response = client.patch(
        url=f'/livro/{livro.id}',
        headers={'Authorization': f'Bearer {get_token}'},
        data = json.dumps(
            {'ano': 2007}
        )
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 
                               'titulo': 'nome do vento', 
                               'ano':2007, 
                               'romancista_id':add_romancista_patrick.id}
    

def test_patch_liro_nao_existente(client, get_token):

    response = client.patch(
        url=f'/livro/1',
        headers={'Authorization': f'Bearer {get_token}'},
        data = json.dumps(
            {'ano': 2007}
        )
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': "Livro não consta no MADR"}


@pytest.mark.asyncio    
async def test_get_liro_ja_existente(client, get_token, add_romancista_patrick, session):

    livro = Livro(
        ano= 2007,
        titulo= 'nome do vento',
        romancista_id= add_romancista_patrick.id
    )

    session.add(livro)
    await session.commit()
    await session.refresh(livro)

    response = client.get(
        url=f'/livro/{livro.id}',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 
                               'titulo': 'nome do vento', 
                               'ano':2007, 
                               'romancista_id':add_romancista_patrick.id}
    
def test_get_liro_nao_existente(client, get_token):

    response = client.get(
        url=f'/livro/1',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': "Livro não consta no MADR"}

@pytest.mark.asyncio    
async def test_query_liro_ja_existente(client, get_token, add_romancista_patrick, session):

    livro = Livro(
        ano= 2007,
        titulo= 'nome do vento',
        romancista_id= add_romancista_patrick.id
    )

    session.add(livro)
    await session.commit()
    await session.refresh(livro)

    response = client.get(
        url=f'/livro/?titulo={livro.titulo}&ano={livro.ano}',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'livros':[{'id': 1, 
                               'titulo': 'nome do vento', 
                               'ano':2007, 
                               'romancista_id':add_romancista_patrick.id}]}

  
def test_query_liro_nao_existente(client, get_token, add_romancista_patrick, session):

    response = client.get(
        url=f'/livro/',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'livros':[]}