from rest_framework import serializers

from todos.models import Todo  # noqa: F401


class TodoSerializer(serializers.ModelSerializer):
    # TODO 1: Meta 클래스를 작성하세요.
    #   - model: Todo
    #   - fields: id, title, description, is_done, created_at, updated_at
    #   - read_only_fields: id, created_at, updated_at
    pass
