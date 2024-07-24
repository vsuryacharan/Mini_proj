from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Additional fields here

    def __str__(self):
        return self.user.username

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    image = models.ImageField(upload_to='candidate_images/', blank=True, null=True)


    def __str__(self):
        return self.name
class Block(models.Model):
    index = models.IntegerField()
    timestamp = models.FloatField()
    proof = models.IntegerField()
    previous_hash = models.CharField(max_length=64)
    node_identifier = models.CharField(max_length=64, default="")

    class Meta:
        unique_together = (('index', 'timestamp'),)  # Example of a unique constraint

    def __str__(self):
        return f'Block {self.index}'


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='votes')

    def __str__(self):
        return f'Vote by {self.user.username} for {self.candidate.name}'

class VotingSession(models.Model):
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=False)

    def start_voting(self):
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(days=1)
        self.active = True
        self.save()

    def stop_voting(self):
        self.active = False
        self.save()
