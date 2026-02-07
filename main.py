"""
╔═══════════════════════════════════════════════════════════════╗
║              Q-RACING PRO BACKEND v2.0                        ║
║             ⚡ QUANTUM ENTANGLEMENT ENGINE ⚡                  ║
║                Y2K EDITION - CIRCA 2000                       ║
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

# ===== Y2K QUANTUM RACING ENGINE =====
app = FastAPI(
    title="Q-Racing Pro Backend",
    description="⚡ Quantum Entanglement Racing Simulation Engine ⚡",
    version="2.0.0-Y2K"
)

# CORS Configuration - Allow all origins for the Y2K web experience
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
    
    Basis States: |00⟩, |01⟩, |10⟩, |11⟩
    - First qubit: Lane position in Universe α
    - Second qubit: Lane position in Universe β
    """
    
    def __init__(self):
        # Quantum state vector in computational basis: [|00⟩, |01⟩, |10⟩, |11⟩]
        self.state = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
        self.in_superposition = False
        self.lasers = []
        self.score = 0
        self.frame = 0
        self.running = True
        self.start_time = datetime.now()
        self.hadamard_count = 0
        self.pauli_x_count = 0

    def apply_hadamard(self):
        """
        Apply Hadamard gate + CNOT to create entangled superposition.
        Places the quantum vehicle in both universes simultaneously.
        
        H ⊗ I followed by CNOT creates Bell state.
        """
        if self.in_superposition:
            return  # Already in superposition
            
        # Hadamard on first qubit: H ⊗ I
        h = (1 / np.sqrt(2)) * np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, -1, 0],
            [0, 1, 0, -1]
        ])
        
        # CNOT gate for entanglement
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
        """
        Apply Pauli-X (NOT) gate to flip lane position.
        
        target 'A': Flip in Universe α (first qubit)
        target 'B': Flip in Universe β (second qubit)
        """
        if target == 'A':
            # X ⊗ I: Flip first qubit
            gate = np.array([
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                [1, 0, 0, 0],
                [0, 1, 0, 0]
            ])
        else:
            # I ⊗ X: Flip second qubit
            gate = np.array([
                [0, 1, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0]
            ])
            
        self.state = np.dot(gate, self.state)
        self.pauli_x_count += 1

    def update(self):
        """
        Game tick update - spawns lasers and handles collisions.
        """
        self.frame += 1
        
        # Spawn lasers periodically (every ~1.67 seconds at 60fps)
        if self.frame % 100 == 0:
            universe = random.choice(['A', 'B']) if self.in_superposition else 'A'
            self.lasers.append({
                'universe': universe, 
                'lane': random.choice([0, 1]), 
                'y': -10,
                'id': f"laser_{self.frame}"
            })
        
        # Update laser positions and check collisions
        for laser in self.lasers[:]:
            laser['y'] += 2  # Laser speed
            
            # Collision detection zone (car position)
            if 60 < laser['y'] < 65:
                if self.check_collision(laser):
                    self.running = False
                else:
                    self.lasers.remove(laser)
            elif laser['y'] > 100:
                self.lasers.remove(laser)
        
        # Increment score while running
        if self.running:
            self.score += 1

    def check_collision(self, laser):
        """
        Quantum measurement - collapse state and check for collision.
        
        The collision is probabilistic based on the quantum state.
        Upon survival, the state collapses to a classical state.
        """
        probs = np.abs(self.state) ** 2
        
        # Determine which basis states would result in a hit
        if laser['universe'] == 'A' and laser['lane'] == 0:
            hit_idx = [0, 1]  # |00⟩, |01⟩
        elif laser['universe'] == 'A' and laser['lane'] == 1:
            hit_idx = [2, 3]  # |10⟩, |11⟩
        elif laser['universe'] == 'B' and laser['lane'] == 0:
            hit_idx = [0, 2]  # |00⟩, |10⟩
        else:  # Universe B, lane 1
            hit_idx = [1, 3]  # |01⟩, |11⟩
        
        # Probability of collision
        prob_hit = sum(probs[i] for i in hit_idx)
        
        # Quantum measurement - probabilistic outcome
        if random.random() < prob_hit:
            return True  # 💥 COLLISION - GAME OVER
        
        # Survived! Collapse to safe classical state in Universe α
        safe_lane = 0 if (probs[0] + probs[1] > probs[2] + probs[3]) else 1
        self.state = np.array([0, 0, 0, 0], dtype=complex)
        self.state[0 if safe_lane == 0 else 2] = 1.0
        self.in_superposition = False
        
        return False

    def get_state(self):
        """
        Return complete game state for frontend rendering.
        """
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
            "game_time_ms": int((datetime.now() - self.start_time).total_seconds() * 1000)
        }


# ===== ROOT ENDPOINT =====
@app.get("/")
async def root():
    """Y2K Welcome Message"""
    return {
        "message": "⚡ Q-RACING PRO v2.0 - Y2K EDITION ⚡",
        "status": "QUANTUM ENGINE ONLINE",
        "endpoints": {
            "websocket": "/ws/{client_id}",
            "health": "/health"
        },
        "credits": "DR. XU GROUP | TEXAS A&M PHYSICS"
    }


# ===== HEALTH CHECK =====
@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "engine": "QUANTUM ENTANGLEMENT ENGINE v2.0",
        "timestamp": datetime.now().isoformat()
    }


# ===== WEBSOCKET GAME ENDPOINT =====
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    Real-time WebSocket connection for quantum racing gameplay.
    
    Handles:
    - 'hadamard' action: Enter superposition
    - 'pauli_x' action: Flip lane position (target: 'A' or 'B')
    """
    await websocket.accept()
    print(f"⚡ Client {client_id} connected to Quantum Racing Engine")
    
    game = QuantumGame()
    
    try:
        while True:
            # Non-blocking receive for player input
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(), 
                    timeout=0.01
                )
                action = data.get("action")
                
                if action == "hadamard":
                    game.apply_hadamard()
                elif action == "pauli_x":
                    game.apply_pauli_x(data.get("target", "A"))
                    
            except asyncio.TimeoutError:
                pass  # No input this frame
            
            # Update game state and send to client
            if game.running:
                game.update()
                await websocket.send_json({
                    "type": "game_state", 
                    "data": game.get_state()
                })
            else:
                # Send final state on game over
                await websocket.send_json({
                    "type": "game_over",
                    "data": game.get_state(),
                    "message": "⚠️ QUANTUM COLLAPSE - GAME OVER ⚠️"
                })
                break
            
            # ~60 FPS game loop
            await asyncio.sleep(1 / 60)
            
    except WebSocketDisconnect:
        print(f"⚡ Client {client_id} disconnected - Final Score: {game.score}")
    except Exception as e:
        print(f"⚠️ Error with client {client_id}: {e}")


# ===== DEV SERVER =====
if __name__ == "__main__":
    import uvicorn
    print("╔════════════════════════════════════════╗")
    print("║   ⚡ Q-RACING PRO SERVER v2.0 ⚡       ║")
    print("║       Y2K EDITION - ACTIVATED          ║")
    print("╚════════════════════════════════════════╝")
    uvicorn.run(app, host="0.0.0.0", port=8000)