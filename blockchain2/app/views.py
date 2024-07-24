

# views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from .models import Candidate, Vote, VotingSession, Block
from .blockchain import Blockchain
from django.http import JsonResponse
blockchain = Blockchain()

from django.core.exceptions import ObjectDoesNotExist

@login_required
def vote(request):
    session = VotingSession.objects.filter(active=True).first()
    if session and session.end_time > timezone.now():
        candidates = Candidate.objects.all()
        if request.method == 'POST':
            candidate_id = request.POST.get('candidate')
            try:
                if Vote.objects.filter(user=request.user, block__index=session.id).exists():
                    return render(request, 'vote.html', {'message': 'You have already voted in this session.'})
                candidate = Candidate.objects.get(id=candidate_id)
                latest_block = blockchain.get_previous_block()
                if not latest_block:
                    proof = blockchain.proof_of_work(100)
                    latest_block = blockchain.create_block(proof, '1')

                # Ensure the block exists
                if not latest_block:
                    return render(request, 'vote.html', {'message': 'No blocks available'})

                # Create the vote in the Django model
                Vote.objects.create(user=request.user, candidate=candidate, block=latest_block)
                candidate.votes += 1
                candidate.save()
                # Add the vote to the blockchain
                blockchain.add_vote(user=request.user, vote=candidate, node_identifier="some_node_identifier")

                return redirect('results')
            except ObjectDoesNotExist:
                return render(request, 'vote.html', {'message': 'Invalid candidate'})
        return render(request, 'vote.html', {'candidates': candidates, 'end_time': session.end_time})
    else:
        return render(request, 'vote.html', {'message': 'Voting is not active'})

@login_required
def start_voting(request):
    if request.user.is_superuser:
        session = VotingSession.objects.first()
        if not session:
            session = VotingSession.objects.create()
        session.start_voting()
        return redirect('vote')
    return JsonResponse({'error': 'You are not authorized to start the voting session'}, status=403)

@login_required
def results(request):
    candidates = Candidate.objects.all().order_by('-votes')
    return render(request, 'results.html', {'candidates': candidates})


# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('vote')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('login')
@login_required
def end_voting(request):
    if request.user.is_superuser:
        session = VotingSession.objects.filter(active=True).first()
        if session:
            session.stop_voting()
            
            # Create a new block with the pending votes
            previous_block = blockchain.get_previous_block()
            previous_proof = previous_block.proof
            proof = blockchain.proof_of_work(previous_proof)
            previous_hash = blockchain.hash(previous_block)
            block = blockchain.create_block(proof, previous_hash)
            
            # Reset the votes
            for candidate in Candidate.objects.all():
                candidate.votes = Vote.objects.filter(candidate=candidate).count()
                candidate.save()
            
        return redirect('results')
    return JsonResponse({'error': 'You are not authorized to end the voting session'}, status=403)

# views.py
from rest_framework import viewsets
from .models import Candidate, Block, Vote
from .serializers import CandidateSerializer, BlockSerializer, VoteSerializer

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

class BlockViewSet(viewsets.ModelViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer

class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
