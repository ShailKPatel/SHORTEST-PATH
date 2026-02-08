from fastapi import APIRouter, HTTPException
from app.models import GraphGenerateRequest, AlgorithmRunRequest, BatchRunRequest
from app.graph_logic import GraphGenerator
from app.algorithms import ALGORITHMS
import networkx as nx
import math
import time
import random

router = APIRouter(prefix="/api", tags=["visualization"])

@router.post("/generate-graph")
async def generate_graph(request: GraphGenerateRequest):
    G = GraphGenerator.generate_graph(
        request.num_nodes, 
        request.density, 
        request.directed, 
        (request.weight_min, request.weight_max),
        request.allow_disconnected
    )
    return GraphGenerator.to_json(G)

@router.post("/run-algorithm")
async def run_algorithm(request: AlgorithmRunRequest):
    if request.algorithm not in ALGORITHMS:
        raise HTTPException(status_code=400, detail="Algorithm not found")
        
    # Reconstruct graph from JSON
    if request.graph['directed']:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
        
    for node in request.graph['nodes']:
        G.add_node(node['id'], x=node['x'], y=node['y'])
        
    for edge in request.graph['edges']:
        G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
        
    algorithm_fn = ALGORITHMS[request.algorithm]
    
    steps = []
    try:
        gen = algorithm_fn(G, request.start_node, request.end_node)
        for step in gen:
            steps.append(step)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Sanitize inputs for JSON (handle infinity)
    def sanitize_floats(obj):
        if isinstance(obj, float):
             if math.isinf(obj) or math.isnan(obj):
                 return "Infinity"
             return obj
        if isinstance(obj, dict):
            return {k: sanitize_floats(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [sanitize_floats(i) for i in obj]
        return obj

    cleaned_steps = sanitize_floats(steps)
    return {"steps": cleaned_steps}

@router.post("/batch-run")
async def batch_run_analysis(request: BatchRunRequest):
    results = []
    
    for _ in range(request.num_graphs):
        # 1. Generate Graph
        G = GraphGenerator.generate_graph(
            num_nodes=request.num_nodes,
            density=0.2, # Fixed for batch? or passed?
            directed=request.directed
        )
        
        # Select random start/end
        nodes = list(G.nodes())
        if len(nodes) < 2:
            continue
            
        start = random.choice(nodes)
        end = random.choice(nodes)
        while end == start:
            end = random.choice(nodes)
            
        # 2. Run All Algorithms
        graph_res = {}
        
        algos_to_run = ALGORITHMS.items()
        if request.algorithms:
            algos_to_run = [(k, v) for k, v in ALGORITHMS.items() if k in request.algorithms]

        for algo_name, algo_fn in algos_to_run:
            start_time = time.perf_counter()
            try:
                # We need to exhaust the generator to get the final state
                gen = algo_fn(G, start, end)
                last_step = None
                step_count = 0
                for step in gen:
                    last_step = step
                    step_count += 1
                
                duration = (time.perf_counter() - start_time) * 1000 # ms
                
                cost = float('inf')
                visited = 0
                
                if last_step:
                     if 'best_cost' in last_step:
                         cost = last_step['best_cost']
                     elif last_step.get('distances') and last_step['distances'].get(end) is not None:
                         cost = last_step['distances'][end]
                     
                     if 'visited' in last_step:
                         visited = len(last_step['visited'])

                graph_res[algo_name] = {
                    "success": cost != float('inf'),
                    "cost": cost,
                    "visited": visited,
                    "time": duration
                }
                
            except Exception as e:
                graph_res[algo_name] = {
                    "success": False,
                    "cost": float('inf'),
                    "visited": 0,
                    "time": 0,
                    "error": str(e)
                }
                
        results.append(graph_res)

    # Sanitize inputs for JSON (handle infinity)
    def sanitize_floats(obj):
        if isinstance(obj, float):
             if math.isinf(obj) or math.isnan(obj):
                 return "Infinity"
             return obj
        if isinstance(obj, dict):
            return {k: sanitize_floats(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [sanitize_floats(i) for i in obj]
        return obj

    return sanitize_floats(results)

import os

@router.get("/algorithm-code/{algorithm_name}")
async def get_algorithm_code(algorithm_name: str):
    # Mapping of UI names to filenames
    FILENAME_MAP = {
        "Dijkstra": "dijkstra.py",
        "A*": "a_star.py",
        "Bellman-Ford": "bellman_ford.py",
        "Uniform Cost Search": "uniform_cost_search.py",
        "Floyd-Warshall": "floyd_warshall.py"
    }
    
    if algorithm_name not in FILENAME_MAP:
        raise HTTPException(status_code=404, detail="Algorithm code not found")
        
    filename = FILENAME_MAP[algorithm_name]
    # Read from algorithms_display directory for educational code
    file_path = os.path.join("app", "algorithms_display", filename)
    
    try:
        if not os.path.exists(file_path):
             raise HTTPException(status_code=404, detail="File not found")
             
        with open(file_path, "r") as f:
            code = f.read()
            
        return {"code": code, "language": "python"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
