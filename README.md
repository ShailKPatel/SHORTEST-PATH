# Shortest Path Visualizer

A verification and educational tool to demonstrate shortest-path algorithms on weighted graphs.

## Features

- **Interactive Visualization**: Watch algorithms explore the graph in real-time from start (Pac-Man 🟡) to goal (Ghost 👻).
- **Single-Source → Single-Target**: All algorithms find the shortest path from one start node to one end node.
- **Pac-Man Theme**: Retro-styled UI for a unique user experience.
- **Batch Analysis**: Run multiple random graphs to statistically compare algorithm performance.
- **FastAPI Backend**: Robust API-driven architecture.
- **Vanilla JS Frontend**: Lightweight, responsive visualization using HTML5 Canvas.

## Algorithms
1. **Dijkstra**: Guaranteed optimal for non-negative weights.
2. **A* Search**: Heuristic-driven (Euclidean distance) - optimal with admissible heuristic.
3. **Greedy Best-First**: Fast but not guaranteed optimal.
4. **Bellman-Ford**: Handles negative weights (restricted to positive for this demo).
5. **Uniform Cost Search**: Equivalent to Dijkstra for non-negative weights.
6. **Floyd-Warshall**: All-pairs shortest path (adapted for single-source visualization).

## Setup & Run

1.  **Create and Activate Virtual Environment**:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Server**:
    ```bash
    uvicorn app.main:app --reload
    ```

    *Alternatively, if not activated:*
    ```bash
    .venv\Scripts\python -m uvicorn app.main:app --reload
    ```

4.  **Open Access**:
    - Go to [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Structure
- `app/main.py`: Entry point.
- `app/algorithms/`: Algorithm implementations.
- `app/routers/`: API endpoints.
- `app/static/`: CSS and JS files.
- `app/templates/`: HTML files.
