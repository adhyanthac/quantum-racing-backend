"""
Q-RACING PRO BACKEND v2.2
Quantum Entanglement Racing Engine
DR. XU GROUP | TEXAS A&M PHYSICS
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import numpy as np
import json
import random
from datetime import datetime

app = FastAPI(
    title="Q-Racing Pro Backend",
    description="Quantum Entanglement Racing Simulation",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)


class QuantumGame:
    """Quantum Racing Vehicle Engine"""
    
    # Game constants
    GAME_DURATION_SECONDS = 60  # 1 minute total game time
    GAME_FPS = 60
    TOTAL_FRAMES = GAME_DURATION_SECONDS * GAME_FPS  # 3600 frames for full game
    
    # Car position (Y percent from top - car is at 70-80% of screen height)
    CAR_TOP_Y = 70  # Top edge of car
    CAR_BOTTOM_Y = 80  # Bottom edge of car
    
    # Collision zone - EXACT touch only (laser must overlap with car body)
    COLLISION_Y_MIN = 72  # Laser must be at least here
    COLLISION_Y_MAX = 78  # Laser must be no more than here
    
    def __init__(self):
        self.state = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
        self.in_superposition = False
        self.lasers = []
        self.score = 0
        self.frame = 0
        self.running = True
        self.paused = False
        self.game_won = False  # Track if player completed the race
        self.start_time = datetime.now()
        self.hadamard_count = 0
        self.pauli_x_count = 0
        
        # Slowed game speed
        self.laser_speed = 0.6
        self.laser_spawn_interval = 200  # Spawn less frequently

    def get_progress(self):
        """Calculate progress as percentage (0-100)"""
        return min(100, (self.frame / self.TOTAL_FRAMES) * 100)

    def apply_hadamard(self):
        if self.in_superposition or self.paused:
            return
        
        h = (1 / np.sqrt(2)) * np.array([
            [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, -1, 0], [0, 1, 0, -1]
        ])
        cnot = np.array([
            [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]
        ])
        
        self.state = np.dot(cnot, np.dot(h, self.state))
        self.in_superposition = True
        self.hadamard_count += 1

    def apply_pauli_x(self, target):
        if self.paused:
            return
        
        if target == 'A':
            gate = np.array([[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]])
        else:
            gate = np.array([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
        
        self.state = np.dot(gate, self.state)
        self.pauli_x_count += 1

    def toggle_pause(self):
        self.paused = not self.paused
        return self.paused

    def update(self):
        if self.paused:
            return
        
        self.frame += 1
        
        # Check if game is complete (1 minute reached)
        if self.frame >= self.TOTAL_FRAMES:
            self.game_won = True
            self.running = False
            return
        
        # Spawn lasers
        if self.frame % self.laser_spawn_interval == 0:
            universe = random.choice(['A', 'B']) if self.in_superposition else 'A'
            self.lasers.append({
                'universe': universe, 
                'lane': random.choice([0, 1]), 
                'y': -5,
                'id': f"laser_{self.frame}"
            })
        
        # Update laser positions
        collision_laser = None
        for laser in self.lasers[:]:
            laser['y'] += self.laser_speed
            
            # EXACT collision detection - only when laser is IN the car zone
            if self.COLLISION_Y_MIN <= laser['y'] <= self.COLLISION_Y_MAX:
                if self.check_collision(laser):
                    collision_laser = laser
                    self.running = False
                    break
            
            # Remove lasers that passed through (survived) or went off screen
            if laser['y'] > self.COLLISION_Y_MAX and laser in self.lasers:
                self.lasers.remove(laser)
            elif laser['y'] > 100:
                if laser in self.lasers:
                    self.lasers.remove(laser)
        
        if self.running:
            self.score += 1

    def check_collision(self, laser):
        """Quantum measurement and precise collision check"""
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
        
        # Survived - collapse state
        safe_lane = 0 if (probs[0] + probs[1] > probs[2] + probs[3]) else 1
        self.state = np.array([0, 0, 0, 0], dtype=complex)
        self.state[0 if safe_lane == 0 else 2] = 1.0
        self.in_superposition = False
        
        return False

    def get_state(self):
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
            "progress": self.get_progress(),
            "running": self.running,
            "paused": self.paused,
            "game_won": self.game_won,
            "total_frames": self.TOTAL_FRAMES,
            "game_time_seconds": self.frame / self.GAME_FPS
        }


@app.get("/")
async def root():
    return {"message": "Q-RACING PRO v2.2", "status": "ONLINE"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    print(f"Client {client_id} connected")
    
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
                    game = QuantumGame()
                    
            except asyncio.TimeoutError:
                pass
            
            game.update()
            
            if game.running:
                await websocket.send_json({
                    "type": "game_state", 
                    "data": game.get_state()
                })
            else:
                # Send final state - don't break, wait for restart
                await websocket.send_json({
                    "type": "game_over" if not game.game_won else "game_won",
                    "data": game.get_state()
                })
            
            await asyncio.sleep(1 / 60)
            
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected - Score: {game.score}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)