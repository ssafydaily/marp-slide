import pytest
from django.core.exceptions import ValidationError

from todos.models import Todo

pytestmark = pytest.mark.django_db


def test_create_todo_with_defaults():
    todo = Todo.objects.create(title="장보기")

    assert todo.title == "장보기"
    assert todo.description == ""
    assert todo.is_done is False
    assert todo.created_at is not None
    assert todo.updated_at is not None


def test_str_returns_title():
    todo = Todo(title="운동하기")

    assert str(todo) == "운동하기"


def test_mark_done_changes_is_done():
    todo = Todo.objects.create(title="공부하기")

    todo.mark_done()
    todo.refresh_from_db()

    assert todo.is_done is True


def test_latest_todo_comes_first():
    first = Todo.objects.create(title="첫 번째")
    second = Todo.objects.create(title="두 번째")

    assert list(Todo.objects.all()) == [second, first]


@pytest.mark.parametrize("title", ["a", "가" * 200])
def test_title_within_max_length_is_valid(title):
    todo = Todo(title=title)

    todo.full_clean()  # 예외가 발생하지 않으면 통과


def test_title_over_max_length_is_invalid():
    todo = Todo(title="가" * 201)

    with pytest.raises(ValidationError):
        todo.full_clean()
