from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
import json
from typing import Dict, List

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
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
        self.successful_measures = 0
        self.hadamard_uses = 0

    def apply_hadamard(self):
        if not self.alive: return
        if max(self.amplitudes) > 0.9:
            idx = self.amplitudes.index(max(self.amplitudes))
            self.amplitudes[idx] = 0.707
            self.amplitudes[(idx + 1) % 4] = 0.707
            self.hadamard_uses += 1
        else:
            self.measure()

    def shift(self, direction):
        if not self.alive: return
        if direction == "right":
            self.amplitudes = [self.amplitudes[-1]] + self.amplitudes[:-1]
        else:
            self.amplitudes = self.amplitudes[1:] + [self.amplitudes[0]]

    def measure(self):
        if not self.alive: return
        probs = [a**2 for a in self.amplitudes]
        if max(self.amplitudes) < 0.9: 
            self.successful_measures += 1
        
        choice = random.choices([0, 1, 2, 3], weights=probs)[0]
        self.amplitudes = [0.0] * 4
        self.amplitudes[choice] = 1.0

    def update_score(self):
        if self.alive:
            self.frames_alive += 1
            self.score = (self.frames_alive // 10) + (self.successful_measures * 150) + (self.hadamard_uses * 50)

    def to_dict(self):
        return {
            "amplitudes": self.amplitudes,
            "alive": self.alive,
            "score": self.score,
            "frames_alive": self.frames_alive,
            "successful_measures": self.successful_measures,
            "hadamard_uses": self.hadamard_uses
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

    def update(self):
        if self.paused or not self.running:
            return

        self.frame += 1
        self.distance_to_finish -= 4

        # Generate obstacles
        if self.frame % 70 == 0:
            random.seed(self.seed_A + self.frame)
            blocked_A = random.sample([0, 1, 2, 3], random.randint(1, 2))
            self.obstacles_A.append({"lanes": blocked_A, "y": -50})
            
            random.seed(self.seed_B + self.frame)
            blocked_B = random.sample([0, 1, 2, 3], random.randint(1, 2))
            self.obstacles_B.append({"lanes": blocked_B, "y": -50})
            
            random.seed()

        # Update obstacles
        for obs in self.obstacles_A[:]:
            obs["y"] += 6
            if self.vehicle.alive and 500 < obs["y"] < 560:
                for lane in obs["lanes"]:
                    if self.vehicle.amplitudes[lane]**2 > 0.1:
                        self.vehicle.alive = False
            if obs["y"] > 800:
                self.obstacles_A.remove(obs)
        
        for obs in self.obstacles_B[:]:
            obs["y"] += 6
            if self.vehicle.alive and 500 < obs["y"] < 560:
                for lane in obs["lanes"]:
                    if self.vehicle.amplitudes[lane]**2 > 0.1:
                        self.vehicle.alive = False
            if obs["y"] > 800:
                self.obstacles_B.remove(obs)

        self.vehicle.update_score()

        # Check win/lose conditions
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

# Store active game sessions
sessions: Dict[str, GameSession] = {}

@app.get("/")
async def root():
    return {"message": "Quantum Racing Backend API"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    
    # Create new game session
    session = GameSession()
    sessions[client_id] = session
    
    try:
        # Game loop task
        async def game_loop():
            while True:
                if session.running and not session.paused:
                    session.update()
                    # Send game state to frontend
                    await websocket.send_json({
                        "type": "game_state",
                        "data": session.get_state()
                    })
                await asyncio.sleep(1/60)  # 60 FPS
        
        # Start game loop
        loop_task = asyncio.create_task(game_loop())
        
        # Handle incoming messages
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
            elif action == "measure":
                session.vehicle.measure()
            
    except WebSocketDisconnect:
        loop_task.cancel()
        if client_id in sessions:
            del sessions[client_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)