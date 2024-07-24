from django.contrib import admin
from .models import *
# Register your models hers
admin.site.register(Vote)
from django.contrib import admin
from .models import Candidate, VotingSession, Block, Vote

admin.site.register(Candidate)
admin.site.register(VotingSession)
admin.site.register(Block)
