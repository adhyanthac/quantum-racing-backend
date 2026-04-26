"""
Render deployment entry point.
Re-exports the FastAPI app from quantum-engine.py
"""
import importlib

# Import quantum-engine.py (hyphenated filename requires importlib)
quantum_engine = importlib.import_module("quantum-engine")
app = quantum_engine.app
