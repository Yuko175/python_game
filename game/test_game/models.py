from django.db import models

class MyModel(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='名前')
    age = models.IntegerField(verbose_name='年齢')
