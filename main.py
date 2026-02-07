"""
╔═══════════════════════════════════════════════════════════════╗
║              Q-RACING PRO BACKEND v2.1                        ║
║             ⚡ QUANTUM ENTANGLEMENT ENGINE ⚡                  ║
║         DR. XU GROUP | TEXAS A&M PHYSICS                      ║
╚═══════════════════════════════════════════════════════════════╝
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import numpy as np
import json
import random
from datetime import datetime

# ===== QUANTUM RACING ENGINE =====
app = FastAPI(
    title="Q-Racing Pro Backend",
    description="⚡ Quantum Entanglement Racing Simulation Engine ⚡",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)


class QuantumGame:
    """
    ⚛️ QUANTUM VEHICLE STATE ENGINE ⚛️
    
    Simulates a quantum racing vehicle existing in superposition
    across multiple parallel universes (α and β).
    """
    
    def __init__(self):
        # Quantum state vector: [|00⟩, |01⟩, |10⟩, |11⟩]
        self.state = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
        self.in_superposition = False
        self.lasers = []
        self.score = 0
        self.frame = 0
        self.running = True
        self.paused = False  # New: pause state
        self.start_time = datetime.now()
        self.hadamard_count = 0
        self.pauli_x_count = 0
        
        # SLOWED DOWN: Game speed settings
        self.laser_speed = 0.8  # Was 2, now much slower
        self.laser_spawn_interval = 180  # Was 100, now spawns less frequently

    def apply_hadamard(self):
        """Apply Hadamard + CNOT for superposition."""
        if self.in_superposition or self.paused:
            return
            
        h = (1 / np.sqrt(2)) * np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, -1, 0],
            [0, 1, 0, -1]
        ])
        
        cnot = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ])
        
        self.state = np.dot(cnot, np.dot(h, self.state))
        self.in_superposition = True
        self.hadamard_count += 1

    def apply_pauli_x(self, target):
        """Apply Pauli-X gate to flip lane position."""
        if self.paused:
            return
            
        if target == 'A':
            gate = np.array([
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                [1, 0, 0, 0],
                [0, 1, 0, 0]
            ])
        else:
            gate = np.array([
                [0, 1, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0]
            ])
            
        self.state = np.dot(gate, self.state)
        self.pauli_x_count += 1

    def toggle_pause(self):
        """Toggle pause state."""
        self.paused = not self.paused
        return self.paused

    def update(self):
        """Game tick update - SLOWED DOWN."""
        if self.paused:
            return
            
        self.frame += 1
        
        # Spawn lasers less frequently
        if self.frame % self.laser_spawn_interval == 0:
            universe = random.choice(['A', 'B']) if self.in_superposition else 'A'
            self.lasers.append({
                'universe': universe, 
                'lane': random.choice([0, 1]), 
                'y': -10,
                'id': f"laser_{self.frame}"
            })
        
        # Move lasers slower
        for laser in self.lasers[:]:
            laser['y'] += self.laser_speed
            
            if 60 < laser['y'] < 65:
                if self.check_collision(laser):
                    self.running = False
                else:
                    self.lasers.remove(laser)
            elif laser['y'] > 100:
                self.lasers.remove(laser)
        
        if self.running:
            self.score += 1

    def check_collision(self, laser):
        """Quantum measurement and collision check."""
        probs = np.abs(self.state) ** 2
        
        if laser['universe'] == 'A' and laser['lane'] == 0:
            hit_idx = [0, 1]
        elif laser['universe'] == 'A' and laser['lane'] == 1:
            hit_idx = [2, 3]
        elif laser['universe'] == 'B' and laser['lane'] == 0:
            hit_idx = [0, 2]
        else:
            hit_idx = [1, 3]
        
        prob_hit = sum(probs[i] for i in hit_idx)
        
        if random.random() < prob_hit:
            return True
        
        safe_lane = 0 if (probs[0] + probs[1] > probs[2] + probs[3]) else 1
        self.state = np.array([0, 0, 0, 0], dtype=complex)
        self.state[0 if safe_lane == 0 else 2] = 1.0
        self.in_superposition = False
        
        return False

    def get_state(self):
        """Return complete game state."""
        return {
            "quantum_vehicle": {
                "state_vector": [
                    {"real": float(c.real), "imag": float(c.imag)} 
                    for c in self.state
                ],
                "in_superposition": self.in_superposition,
                "hadamard_count": self.hadamard_count,
                "pauli_x_count": self.pauli_x_count
            },
            "lasers": self.lasers,
            "score": self.score,
            "frame": self.frame,
            "running": self.running,
            "paused": self.paused,
            "game_time_ms": int((datetime.now() - self.start_time).total_seconds() * 1000)
        }


@app.get("/")
async def root():
    return {
        "message": "⚡ Q-RACING PRO v2.1 ⚡",
        "status": "QUANTUM ENGINE ONLINE",
        "endpoints": {"websocket": "/ws/{client_id}", "health": "/health"}
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Real-time WebSocket for quantum racing gameplay."""
    await websocket.accept()
    print(f"⚡ Client {client_id} connected")
    
    game = QuantumGame()
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.02)
                action = data.get("action")
                
                if action == "hadamard":
                    game.apply_hadamard()
                elif action == "pauli_x":
                    game.apply_pauli_x(data.get("target", "A"))
                elif action == "pause":
                    game.toggle_pause()
                elif action == "restart":
                    # Reset game without disconnecting
                    game = QuantumGame()
                    
            except asyncio.TimeoutError:
                pass
            
            if game.running:
                game.update()
                await websocket.send_json({
                    "type": "game_state", 
                    "data": game.get_state()
                })
            else:
                await websocket.send_json({
                    "type": "game_over",
                    "data": game.get_state(),
                    "message": "GAME OVER"
                })
                # Don't break - wait for restart command
            
            await asyncio.sleep(1 / 60)
            
    except WebSocketDisconnect:
        print(f"⚡ Client {client_id} disconnected - Score: {game.score}")
    except Exception as e:
        print(f"⚠️ Error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)