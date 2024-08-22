from django.db import models
import uuid

class Cell(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    row = models.PositiveIntegerField()
    col = models.PositiveIntegerField()
    value = models.CharField(max_length=1, choices=(('O', 'O'), ('X', 'X')), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
