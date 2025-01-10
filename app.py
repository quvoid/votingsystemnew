from flask import Flask, request, render_template, redirect, url_for, flash

class Node:
    def __init__(self, candidate_id, candidate_name):
        self.candidate_id = candidate_id
        self.candidate_name = candidate_name
        self.votes = 0
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        
    def add_candidate(self, candidate_id, candidate_name):
        new_node = Node(candidate_id, candidate_name)
        if not self.head:
            self.head = new_node
            return
        
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
        
    def find_candidate(self, candidate_id):
        current = self.head
        while current:
            if current.candidate_id == candidate_id:
                return current
            current = current.next
        return None

class VoterHashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [[] for _ in range(size)]
        
    def _hash(self, voter_id):
        return hash(voter_id) % self.size
    
    def add_voter(self, voter_id):
        hash_key = self._hash(voter_id)
        if not self.has_voted(voter_id):
            self.table[hash_key].append(voter_id)
            return True
        return False
        
    def has_voted(self, voter_id):
        hash_key = self._hash(voter_id)
        return voter_id in self.table[hash_key]

class VotingSystem:
    def __init__(self):
        self.candidates = LinkedList()
        self.voters = VoterHashTable()
        self.total_votes = 0
        
    def add_candidate(self, candidate_id, candidate_name):
        self.candidates.add_candidate(candidate_id, candidate_name)
        
    def cast_vote(self, voter_id, candidate_id):
        if self.voters.has_voted(voter_id):
            return False, "You have already voted!"
            
        candidate = self.candidates.find_candidate(candidate_id)
        if not candidate:
            return False, "Invalid candidate ID!"
            
        if self.voters.add_voter(voter_id):
            candidate.votes += 1
            self.total_votes += 1
            return True, "Vote cast successfully!"
        return False, "Error casting vote!"
        
    def get_results(self):
        results = []
        current = self.candidates.head
        while current:
            vote_percentage = (current.votes / self.total_votes * 100) if self.total_votes > 0 else 0
            results.append({
                'candidate_id': current.candidate_id,
                'name': current.candidate_name,
                'votes': current.votes,
                'percentage': round(vote_percentage, 2)
            })
            current = current.next
        return sorted(results, key=lambda x: x['votes'], reverse=True)

    def find_candidate_by_name(self, name):
        current = self.candidates.head
        while current:
            if current.candidate_name.lower() == name.lower():
                return current
            current = current.next
        return None

    def get_total_votes(self):
        return self.total_votes

    def reset_voting(self):
        self.candidates = LinkedList()
        self.voters = VoterHashTable()
        self.total_votes = 0

    def get_candidates_list(self):
        candidates = []
        current = self.candidates.head
        while current:
            candidates.append({
                'candidate_id': current.candidate_id,
                'name': current.candidate_name
            })
            current = current.next
        return candidates

    def get_candidate_votes(self, candidate_id):
        candidate = self.candidates.find_candidate(candidate_id)
        return candidate.votes if candidate else 0

    def get_voting_statistics(self):
        return {
            'total_candidates': len(self.get_candidates_list()),
            'total_votes': self.total_votes
        }

app = Flask(__name__)
app.secret_key = 'your_secret_key'

voting_system = VotingSystem()

@app.route('/')
def index():
    results = voting_system.get_results()
    total_votes = voting_system.get_total_votes()
    return render_template('index.html', results=results, total_votes=total_votes)

@app.route('/vote', methods=['POST'])
def vote():
    voter_id = request.form.get('voter_id')
    candidate_id = request.form.get('candidate_id')
    
    success, message = voting_system.cast_vote(voter_id, candidate_id)
    flash(message)
    return redirect(url_for('index'))

@app.route('/add_candidate', methods=['POST'])
def add_candidate():
    candidate_id = request.form.get('candidate_id')
    candidate_name = request.form.get('candidate_name')
    
    voting_system.add_candidate(candidate_id, candidate_name)
    flash('Candidate added successfully!')
    return redirect(url_for('index'))

@app.route('/find_candidate', methods=['POST'])
def find_candidate():
    candidate_name = request.form.get('candidate_name')
    candidate = voting_system.find_candidate_by_name(candidate_name)
    
    if candidate:
        flash(f"Candidate found: {candidate.candidate_name} (ID: {candidate.candidate_id})")
    else:
        flash("Candidate not found.")
    
    return redirect(url_for('index'))

@app.route('/reset_voting', methods=['POST'])
def reset_voting():
    voting_system.reset_voting()
    flash("Voting has been reset.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Add some initial candidates
    voting_system.add_candidate("1", "Bhartiya Janta Party")
    voting_system.add_candidate("2", "India National Congress")
    voting_system.add_candidate("3", "RSS")
    voting_system.add_candidate("4", "Aam Aadmi Party")
    app.run(debug=True)
