from django import forms
from .models import Cell

class MyForm(forms.ModelForm):
    class Meta:
        model = Cell
        fields = ['x', 'y', 'mark']