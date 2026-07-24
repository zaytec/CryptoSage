import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_requires_non_sample_secret():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(
            environment="production",
            secret_key="replace-with-a-long-random-secret-of-at-least-32-characters",
        )


def test_production_rejects_wildcard_cors():
    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        Settings(
            environment="production",
            secret_key="a-unique-production-secret-that-is-longer-than-thirty-two-characters",
            cors_origins="https://example.com,*",
        )
