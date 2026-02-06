from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
import json
from typing import Dict, List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuantumEntangledVehicle:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.amplitudes = [0.0, 1.0, 0.0, 0.0]
        self.alive = True
        self.score = 0
        self.frames_alive = 0
        self.hadamard_uses = 0
        self.in_superposition = False

    def apply_hadamard(self):
        if not self.alive: return
        
        if max(self.amplitudes) > 0.9:
            idx = self.amplitudes.index(max(self.amplitudes))
            self.amplitudes[idx] = 0.707
            self.amplitudes[(idx + 1) % 4] = 0.707
            self.hadamard_uses += 1
            self.in_superposition = True
        else:
            # Already in superposition, collapse it
            self.collapse()

    def shift(self, direction):
        if not self.alive: return
        if direction == "right":
            self.amplitudes = [self.amplitudes[-1]] + self.amplitudes[:-1]
        else:
            self.amplitudes = self.amplitudes[1:] + [self.amplitudes[0]]

    def collapse(self):
        """Collapse to definite state"""
        if not self.alive: return
        probs = [a**2 for a in self.amplitudes]
        
        choice = random.choices([0, 1, 2, 3], weights=probs)[0]
        self.amplitudes = [0.0] * 4
        self.amplitudes[choice] = 1.0
        self.in_superposition = False

    def check_collision(self, obstacle_lanes, is_measure_obstacle):
        """
        Check collision with obstacle
        Returns True if vehicle dies
        """
        if not self.alive:
            return False
            
        # Check which lanes the vehicle occupies
        occupied_lanes = []
        for lane, amp in enumerate(self.amplitudes):
            if amp**2 > 0.1:  # Significant probability
                occupied_lanes.append(lane)
        
        # Check if any occupied lane hits an obstacle
        collision = any(lane in obstacle_lanes for lane in occupied_lanes)
        
        if not collision:
            return False
        
        # Collision detected
        if is_measure_obstacle:
            # Hit a measure obstacle
            if self.in_superposition:
                # 50% chance to survive
                if random.random() < 0.5:
                    # Survive - collapse to safe lane
                    safe_lanes = [l for l in range(4) if l not in obstacle_lanes]
                    if safe_lanes:
                        choice = random.choice(safe_lanes)
                        self.amplitudes = [0.0] * 4
                        self.amplitudes[choice] = 1.0
                        self.in_superposition = False
                        return False
                    else:
                        # No safe lane - die
                        return True
                else:
                    # Die
                    return True
            else:
                # Classical state - die
                return True
        else:
            # Regular obstacle - always die
            return True

    def update_score(self):
        if self.alive:
            self.frames_alive += 1
            self.score = (self.frames_alive // 10) + (self.hadamard_uses * 50)

    def to_dict(self):
        return {
            "amplitudes": self.amplitudes,
            "alive": self.alive,
            "score": self.score,
            "frames_alive": self.frames_alive,
            "hadamard_uses": self.hadamard_uses,
            "in_superposition": self.in_superposition
        }

class GameSession:
    def __init__(self):
        self.vehicle = QuantumEntangledVehicle()
        self.obstacles_A: List[Dict] = []
        self.obstacles_B: List[Dict] = []
        self.frame = 0
        self.distance_to_finish = 10000
        self.paused = False
        self.seed_A = random.randint(0, 999999)
        self.seed_B = random.randint(0, 999999)
        self.running = False

    def reset(self):
        self.vehicle = QuantumEntangledVehicle()
        self.obstacles_A = []
        self.obstacles_B = []
        self.frame = 0
        self.distance_to_finish = 10000
        self.paused = False
        self.seed_A = random.randint(0, 999999)
        self.seed_B = random.randint(0, 999999)
        self.running = True

    def generate_fair_obstacles(self):
        """Generate obstacles that don't block all lanes across both universes"""
        max_attempts = 10
        for _ in range(max_attempts):
            random.seed(self.seed_A + self.frame)
            num_blocked_a = random.randint(1, 2)
            blocked_A = random.sample([0, 1, 2, 3], num_blocked_a)
            
            random.seed(self.seed_B + self.frame)
            num_blocked_b = random.randint(1, 2)
            blocked_B = random.sample([0, 1, 2, 3], num_blocked_b)
            
            random.seed()
            
            # Check if there's at least one safe lane across both universes
            all_blocked = set(blocked_A + blocked_B)
            if len(all_blocked) < 4:  # At least one lane is safe
                # Randomly choose which obstacle row gets the measure block
                measure_in_A = random.random() < 0.5
                
                return blocked_A, blocked_B, measure_in_A
        
        # Fallback - ensure fairness
        blocked_A = [0]
        blocked_B = [3]
        measure_in_A = True
        return blocked_A, blocked_B, measure_in_A

    def update(self):
        if self.paused or not self.running:
            return

        self.frame += 1
        self.distance_to_finish -= 4  # Slower speed (was 6, now 4 = ~33% slower)

        # Generate obstacles - slower rate
        if self.frame % 90 == 0:  # Was 70, now 90 (slower spawn)
            blocked_A, blocked_B, measure_in_A = self.generate_fair_obstacles()
            
            self.obstacles_A.append({
                "lanes": blocked_A, 
                "y": -50,
                "is_measure": measure_in_A
            })
            self.obstacles_B.append({
                "lanes": blocked_B, 
                "y": -50,
                "is_measure": not measure_in_A
            })

        # Update obstacles - slower movement
        for obs in self.obstacles_A[:]:
            obs["y"] += 4  # Was 6, now 4 (~33% slower)
            if self.vehicle.alive and 500 < obs["y"] < 560:
                if self.vehicle.check_collision(obs["lanes"], obs["is_measure"]):
                    self.vehicle.alive = False
            if obs["y"] > 800:
                self.obstacles_A.remove(obs)
        
        for obs in self.obstacles_B[:]:
            obs["y"] += 4  # Was 6, now 4 (~33% slower)
            if self.vehicle.alive and 500 < obs["y"] < 560:
                if self.vehicle.check_collision(obs["lanes"], obs["is_measure"]):
                    self.vehicle.alive = False
            if obs["y"] > 800:
                self.obstacles_B.remove(obs)

        self.vehicle.update_score()

        if self.distance_to_finish <= 0 or not self.vehicle.alive:
            self.running = False

    def get_state(self):
        return {
            "vehicle": self.vehicle.to_dict(),
            "obstacles_A": self.obstacles_A,
            "obstacles_B": self.obstacles_B,
            "distance_to_finish": self.distance_to_finish,
            "paused": self.paused,
            "running": self.running,
            "frame": self.frame
        }

sessions: Dict[str, GameSession] = {}

@app.get("/")
async def root():
    return {"message": "Quantum Racing Backend API"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    
    session = GameSession()
    sessions[client_id] = session
    
    try:
        async def game_loop():
            while True:
                if session.running and not session.paused:
                    session.update()
                    await websocket.send_json({
                        "type": "game_state",
                        "data": session.get_state()
                    })
                await asyncio.sleep(1/60)
        
        loop_task = asyncio.create_task(game_loop())
        
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "start":
                session.reset()
            elif action == "pause":
                session.paused = not session.paused
            elif action == "hadamard":
                session.vehicle.apply_hadamard()
            elif action == "shift_left":
                session.vehicle.shift("left")
            elif action == "shift_right":
                session.vehicle.shift("right")
            
    except WebSocketDisconnect:
        loop_task.cancel()
        if client_id in sessions:
            del sessions[client_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)