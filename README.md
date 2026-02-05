# Shortest Path Visualizer

A verification and educational tool to demonstrate shortest-path algorithms on weighted graphs.

## Features

- **Interactive Visualization**: Watch Dijkstra, A*, Bellman-Ford, and others explore the graph in real-time.
- **Pac-Man Theme**: Retro-styled UI for a unique user experience.
- **Batch Analysis**: run 30 random graphs to statistically compare algorithm performance.
- **FastAPI Backend**: Robust API-driven architecture.
- **Vanilla JS Frontend**: Lightweight, responsive visualization using HTML5 Canvas.

## Algorithms
1. **Dijkstra**: Guaranteed optimal.
2. **A* Search**: Heuristic-driven (Euclidean distance).
3. **Greedy Best-First**: Fast but not guaranteed optimal.
4. **Bellman-Ford**: Handles negative weights (though we restrict to positive for this demo).
5. **Bidirectional Dijkstra**: Meet-in-the-middle optimization.
6. **Floyd-Warshall**: All-pairs shortest path (visualized by pivot).

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
