from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_dice
from app.main import create_app
from tests.api.helpers import FIXED_ROLL


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_dice] = lambda: lambda: FIXED_ROLL
    with TestClient(app) as test_client:
        yield test_client
