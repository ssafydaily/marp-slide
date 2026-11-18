from rest_framework import viewsets

from todos.models import Todo
from todos.serializers import TodoSerializer


class TodoViewSet(viewsets.ModelViewSet):
    """할 일 CRUD API.

    - GET    /api/todos/            목록 (?is_done=true|false, ?search=키워드)
    - POST   /api/todos/            생성
    - GET    /api/todos/{id}/       상세
    - PUT    /api/todos/{id}/       전체 수정
    - PATCH  /api/todos/{id}/       부분 수정
    - DELETE /api/todos/{id}/       삭제
    """

    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        is_done = self.request.query_params.get("is_done")
        if is_done is not None:
            queryset = queryset.filter(is_done=is_done.lower() == "true")

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search.strip())

        return queryset
