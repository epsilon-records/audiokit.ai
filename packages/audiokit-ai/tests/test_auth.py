import pytest
from fastapi import HTTPException
from audiokit_ai.auth import verify_token

def test_verify_token_valid():
    token = "valid-token"
    assert verify_token(token) == token

def test_verify_token_invalid():
    token = "invalid-token"
    with pytest.raises(HTTPException) as exc_info:
        verify_token(token)
    assert exc_info.value.status_code == 401 