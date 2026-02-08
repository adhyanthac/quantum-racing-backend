"""
QUANTUM RACING BACKEND v4.0
Real Quantum Mechanics with Entanglement
DR. XU GROUP | TEXAS A&M PHYSICS

QUANTUM MECHANICS IMPLEMENTATION:
- State vector: |ψ⟩ = α|00⟩ + β|01⟩ + γ|10⟩ + δ|11⟩
- First qubit = Universe A lane, Second qubit = Universe B lane
- |0⟩ = left lane, |1⟩ = right lane

GATES:
- H (Hadamard on qubit A) + CNOT: Creates entangled Bell state
- Pauli-X on qubit A: Switches Universe A car lane (A/D keys)
- Pauli-X on qubit B: Switches Universe B car lane (arrow keys)

MEASUREMENT:
- Laser hitting = measurement event
- Born rule determines probability of each outcome
- Collapse to definite state based on probability
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import numpy as np
import json
import random
from datetime import datetime

app = FastAPI(
    title="Quantum Racing Backend",
    description="Real Quantum Mechanics Racing Simulation",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)


# Speed configurations - INCREASED by 60%
SPEED_CONFIGS = {
    'slow': {'laser_speed': 0.8, 'spawn_interval': 60, 'superposition_spawn': 45},
    'normal': {'laser_speed': 1.1, 'spawn_interval': 45, 'superposition_spawn': 32},
    'fast': {'laser_speed': 1.6, 'spawn_interval': 30, 'superposition_spawn': 22},
}


class QuantumGame:
    """
    Real Quantum Racing Engine with Entanglement
    
    State vector representation:
    |ψ⟩ = state[0]|00⟩ + state[1]|01⟩ + state[2]|10⟩ + state[3]|11⟩
    
    - First qubit: Universe A lane (|0⟩ = left, |1⟩ = right)
    - Second qubit: Universe B lane (|0⟩ = left, |1⟩ = right)
    """
    
    GAME_DURATION_SECONDS = 60
    GAME_FPS = 60
    TOTAL_FRAMES = GAME_DURATION_SECONDS * GAME_FPS
    
    # Collision zone
    CAR_Y = 75
    COLLISION_Y_MIN = 73
    COLLISION_Y_MAX = 77
    
    def __init__(self, speed='normal'):
        # Quantum state vector: [|00⟩, |01⟩, |10⟩, |11⟩]
        # Start in classical state |00⟩ (both in left lane, Universe B inactive)
        self.state = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
        self.in_superposition = False
        
        # Game state
        self.lasers = []
        self.score = 0
        self.frame = 0
        self.running = True
        self.paused = False
        self.game_won = False
        
        # Statistics
        self.hadamard_uses = 0
        self.lasers_passed = 0
        self.crash_frame = None
        
        # Lane offset for visual swapping (toggles 0/1)
        self.lane_offset = 0
        
        # Speed settings
        config = SPEED_CONFIGS.get(speed, SPEED_CONFIGS['normal'])
        self.laser_speed = config['laser_speed']
        self.classical_spawn_interval = config['spawn_interval']
        self.superposition_spawn_interval = config['superposition_spawn']
        self.speed_mode = speed

    @property
    def laser_spawn_interval(self):
        return self.superposition_spawn_interval if self.in_superposition else self.classical_spawn_interval

    def set_speed(self, speed):
        config = SPEED_CONFIGS.get(speed, SPEED_CONFIGS['normal'])
        self.laser_speed = config['laser_speed']
        self.classical_spawn_interval = config['spawn_interval']
        self.superposition_spawn_interval = config['superposition_spawn']
        self.speed_mode = speed

    def get_progress(self):
        return min(100, (self.frame / self.TOTAL_FRAMES) * 100)

    def apply_hadamard_cnot(self):
        """
        Press H: Create TRUE quantum superposition with random probabilities!
        
        State vector: |ψ⟩ = α|00⟩ + β|01⟩ + γ|10⟩ + δ|11⟩
        
        |00⟩ = A:left, B:left
        |01⟩ = A:left, B:right  
        |10⟩ = A:right, B:left
        |11⟩ = A:right, B:right
        
        Probabilities are RANDOM - player must read them to choose wisely!
        """
        if self.paused:
            return
        
        # Generate random amplitudes
        # Create 4 random values and normalize
        raw = np.array([random.random() for _ in range(4)])
        
        # Ensure we have some variety (not all in one state)
        # Add minimum threshold
        raw = raw + 0.1
        
        # Normalize to get valid quantum state (sum of squares = 1)
        amplitudes = np.sqrt(raw / np.sum(raw))
        
        self.state = amplitudes.astype(complex)
        self.in_superposition = True
        self.hadamard_uses += 1
        self.lane_offset = 0  # Reset offset when entering superposition

    def apply_pauli_x_A(self):
        """
        Press A or D: Swap lanes
        Toggles the lane offset, visually swapping both cars.
        The quantum state probability (50/50) stays the same for collisions.
        """
        if self.paused:
            return
        
        # Toggle the lane offset - this swaps the visual positions
        self.lane_offset = 1 - self.lane_offset
        
        # In classical mode, also flip the actual quantum state
        if not self.in_superposition:
            pauli_x_I = np.array([
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                [1, 0, 0, 0],
                [0, 1, 0, 0]
            ], dtype=complex)
            self.state = pauli_x_I @ self.state

    def apply_pauli_x_B(self):
        """
        Press ←/→: Swap lanes (same as A/D since entangled)
        """
        if self.paused:
            return
        
        # Toggle the lane offset - this swaps the visual positions
        self.lane_offset = 1 - self.lane_offset
        
        # In classical mode, also flip the actual quantum state
        if not self.in_superposition:
            I_pauli_x = np.array([
                [0, 1, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0]
            ], dtype=complex)
            self.state = I_pauli_x @ self.state

    def toggle_pause(self):
        self.paused = not self.paused
        return self.paused

    def get_probabilities(self):
        """Get probability of each basis state using Born rule"""
        probs = np.abs(self.state) ** 2
        return {
            '00': float(probs[0]),  # A:left, B:left
            '01': float(probs[1]),  # A:left, B:right
            '10': float(probs[2]),  # A:right, B:left
            '11': float(probs[3])   # A:right, B:right
        }

    def get_lane_probabilities(self):
        """
        Get marginal probabilities for each universe's lane
        P(A=left) = P(|00⟩) + P(|01⟩)
        P(A=right) = P(|10⟩) + P(|11⟩)
        P(B=left) = P(|00⟩) + P(|10⟩)
        P(B=right) = P(|01⟩) + P(|11⟩)
        """
        probs = np.abs(self.state) ** 2
        return {
            'A': {'left': float(probs[0] + probs[1]), 'right': float(probs[2] + probs[3])},
            'B': {'left': float(probs[0] + probs[2]), 'right': float(probs[1] + probs[3])}
        }

    def update(self):
        if self.paused or not self.running:
            return
        
        self.frame += 1
        
        # Win condition
        if self.frame >= self.TOTAL_FRAMES:
            self.game_won = True
            self.running = False
            return
        
        # Spawn lasers
        if self.frame % self.laser_spawn_interval == 0:
            if self.in_superposition:
                # In superposition: lasers can appear in BOTH universes
                universe = random.choice(['A', 'B'])
            else:
                # Classical: only Universe A
                universe = 'A'
            
            # Random speed variation (0.7x to 1.5x base speed)
            speed_multiplier = 0.7 + random.random() * 0.8
            
            self.lasers.append({
                'universe': universe,
                'lane': random.choice([0, 1]),  # 0=left, 1=right
                'y': -5,
                'id': f"laser_{self.frame}",
                'speed': self.laser_speed * speed_multiplier
            })
        
        # Update lasers and check collisions
        for laser in self.lasers[:]:
            # Each laser has its own speed
            laser['y'] += laser.get('speed', self.laser_speed)
            
            # Collision check (measurement!)
            if self.COLLISION_Y_MIN <= laser['y'] <= self.COLLISION_Y_MAX:
                result = self.measure_collision(laser)
                if result == 'crash':
                    self.crash_frame = self.frame
                    self.running = False
                    return
                elif result == 'pass':
                    self.lasers_passed += 1
                    if laser in self.lasers:
                        self.lasers.remove(laser)
                    # COLLAPSE after passing in superposition!
                    if self.in_superposition:
                        self._collapse_after_pass(laser)
            
            # Remove off-screen lasers
            elif laser['y'] > 100:
                if laser in self.lasers:
                    self.lasers.remove(laser)
        
        if self.running:
            self.score += 1

    def measure_collision(self, laser):
        """
        QUANTUM MEASUREMENT using TRUE Born Rule!
        
        Survival probability = probability of being in the SAFE lane
        Based on the actual quantum state probabilities.
        
        Player must read probabilities and choose wisely!
        
        Returns: 'crash' or 'pass'
        """
        probs = np.abs(self.state) ** 2
        universe = laser['universe']
        laser_lane = laser['lane']
        
        # Classical mode: deterministic collision
        if not self.in_superposition:
            if probs[0] > 0.5 or probs[1] > 0.5:
                base_lane = 0
            else:
                base_lane = 1
            car_lane = (base_lane + self.lane_offset) % 2
            return 'crash' if car_lane == laser_lane else 'pass'
        
        # QUANTUM MODE: Use TRUE Born rule with actual probabilities!
        # Calculate probability of survival based on quantum state
        
        # Apply lane_offset to determine effective laser lane in quantum basis
        effective_laser_lane = (laser_lane + self.lane_offset) % 2
        
        if universe == 'A':
            # Probability car A is in SAFE lane (NOT the laser lane)
            if effective_laser_lane == 0:  # Laser in left lane
                # Safe if A is in right lane: |10⟩ or |11⟩
                prob_safe = probs[2] + probs[3]
            else:  # Laser in right lane
                # Safe if A is in left lane: |00⟩ or |01⟩
                prob_safe = probs[0] + probs[1]
        else:  # Universe B
            if effective_laser_lane == 0:  # Laser in left lane
                # Safe if B is in right lane: |01⟩ or |11⟩
                prob_safe = probs[1] + probs[3]
            else:  # Laser in right lane
                # Safe if B is in left lane: |00⟩ or |10⟩
                prob_safe = probs[0] + probs[2]
        
        # Born rule: survive with probability = prob_safe
        if random.random() < prob_safe:
            return 'pass'
        else:
            return 'crash'

    def _collapse_to_safe(self, universe, laser_lane):
        """
        Collapse wavefunction to safe states (renormalize)
        After passing through laser, we're definitely NOT in the hit lane
        """
        probs = np.abs(self.state) ** 2
        
        if universe == 'A':
            if laser_lane == 0:
                # A was measured NOT in left lane → collapse to |10⟩ or |11⟩
                safe_probs = probs[2] + probs[3]
                if safe_probs > 0:
                    self.state = np.array([0, 0, self.state[2], self.state[3]], dtype=complex)
                    self.state = self.state / np.linalg.norm(self.state)
            else:
                # A was measured NOT in right lane → collapse to |00⟩ or |01⟩
                safe_probs = probs[0] + probs[1]
                if safe_probs > 0:
                    self.state = np.array([self.state[0], self.state[1], 0, 0], dtype=complex)
                    self.state = self.state / np.linalg.norm(self.state)
        else:
            if laser_lane == 0:
                # B was measured NOT in left lane → collapse to |01⟩ or |11⟩
                safe_probs = probs[1] + probs[3]
                if safe_probs > 0:
                    self.state = np.array([0, self.state[1], 0, self.state[3]], dtype=complex)
                    self.state = self.state / np.linalg.norm(self.state)
            else:
                # B was measured NOT in right lane → collapse to |00⟩ or |10⟩
                safe_probs = probs[0] + probs[2]
                if safe_probs > 0:
                    self.state = np.array([self.state[0], 0, self.state[2], 0], dtype=complex)
                    self.state = self.state / np.linalg.norm(self.state)
        
        # Check if we're back to classical (only Universe A)
        self._check_superposition()

    def _check_superposition(self):
        """Check if we're still in superposition or collapsed to classical"""
        probs = np.abs(self.state) ** 2
        # If we're in a pure |x0⟩ or |x1⟩ state (B qubit is definite), 
        # we could consider it classical, but let's keep superposition active
        # until explicitly collapsed
        total_prob = sum(probs)
        if total_prob < 0.01:
            # Edge case: reset to classical
            self.state = np.array([1.0, 0, 0, 0], dtype=complex)
            self.in_superposition = False

    def _collapse_after_pass(self, laser):
        """
        Collapse back to classical mode after passing through a laser.
        The wavefunction measurement causes collapse - can use H again!
        """
        universe = laser['universe']
        laser_lane = laser['lane']
        probs = np.abs(self.state) ** 2
        
        # Determine which lane the car ended up in based on survival
        # If laser was in lane X and we passed, we're in the OTHER lane
        safe_lane = 1 - laser_lane
        
        # Collapse to classical state
        if safe_lane == 0:  # Car in left lane
            self.state = np.array([1.0, 0, 0, 0], dtype=complex)  # |00⟩
        else:  # Car in right lane
            self.state = np.array([0, 0, 1.0, 0], dtype=complex)  # |10⟩
        
        self.in_superposition = False
        self.lane_offset = 0  # Reset offset

    def get_state(self):
        lane_probs = self.get_lane_probabilities()
        probs = np.abs(self.state) ** 2
        
        # In classical, car is in definite lane
        # In superposition, show car position based on highest probability
        if not self.in_superposition:
            base_lane_A = 0 if lane_probs['A']['left'] > 0.5 else 1
            base_lane_B = base_lane_A
        else:
            # Show most likely position for each car
            base_lane_A = 0 if lane_probs['A']['left'] > lane_probs['A']['right'] else 1
            base_lane_B = 0 if lane_probs['B']['left'] > lane_probs['B']['right'] else 1
        
        # Apply lane offset (flips lanes when swap is pressed)
        visual_lane_A = (base_lane_A + self.lane_offset) % 2
        visual_lane_B = (base_lane_B + self.lane_offset) % 2
        
        # Calculate effective probabilities (with offset applied)
        if self.lane_offset == 0:
            eff_A_left = lane_probs['A']['left']
            eff_A_right = lane_probs['A']['right']
            eff_B_left = lane_probs['B']['left']
            eff_B_right = lane_probs['B']['right']
        else:
            # Offset flips visual lanes
            eff_A_left = lane_probs['A']['right']
            eff_A_right = lane_probs['A']['left']
            eff_B_left = lane_probs['B']['right']
            eff_B_right = lane_probs['B']['left']
        
        return {
            "in_superposition": self.in_superposition,
            "state_vector": [
                {"real": float(c.real), "imag": float(c.imag)} 
                for c in self.state
            ],
            "probabilities": self.get_probabilities(),
            "lane_probabilities": lane_probs,
            # 4 probability percentages for display
            "prob_A_left": round(eff_A_left * 100, 1),
            "prob_A_right": round(eff_A_right * 100, 1),
            "prob_B_left": round(eff_B_left * 100, 1),
            "prob_B_right": round(eff_B_right * 100, 1),
            "car_A": {
                "lane": visual_lane_A,
                "left_prob": eff_A_left,
                "right_prob": eff_A_right
            },
            "car_B": {
                "lane": visual_lane_B,
                "left_prob": eff_B_left,
                "right_prob": eff_B_right
            },
            "lasers": self.lasers,
            "score": self.score,
            "frame": self.frame,
            "progress": self.get_progress(),
            "running": self.running,
            "paused": self.paused,
            "game_won": self.game_won,
            "total_frames": self.TOTAL_FRAMES,
            "hadamard_uses": self.hadamard_uses,
            "lasers_passed": self.lasers_passed,
            "crash_frame": self.crash_frame,
            "speed_mode": self.speed_mode,
            "lane_offset": self.lane_offset
        }


@app.get("/")
async def root():
    return {"message": "Quantum Racing v4.0 - Real Entanglement", "status": "ONLINE"}


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "4.0.0"}


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
                
                if action == "hadamard":
                    # H key - enter superposition (Hadamard + CNOT)
                    game.apply_hadamard_cnot()
                elif action == "pauli_x_A":
                    # A/D key - switch lane in Universe A
                    game.apply_pauli_x_A()
                elif action == "pauli_x_B":
                    # Arrow keys - switch lane in Universe B
                    game.apply_pauli_x_B()
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
        print(f"Client {client_id} - Score: {game.score}, H uses: {game.hadamard_uses}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)