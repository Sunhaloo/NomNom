from django.db import models


# WARNING: this is merely for show
class Test(models.Model):
    # create a test name field
    name = models.CharField(max_length=20)
