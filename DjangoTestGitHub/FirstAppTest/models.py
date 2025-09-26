from django.db import models


# create the 'Question' database table
class Question(models.Model):
    # class variables that will become our database fields
    question_text = models.CharField(max_length=200)
    # INFO: the actual field name is going to be `pub_date`
    # but the user is going to see 'data published' and NOT `pub_date`
    pub_date = models.DateTimeField("date published")

    # method to allow us to get better return results in 'RPEL'
    def __str__(self):
        # return the 'question_text' field instead of just showing object
        return self.question_text


# create the 'Choice' database table
class Choice(models.Model):
    # class variables that will become our database fields
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    # method to allow us to get better return results in 'RPEL'
    def __str__(self):
        # return the 'question_text' field instead of just showing object
        return self.choice_text
