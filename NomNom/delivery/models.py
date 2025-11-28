from django.db import models

class Delivery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default= 'Pending')
    eta = models.DateTimeField()
    #These are temporary placeholders for the actual fields, I dunno how to access them.

    def __str__(self):
        return f"{self.user.username} - {self.status}"
    
# Create your models here.
