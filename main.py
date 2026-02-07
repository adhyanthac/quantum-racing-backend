"""
Q-RACING PRO BACKEND v2.4
Quantum Entanglement Racing Engine
DR. XU GROUP | TEXAS A&M PHYSICS

STRATEGIC SUPERPOSITION MODE:
- Entering superposition gives you a "quantum shield" for 1 dodge
- After dodging ONE laser in superposition, state collapses
- Brief invincibility (0.3 sec) when entering superposition
- Lasers spawn slower in superposition mode
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
    version="2.4.0"
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)


# Speed configurations
SPEED_CONFIGS = {
    'slow': {'laser_speed': 0.4, 'spawn_interval': 300, 'superposition_spawn': 400},
    'normal': {'laser_speed': 0.6, 'spawn_interval': 220, 'superposition_spawn': 320},
    'fast': {'laser_speed': 1.0, 'spawn_interval': 160, 'superposition_spawn': 240},
}


class QuantumGame:
    """Quantum Racing Vehicle Engine with Strategic Superposition"""
    
    # Game constants
    GAME_DURATION_SECONDS = 60
    GAME_FPS = 60
    TOTAL_FRAMES = GAME_DURATION_SECONDS * GAME_FPS
    
    # Car position
    CAR_TOP_Y = 70
    CAR_BOTTOM_Y = 80
    COLLISION_Y_MIN = 72
    COLLISION_Y_MAX = 78
    
    # Superposition mechanics
    INVINCIBILITY_FRAMES = 18  # 0.3 seconds of invincibility when entering superposition
    
    def __init__(self, speed='normal'):
        self.state = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
        self.in_superposition = False
        self.lasers = []
        self.score = 0
        self.frame = 0
        self.running = True
        self.paused = False
        self.game_won = False
        self.start_time = datetime.now()
        self.hadamard_count = 0
        self.pauli_x_count = 0
        self.dodges_in_superposition = 0  # Track dodges while in superposition
        self.invincibility_timer = 0  # Frames of invincibility remaining
        self.quantum_dodges = 0  # Total successful quantum dodges
        
        # Speed settings
        config = SPEED_CONFIGS.get(speed, SPEED_CONFIGS['normal'])
        self.laser_speed = config['laser_speed']
        self.base_spawn_interval = config['spawn_interval']
        self.superposition_spawn_interval = config['superposition_spawn']
        self.speed_mode = speed

    @property
    def laser_spawn_interval(self):
        """Slower spawn rate in superposition mode"""
        if self.in_superposition:
            return self.superposition_spawn_interval
        return self.base_spawn_interval

    def set_speed(self, speed):
        """Update game speed"""
        config = SPEED_CONFIGS.get(speed, SPEED_CONFIGS['normal'])
        self.laser_speed = config['laser_speed']
        self.base_spawn_interval = config['spawn_interval']
        self.superposition_spawn_interval = config['superposition_spawn']
        self.speed_mode = speed

    def get_progress(self):
        """Calculate progress as percentage (0-100)"""
        return min(100, (self.frame / self.TOTAL_FRAMES) * 100)

    def apply_hadamard(self):
        """Enter superposition - gives quantum dodge ability"""
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
        self.dodges_in_superposition = 0  # Reset dodge counter
        self.invincibility_timer = self.INVINCIBILITY_FRAMES  # Brief invincibility

    def apply_pauli_x(self, target):
        """Switch lanes in target universe"""
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
        if self.paused or not self.running:
            return
        
        self.frame += 1
        
        # Decrease invincibility timer
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
        
        # Check if game is complete
        if self.frame >= self.TOTAL_FRAMES:
            self.game_won = True
            self.running = False
            return
        
        # Spawn lasers (slower in superposition)
        if self.frame % self.laser_spawn_interval == 0:
            universe = random.choice(['A', 'B']) if self.in_superposition else 'A'
            self.lasers.append({
                'universe': universe, 
                'lane': random.choice([0, 1]), 
                'y': -5,
                'id': f"laser_{self.frame}"
            })
        
        # Update laser positions
        for laser in self.lasers[:]:
            laser['y'] += self.laser_speed
            
            # Collision detection
            if self.COLLISION_Y_MIN <= laser['y'] <= self.COLLISION_Y_MAX:
                # Skip if invincible
                if self.invincibility_timer > 0:
                    continue
                    
                if self.check_collision(laser):
                    self.running = False
                    return
            
            # Remove off-screen lasers
            if laser['y'] > 100:
                if laser in self.lasers:
                    self.lasers.remove(laser)
        
        if self.running:
            self.score += 1

    def check_collision(self, laser):
        """
        Strategic collision check:
        - In superposition: First dodge is FREE (50/50 but collapse if survive)
        - After collapse: Back to classical mode
        """
        probs = np.abs(self.state) ** 2
        
        # Determine which states would be hit by this laser
        if laser['universe'] == 'A' and laser['lane'] == 0:
            hit_idx = [0, 1]  # |00⟩ and |01⟩
        elif laser['universe'] == 'A' and laser['lane'] == 1:
            hit_idx = [2, 3]  # |10⟩ and |11⟩
        elif laser['universe'] == 'B' and laser['lane'] == 0:
            hit_idx = [0, 2]  # |00⟩ and |10⟩
        else:
            hit_idx = [1, 3]  # |01⟩ and |11⟩
        
        prob_hit = sum(probs[i] for i in hit_idx)
        
        # STRATEGIC SUPERPOSITION BENEFIT:
        # If in superposition and this is first dodge attempt,
        # GUARANTEE survival (collapse to safe state)
        if self.in_superposition and self.dodges_in_superposition == 0:
            # First dodge in superposition - GUARANTEED SAFE
            self.dodges_in_superposition += 1
            self.quantum_dodges += 1
            
            # Collapse to the safe lane (opposite of laser lane)
            if laser['universe'] == 'A':
                safe_lane = 1 if laser['lane'] == 0 else 0
            else:
                safe_lane = 1 if laser['lane'] == 0 else 0
            
            # Collapse state to safe position
            self.state = np.array([0, 0, 0, 0], dtype=complex)
            if safe_lane == 0:
                self.state[0] = 1.0  # |00⟩
            else:
                self.state[3] = 1.0  # |11⟩ 
            
            self.in_superposition = False  # Collapse back to classical
            return False  # SURVIVED!
        
        # Normal collision (classical or 2nd+ laser in superposition)
        if random.random() < prob_hit:
            return True  # HIT - GAME OVER
        
        # Survived without quantum benefit - still collapse
        if self.in_superposition:
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
                "pauli_x_count": self.pauli_x_count,
                "quantum_dodges": self.quantum_dodges,
                "invincible": self.invincibility_timer > 0
            },
            "lasers": self.lasers,
            "score": self.score,
            "frame": self.frame,
            "progress": self.get_progress(),
            "running": self.running,
            "paused": self.paused,
            "game_won": self.game_won,
            "total_frames": self.TOTAL_FRAMES,
            "game_time_seconds": self.frame / self.GAME_FPS,
            "speed_mode": self.speed_mode
        }


@app.get("/")
async def root():
    return {"message": "Q-RACING PRO v2.4 - Strategic Superposition", "status": "ONLINE"}


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
                elif action == "set_speed":
                    speed = data.get("speed", "normal")
                    game.set_speed(speed)
                elif action == "restart":
                    old_speed = game.speed_mode
                    game = QuantumGame(speed=old_speed)
                    
            except asyncio.TimeoutError:
                pass
            
            game.update()
            
            if game.running:
                await websocket.send_json({
                    "type": "game_state", 
                    "data": game.get_state()
                })
            else:
                msg_type = "game_won" if game.game_won else "game_over"
                await websocket.send_json({
                    "type": msg_type,
                    "data": game.get_state()
                })
            
            await asyncio.sleep(1 / 60)
            
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected - Score: {game.score}, Quantum Dodges: {game.quantum_dodges}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)