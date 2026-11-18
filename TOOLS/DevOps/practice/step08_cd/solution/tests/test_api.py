import pytest

from todos.models import Todo

pytestmark = pytest.mark.django_db

LIST_URL = "/api/todos/"


def detail_url(pk):
    return f"{LIST_URL}{pk}/"


def test_list_todos(api_client, todo):
    response = api_client.get(LIST_URL)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == todo.title


def test_create_todo(api_client):
    response = api_client.post(LIST_URL, {"title": "새 할 일"}, format="json")

    assert response.status_code == 201
    assert response.json()["is_done"] is False
    assert Todo.objects.count() == 1


def test_create_todo_without_title_returns_400(api_client):
    response = api_client.post(LIST_URL, {}, format="json")

    assert response.status_code == 400
    assert "title" in response.json()


def test_retrieve_todo(api_client, todo):
    response = api_client.get(detail_url(todo.id))

    assert response.status_code == 200
    assert response.json()["id"] == todo.id


def test_retrieve_missing_todo_returns_404(api_client):
    response = api_client.get(detail_url(999999))

    assert response.status_code == 404


def test_update_todo(api_client, todo):
    payload = {"title": "수정된 할 일", "description": "", "is_done": True}

    response = api_client.put(detail_url(todo.id), payload, format="json")

    assert response.status_code == 200
    todo.refresh_from_db()
    assert todo.title == "수정된 할 일"
    assert todo.is_done is True


def test_partial_update_todo(api_client, todo):
    response = api_client.patch(detail_url(todo.id), {"is_done": True}, format="json")

    assert response.status_code == 200
    todo.refresh_from_db()
    assert todo.is_done is True
    assert todo.title == "기존 할 일"


def test_delete_todo(api_client, todo):
    response = api_client.delete(detail_url(todo.id))

    assert response.status_code == 204
    assert not Todo.objects.filter(id=todo.id).exists()


@pytest.mark.parametrize(
    ("query", "expected_titles"),
    [("true", ["완료한 일"]), ("false", ["남은 일"])],
)
def test_filter_by_is_done(api_client, query, expected_titles):
    Todo.objects.create(title="완료한 일", is_done=True)
    Todo.objects.create(title="남은 일", is_done=False)

    response = api_client.get(LIST_URL, {"is_done": query})

    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == expected_titles
