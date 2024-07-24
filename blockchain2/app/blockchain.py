import hashlib
import json
from time import time
from django.utils import timezone
from .models import Block, Vote

class Blockchain:
    def __init__(self):
        self.chain = self.get_chain_from_db()
        self.pending_votes = []
        if not self.chain:
            self.create_block(previous_hash='1', proof=100)  # Genesis block

    def create_block(self, proof, previous_hash):
        # Create block in the database
        block = Block.objects.create(
            index=len(self.chain) + 1,
            timestamp=timezone.now().timestamp(),
            proof=proof,
            previous_hash=previous_hash
        )
        
        # Add pending votes to the block
        for vote in self.pending_votes:
            user = vote['user']
            candidate = vote['vote']
            Vote.objects.create(
                user=user,
                candidate=candidate,
                block=block
            )
        
        # Clear the pending votes list
        self.pending_votes = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        if not self.chain:
            proof = self.proof_of_work(100)
            self.create_block(proof, '1')
        return self.chain[-1] if self.chain else None

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while not check_proof:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        # Convert block to a dictionary and encode it to ensure JSON serialization
        block_dict = {
            'index': block.index,
            'timestamp': block.timestamp,
            'proof': block.proof,
            'previous_hash': block.previous_hash
        }
        encoded_block = json.dumps(block_dict, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            # Check if the previous hash matches
            if block.previous_hash != self.hash(previous_block):
                return False
            previous_proof = previous_block.proof
            proof = block.proof
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            # Check if the hash meets the difficulty criteria
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_vote(self, user, vote, node_identifier):
        # Append vote to pending votes
        self.pending_votes.append({
            'user': user,
            'vote': vote,
            'timestamp': time(),
            'node_identifier': node_identifier,
        })

        # Create a new block if a certain number of votes have been accumulated
        if len(self.pending_votes) >= 1:  # Example condition: create a block after 5 votes
            previous_block = self.get_previous_block()
            proof = self.proof_of_work(previous_block.proof)
            previous_hash = self.hash(previous_block)
            self.create_block(proof, previous_hash)

        # Return the index of the block that will include this vote
        return self.get_previous_block().index + 1

    def get_chain_from_db(self):
        # Fetch the chain from the database ordered by index
        return list(Block.objects.all().order_by('index'))
