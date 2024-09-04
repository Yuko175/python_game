from django.db import models
import uuid

class Board(models.Model):
    row = models.IntegerField()
    col = models.IntegerField()
    player = models.CharField(max_length=10, blank=True, null=True)
    count = models.IntegerField(default=0) 

class DeckCard(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.CharField(max_length=10, blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    up = models.IntegerField()
    down = models.IntegerField()
    right = models.IntegerField()
    left = models.IntegerField()
    display = models.CharField(max_length=100)

class ActionLog(models.Model):
    count = models.IntegerField() 
    player = models.CharField(max_length=10, blank=True, null=True)  
    action = models.CharField(max_length=20, blank=True, null=True) 
    
class Player(models.Model):
    player = models.CharField(max_length=10, blank=True, null=True)    
    knight_count = models.IntegerField() 
