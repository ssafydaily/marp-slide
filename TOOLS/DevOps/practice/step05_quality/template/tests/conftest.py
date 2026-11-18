import pytest
from rest_framework.test import APIClient

from todos.models import Todo


@pytest.fixture
def api_client():
    """DRF API 요청용 클라이언트."""
    return APIClient()


@pytest.fixture
def todo(db):
    """테스트용 할 일 1개."""
    return Todo.objects.create(title="기존 할 일", description="설명")
