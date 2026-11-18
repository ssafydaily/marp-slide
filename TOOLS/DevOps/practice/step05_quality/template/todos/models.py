from django.db import models


class Todo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # 같은 시각에 생성된 경우에도 순서가 보장되도록 id 를 보조 정렬 기준으로 사용
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title

    def mark_done(self):
        """할 일을 완료 상태로 변경한다."""
        self.is_done = True
        self.save(update_fields=["is_done", "updated_at"])
