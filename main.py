"""
Q-RACING PRO BACKEND v3.0
EDUCATIONAL QUANTUM RACING ENGINE
DR. XU GROUP | TEXAS A&M PHYSICS

This version teaches REAL quantum mechanics:
- Superposition = being in MULTIPLE states (uncertainty)
- Measurement = collapsing to a definite state
- Entanglement = correlated states across universes
- Strategic collapse = learning when to measure
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
    description="Educational Quantum Racing Simulation",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)


# Speed configurations
SPEED_CONFIGS = {
    'slow': {'laser_speed': 0.5, 'spawn_interval': 180},
    'normal': {'laser_speed': 0.7, 'spawn_interval': 120},
    'fast': {'laser_speed': 1.0, 'spawn_interval': 80},
}


class QuantumGame:
    """
    Educational Quantum Racing Engine
    
    QUANTUM MECHANICS CONCEPTS:
    1. SUPERPOSITION: Car exists in both lanes simultaneously (50/50 probability)
    2. MEASUREMENT: Player must choose a lane (collapse) before laser arrives
    3. ENTANGLEMENT: Universe β car is always correlated with Universe α
    4. PROBABILITY: If you don't collapse, random chance determines outcome
    """
    
    GAME_DURATION_SECONDS = 60
    GAME_FPS = 60
    TOTAL_FRAMES = GAME_DURATION_SECONDS * GAME_FPS
    
    # Car and collision zones
    CAR_Y_POSITION = 75  # Where the car sits (% from top)
    COLLISION_Y_MIN = 73
    COLLISION_Y_MAX = 77
    
    def __init__(self, speed='normal'):
        # Quantum state: |ψ⟩ = α|0⟩ + β|1⟩
        # state[0] = lane 0 probability amplitude
        # state[1] = lane 1 probability amplitude
        self.lane = 0  # Current definite lane (0 or 1)
        self.in_superposition = False
        self.superposition_lane_probs = [0.5, 0.5]  # Probabilities when in superposition
        
        self.lasers = []
        self.score = 0
        self.frame = 0
        self.running = True
        self.paused = False
        self.game_won = False
        
        # Statistics for learning
        self.successful_collapses = 0  # Times player chose correctly
        self.random_collapses = 0  # Times player didn't choose (random)
        self.total_lasers_dodged = 0
        
        # Speed settings
        config = SPEED_CONFIGS.get(speed, SPEED_CONFIGS['normal'])
        self.laser_speed = config['laser_speed']
        self.laser_spawn_interval = config['spawn_interval']
        self.speed_mode = speed

    def set_speed(self, speed):
        config = SPEED_CONFIGS.get(speed, SPEED_CONFIGS['normal'])
        self.laser_speed = config['laser_speed']
        self.laser_spawn_interval = config['spawn_interval']
        self.speed_mode = speed

    def get_progress(self):
        return min(100, (self.frame / self.TOTAL_FRAMES) * 100)

    def enter_superposition(self):
        """
        Press H to enter superposition.
        Car now exists in BOTH lanes with 50% probability each.
        Player must collapse (choose a lane) before laser arrives!
        """
        if self.paused or self.in_superposition:
            return
        
        self.in_superposition = True
        self.superposition_lane_probs = [0.5, 0.5]

    def collapse_to_lane(self, target_lane):
        """
        Press A/D to collapse to a specific lane.
        This is MEASUREMENT - choosing which state becomes real.
        """
        if self.paused:
            return
            
        if target_lane in [0, 1]:
            self.lane = target_lane
            self.in_superposition = False
            self.superposition_lane_probs = [1.0, 0.0] if target_lane == 0 else [0.0, 1.0]

    def switch_lane(self):
        """
        In classical mode, simply switch lanes.
        This is like a NOT gate (Pauli-X).
        """
        if self.paused:
            return
            
        if not self.in_superposition:
            self.lane = 1 - self.lane  # Toggle between 0 and 1

    def toggle_pause(self):
        self.paused = not self.paused
        return self.paused

    def update(self):
        if self.paused or not self.running:
            return
        
        self.frame += 1
        
        # Check win condition
        if self.frame >= self.TOTAL_FRAMES:
            self.game_won = True
            self.running = False
            return
        
        # Spawn lasers
        if self.frame % self.laser_spawn_interval == 0:
            # Laser targets a random lane
            laser_lane = random.choice([0, 1])
            self.lasers.append({
                'lane': laser_lane,
                'y': -5,
                'id': f"laser_{self.frame}"
            })
        
        # Update laser positions and check collisions
        for laser in self.lasers[:]:
            laser['y'] += self.laser_speed
            
            # Collision check when laser reaches car
            if self.COLLISION_Y_MIN <= laser['y'] <= self.COLLISION_Y_MAX:
                hit = self.check_collision(laser)
                if hit:
                    self.running = False
                    return
                else:
                    # Dodged! Remove laser
                    if laser in self.lasers:
                        self.lasers.remove(laser)
                        self.total_lasers_dodged += 1
            
            # Remove off-screen lasers
            elif laser['y'] > 100:
                if laser in self.lasers:
                    self.lasers.remove(laser)
        
        if self.running:
            self.score += 1

    def check_collision(self, laser):
        """
        CORE QUANTUM LOGIC:
        
        If CLASSICAL (not in superposition):
        - Definite position, simple collision check
        
        If in SUPERPOSITION:
        - Player is in BOTH lanes with 50% probability
        - If player hasn't collapsed, RANDOM 50/50 determines outcome
        - This teaches: you MUST measure (collapse) before interaction!
        """
        laser_lane = laser['lane']
        
        if not self.in_superposition:
            # CLASSICAL: Simple deterministic collision
            return self.lane == laser_lane
        else:
            # QUANTUM: Player is in superposition
            # They didn't choose in time! Random collapse happens.
            self.random_collapses += 1
            
            # 50% chance of being in each lane
            collapsed_lane = random.choice([0, 1])
            self.lane = collapsed_lane
            self.in_superposition = False
            
            # Check if random collapse put us in laser's path
            return collapsed_lane == laser_lane

    def get_state(self):
        return {
            "lane": self.lane,
            "in_superposition": self.in_superposition,
            "lane_probabilities": self.superposition_lane_probs,
            "lasers": self.lasers,
            "score": self.score,
            "frame": self.frame,
            "progress": self.get_progress(),
            "running": self.running,
            "paused": self.paused,
            "game_won": self.game_won,
            "total_frames": self.TOTAL_FRAMES,
            "game_time_seconds": self.frame / self.GAME_FPS,
            "speed_mode": self.speed_mode,
            "stats": {
                "successful_collapses": self.successful_collapses,
                "random_collapses": self.random_collapses,
                "total_dodged": self.total_lasers_dodged
            }
        }


@app.get("/")
async def root():
    return {"message": "Q-RACING PRO v3.0 - Educational Quantum Racing", "status": "ONLINE"}


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "3.0.0"}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    print(f"Client {client_id} connected")
    
    game = QuantumGame()
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.016)
                action = data.get("action")
                
                if action == "superposition":
                    # H key - enter superposition
                    game.enter_superposition()
                elif action == "collapse_left":
                    # A key - collapse to lane 0
                    game.collapse_to_lane(0)
                elif action == "collapse_right":
                    # D key - collapse to lane 1
                    game.collapse_to_lane(1)
                elif action == "switch":
                    # Arrow keys - switch lane (classical only)
                    game.switch_lane()
                elif action == "pause":
                    game.toggle_pause()
                elif action == "set_speed":
                    game.set_speed(data.get("speed", "normal"))
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
        print(f"Client {client_id} - Score: {game.score}, Dodged: {game.total_lasers_dodged}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)