from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import numpy as np
import json
import random

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class QuantumGame:
    def __init__(self):
        # Basis: [|00>, |01>, |10>, |11>]
        self.state = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
        self.in_superposition = False
        self.lasers = []
        self.score = 0
        self.frame = 0
        self.running = True

    def apply_hadamard(self):
        if self.in_superposition: return
        h = (1/np.sqrt(2)) * np.array([[1,0,1,0],[0,1,0,1],[1,0,-1,0],[0,1,0,-1]])
        cnot = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
        self.state = np.dot(cnot, np.dot(h, self.state))
        self.in_superposition = True

    def apply_pauli_x(self, target):
        if target == 'A':
            gate = np.array([[0,0,1,0],[0,0,0,1],[1,0,0,0],[0,1,0,0]])
        else:
            gate = np.array([[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]])
        self.state = np.dot(gate, self.state)

    def update(self):
        self.frame += 1
        if self.frame % 100 == 0:
            univ = random.choice(['A', 'B']) if self.in_superposition else 'A'
            self.lasers.append({'universe': univ, 'lane': random.choice([0, 1]), 'y': -10})
        
        for l in self.lasers[:]:
            l['y'] += 2
            if 60 < l['y'] < 65:
                if self.check_collision(l):
                    self.running = False
                else:
                    self.lasers.remove(l)
            elif l['y'] > 100:
                self.lasers.remove(l)
        if self.running: self.score += 1

    def check_collision(self, laser):
        probs = np.abs(self.state)**2
        hit_idx = [0, 1] if (laser['universe'] == 'A' and laser['lane'] == 0) else \
                  [2, 3] if (laser['universe'] == 'A' and laser['lane'] == 1) else \
                  [0, 2] if (laser['universe'] == 'B' and laser['lane'] == 0) else [1, 3]
        
        prob_hit = sum(probs[i] for i in hit_idx)
        if random.random() < prob_hit: return True
        
        # Success: Collapse to safe classical state in Universe A
        new_lane = 0 if (probs[0]+probs[1] > probs[2]+probs[3]) else 1
        self.state = np.array([0,0,0,0], dtype=complex)
        self.state[0 if new_lane == 0 else 2] = 1.0
        self.in_superposition = False
        return False

    def get_state(self):
        return {
            "quantum_vehicle": {
                "state_vector": [{"real": float(c.real), "imag": float(c.imag)} for c in self.state],
                "in_superposition": self.in_superposition
            },
            "lasers": self.lasers,
            "score": self.score,
            "running": self.running
        }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    game = QuantumGame()
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.01)
                action = data.get("action")
                if action == "hadamard": game.apply_hadamard()
                elif action == "pauli_x": game.apply_pauli_x(data.get("target"))
            except asyncio.TimeoutError: pass
            
            if game.running:
                game.update()
                await websocket.send_json({"type": "game_state", "data": game.get_state()})
            await asyncio.sleep(1/60)
    except WebSocketDisconnect: pass