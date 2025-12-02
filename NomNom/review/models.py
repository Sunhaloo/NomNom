from django.db import models
from pastry.models import Pastry
from django.contrib.auth import get_user_model
User = get_user_model()

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pastry = models.ForeignKey(Pastry, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add= True)

class Meta:
    unique_together = ('user', 'pastry') 
    
def __str__(self):
    return f"{self.user.username} - {self.rating}"
