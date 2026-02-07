import numpy as np
import random
from fastapi import FastAPI, WebSocket

app = FastAPI()

class QuantumEngine:
    def __init__(self):
        # State: [|00>, |01>, |10>, |11>] 
        # (Univ A lane, Univ B lane)
        self.state = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
        self.in_superposition = False
        self.active_lasers = []

    def apply_hadamard(self):
        """Creates superposition and Entanglement via H + CNOT"""
        if self.in_superposition: return
        
        # H gate on Qubit 0 (Universe A)
        h = (1/np.sqrt(2)) * np.array([[1,0,1,0],[0,1,0,1],[1,0,-1,0],[0,1,0,-1]])
        # CNOT (Control: A, Target: B) to create Bell State
        cnot = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
        
        self.state = np.dot(cnot, np.dot(h, self.state))
        self.in_superposition = True

    def apply_pauli_x(self, universe):
        """Standard Bit-Flip (Lane Swap)"""
        if universe == 'A':
            gate = np.array([[0,0,1,0],[0,0,0,1],[1,0,0,0],[0,1,0,0]])
        else:
            gate = np.array([[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]])
        self.state = np.dot(gate, self.state)

    def check_measurement(self, laser):
        """The Born Rule Measurement"""
        probs = np.abs(self.state)**2
        # If laser is in Univ A, Lane 0, it hits states |00> and |01> (indices 0,1)
        if laser['universe'] == 'A':
            hit_idx = [0, 1] if laser['lane'] == 0 else [2, 3]
        else:
            hit_idx = [0, 2] if laser['lane'] == 0 else [1, 3]
            
        prob_collision = sum(probs[i] for i in hit_idx)
        
        if random.random() < prob_collision:
            return "COLLAPSE_DEAD"
        else:
            # COLLAPSE_SUCCESS: Collapse to safe states and return to classical
            safe_idx = [i for i in range(4) if i not in hit_idx]
            # Normalize and snap to the most probable single state
            new_lane = 0 if (probs[0]+probs[1] > probs[2]+probs[3]) else 1
            self.state = np.array([0,0,0,0], dtype=complex)
            self.state[0 if new_lane == 0 else 2] = 1.0 # Return to Univ A only
            self.in_superposition = False
            return "SUCCESS"

# ... (FastAPI WebSocket boilerplate remains similar, calling these methods)



# To run the app, use the command: `uvicorn filename:app --reload`
# Ensure you have the necessary packages installed: fastapi, uvicorn, numpy
# If using a virtual environment, remember to activate it first: .venv\Scripts\activate