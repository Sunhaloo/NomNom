from django.db import models
from django.contrib.auth.models import User
from orders.models import Order

class Delivery(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices= [('Pending', 'Pending'), ('Done', 'Done'), ('Failed', 'Failed')], default='Pending')
    date = models.DateField()
    #These are temporary placeholders for the actual fields, I dunno how to access them.

    
    
# Create your models here.
