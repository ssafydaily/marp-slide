import os
from todos.serializers import TodoSerializer
from rest_framework import viewsets
from todos.models import Todo


class TodoViewSet(viewsets.ModelViewSet):
    """할 일 CRUD API.  (TODO 7: ruff check --fix . / ruff format . 으로 정리해 보세요)"""
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    def get_queryset(self):
        queryset = super().get_queryset()

        is_done = self.request.query_params.get('is_done')
        if is_done != None:
            queryset = queryset.filter(is_done=is_done.lower() == 'true')

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search.strip())

        return queryset
