from django.contrib import admin
from .models import Cell


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
  list_display = ['id','row','col','value']
  list_editable = ['row','col','value']
  