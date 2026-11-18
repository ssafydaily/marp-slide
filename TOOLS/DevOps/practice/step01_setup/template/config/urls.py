from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # TODO 3: "health/" 경로에 config.views.health 를 연결하세요.
]
