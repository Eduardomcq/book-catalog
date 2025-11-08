from jwt import decode
import json
from http import HTTPStatus

from book_catalog.utils.security import generate_jwt
from book_catalog.utils.settings import Settings


def test_generate_jwt():
    token = generate_jwt('test')
    decoded_token = decode(token, Settings().SECRET_KEY, Settings().ALGORITH)

    assert decoded_token['sub'] == 'test'
    assert 'exp' in decoded_token