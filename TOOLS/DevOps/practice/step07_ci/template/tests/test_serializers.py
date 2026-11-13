from todos.serializers import TodoSerializer


def test_serializer_valid_data():
    serializer = TodoSerializer(data={"title": "새 할 일"})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["title"] == "새 할 일"


def test_serializer_requires_title():
    serializer = TodoSerializer(data={"description": "제목 없음"})

    assert not serializer.is_valid()
    assert "title" in serializer.errors


def test_serializer_rejects_blank_title():
    serializer = TodoSerializer(data={"title": "   "})

    assert not serializer.is_valid()
    assert "title" in serializer.errors


def test_serializer_ignores_read_only_fields():
    serializer = TodoSerializer(data={"title": "할 일", "id": 999})

    assert serializer.is_valid()
    assert "id" not in serializer.validated_data
