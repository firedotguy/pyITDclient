import pytest
from helpers import make_response

from itd.exceptions import DEFAULT_ERRORS, AccountDeletedError, NotFoundError, RateLimitError, ValidationError
from itd.core.request import _find_error


def find(status: int, json: dict, *declarations):
    return _find_error(make_response(status, json), json, declarations)


def test_no_error_for_successful_response():
    assert find(200, {'data': {'id': 1}}, ValidationError()) is None


def test_error_is_matched_by_code():
    exception = find(404, {'error': {'code': 'NOT_FOUND'}}, NotFoundError('Post'))

    assert isinstance(exception, NotFoundError)
    assert str(exception) == 'Post not found'  # аргументы декларации не теряются при копировании


def test_declaration_is_not_mutated():
    declaration = ValidationError()

    exception = find(422, {'error': {'code': 'VALIDATION_ERROR', 'message': 'Слишком длинный пост'}}, declaration)

    assert str(exception) == 'Слишком длинный пост'
    assert exception is not declaration
    assert declaration.text == 'Failed validation'  # декларация переиспользуется между запросами, ее нельзя менять


def test_rate_limit_retry_after_is_filled():
    exception = find(429, {'error': {'code': 'RATE_LIMIT_EXCEEDED', 'retryAfter': 5}})

    assert isinstance(exception, RateLimitError)
    assert exception.retry_after == 5
    assert next(declaration for declaration in DEFAULT_ERRORS if isinstance(declaration, RateLimitError)).retry_after == 0


def test_account_deleted_can_restore_is_filled():
    exception = find(403, {'error': {'code': 'ACCOUNT_DELETED', 'canRestore': False}})

    assert isinstance(exception, AccountDeletedError)
    assert exception.can_restore is False


def test_string_error_does_not_break_matching():
    """['error'] не всегда объект - иногда просто строка"""
    exception = find(429, {'error': 'Too Many Requests'})

    assert isinstance(exception, RateLimitError)
    assert exception.retry_after == 0


@pytest.mark.parametrize(
    ('declaration', 'status', 'json'),
    [
        (NotFoundError('User', res_check=lambda res: res.status_code == 500), 500, {}),
        (NotFoundError('Hashtag', json_check=lambda json: json.get('data', {}).get('hashtag') is None), 200, {'data': {'hashtag': None}}),
        (NotFoundError('Poll', 'Опрос не найден'), 400, {'error': {'message': 'Опрос не найден'}})
    ]
)
def test_all_check_kinds_are_supported(declaration, status, json):
    assert isinstance(find(status, json, declaration), NotFoundError)
