from rest_framework import viewsets

from todos.models import Todo  # noqa: F401
from todos.serializers import TodoSerializer  # noqa: F401


class TodoViewSet(viewsets.ModelViewSet):
    # TODO 2: queryset 과 serializer_class 를 지정하세요.

    # TODO 3: get_queryset() 을 오버라이드해서
    #   ?is_done=true / ?is_done=false 쿼리 파라미터로 필터링하세요.
    #   힌트: self.request.query_params.get("is_done")
    pass
