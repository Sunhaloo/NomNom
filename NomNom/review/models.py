from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}"
    
    #again, everything is a skeleton, need to review later.
# Create your models here.
