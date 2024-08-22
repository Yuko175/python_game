from django.forms import ModelForm
from .models import MyModel

class MyForm(ModelForm):
    class Meta:
        model = MyModel
        fields = ['name', 'age']
