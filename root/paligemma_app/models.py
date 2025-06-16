from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils.html import mark_safe
from django.conf import settings


# class Form(models.Model):
#     form_title = models.CharField(max_length=200)
#     form_content = models.TextField()
#     form_published= models.DateTimeField("date published")

#     def _str_(self):
#         return self.form_title

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"
    
class Prompt(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    promptID = models.AutoField(primary_key=True)
    imagePrompt = models.ImageField(upload_to = 'uploads/')               
    textPrompt = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Prompt {self.promptID}'
    
class Response(models.Model):
    responseID = models.AutoField(primary_key=True)
    response = models.CharField(max_length=50)
    feedback = models.IntegerField()
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)

    def __str__(self):
        return f'Response {self.responseID}'

class Profile(models.Model):
    userID = models.OneToOneField(User, on_delete=models.CASCADE)
    prompt = models.ManyToManyField(Prompt, blank=True)
    response = models.ManyToManyField(Response, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class History(models.Model):
    historyID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)

    def __str__(self):
        return f'History {self.historyID}'

    ""
