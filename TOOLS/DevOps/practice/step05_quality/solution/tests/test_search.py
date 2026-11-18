import pytest

from todos.models import Todo

pytestmark = pytest.mark.django_db

LIST_URL = "/api/todos/"


@pytest.fixture
def sample_todos():
    Todo.objects.create(title="Django 공부")
    Todo.objects.create(title="장보기")
    Todo.objects.create(title="django 테스트 작성")


def test_search_by_title_is_case_insensitive(api_client, sample_todos):
    response = api_client.get(LIST_URL, {"search": "DJANGO"})

    assert response.status_code == 200
    titles = {item["title"] for item in response.json()}
    assert titles == {"Django 공부", "django 테스트 작성"}


def test_search_without_match_returns_empty_list(api_client, sample_todos):
    response = api_client.get(LIST_URL, {"search": "없는 키워드"})

    assert response.status_code == 200
    assert response.json() == []


def test_empty_search_returns_all(api_client, sample_todos):
    response = api_client.get(LIST_URL, {"search": ""})

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_search_and_filter_combined(api_client):
    Todo.objects.create(title="Django 배포", is_done=True)
    Todo.objects.create(title="Django 공부", is_done=False)

    response = api_client.get(LIST_URL, {"search": "django", "is_done": "true"})

    assert [item["title"] for item in response.json()] == ["Django 배포"]
