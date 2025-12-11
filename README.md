# Minimal Workflow Engine (FastAPI Backend Assignment)

This project implements a small but fully functional workflow/graph execution engine using FastAPI.  
The engine supports node-based execution, shared state management, branching, looping, and execution logging.  
A sample "Data Quality Pipeline" workflow is included as the example agent.

---

## 📁 Project Structure (/app folder)

- app/main.py → FastAPI entrypoint  
- app/api/  
  - graph_routes.py → API endpoints (create graph, run graph, get state)  
  - ws_routes.py → WebSocket endpoint for log streaming  
- app/core/  
  - engine.py → Graph execution engine  
  - models.py → Pydantic models  
  - registry.py → Tool registry for node functions  
  - storage.py → In-memory graph/run storage  
  - ws_manager.py → WebSocket connection manager  
- app/workflows/  
  - data_quality.py → Example workflow implementation (Data Quality Pipeline)

---

## ▶️ How to Run

1. Clone the repository:
   
2. git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

3. Create and activate a virtual environment:
python -m venv venv
.\venv\Scripts\activate (Windows)
source venv/bin/activate (Mac/Linux)

4.pip install -r requirements.txt

5. Start the FastAPI server:
python -m uvicorn app.main:app --reload

6. Open the interactive API docs:
http://127.0.0.1:8000/docs

7. Use the endpoints:
- **POST /graph/create** → Define a workflow graph  
- **POST /graph/run** → Run the workflow with an initial state  
- **GET /graph/state/{run_id}** → View execution state and logs  
- **WebSocket: ws://127.0.0.1:8000/ws/logs** → Stream real-time logs  

---

## ⚙️ What the Workflow Engine Supports

### ✔ Node-Based Execution  
- Each workflow node maps to a Python function (“tool”).  
- Nodes read and modify a shared state dictionary.

### ✔ Shared State Propagation  
- State moves from one node to the next.  
- Each node can update or replace parts of the state.

### ✔ Branching  
- A node can override the next step by setting `__next_node__` in state.  
- Enables conditional routing.

### ✔ Looping  
- If a node sets `__next_node__` pointing to an earlier node, the engine loops.  
- Used to repeat steps until conditions are met.

### ✔ Execution Logging  
- Each step records:  
- node executed  
- timestamps  
- tool used  
- snapshot of state  
- message  

### ✔ WebSocket Log Streaming (Optional Extra Implemented)  
- Every step broadcast live to connected clients.  
- Helps visualize workflow progress in real time.

### ✔ In-Memory Graph & Run Storage  
- Graph definitions stored in memory  
- Run histories stored with logs and final state  
- Simple and lightweight as required

### ✔ Example Workflow: Data Quality Pipeline  
- Profiles tabular data  
- Identifies anomalies  
- Generates simple rules  
- Applies rules  
- Loops until anomaly count <= threshold  

---

##  Summary

This project demonstrates a clean and modular implementation of:

- A minimal workflow engine  
- Shared-state execution model  
- Branching and looping  
- Logging and real-time WebSocket streaming  
- A fully functional example workflow  

