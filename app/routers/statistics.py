from fastapi import APIRouter, HTTPException
from app.models import BatchRunRequest
from app.graph_logic import GraphGenerator
from app.algorithms import ALGORITHMS
import time
import networkx as nx
import statistics as stats

router = APIRouter(prefix="/api", tags=["statistics"])

@router.post("/batch-run")
async def batch_run(request: BatchRunRequest):
    results = {algo_name: {
        "success_count": 0,
        "total_cost": 0,
        "total_nodes_expanded": 0,
        "execution_times": [],
        "costs": []
    } for algo_name in ALGORITHMS.keys()}
    
    # We will exclude Floyd-Warshall from batch by default if too slow, or keep it manageable.
    # Given N=30, FW is fast enough (30^3 = 27000 ops).
    
    for i in range(request.num_graphs):
        # Generate random graph
        G = GraphGenerator.generate_graph(
            num_nodes=request.num_nodes,
            density=request.density,
            directed=False, # Default for comparison
            weight_range=(1, 10),
            allow_disconnected=False
        )
        
        start_node = 0
        end_node = request.num_nodes - 1
        
        # Calculate Optimal Cost (Baseline: Dijkstra)
        # We run Dijkstra first to get the ground truth
        try:
            dijkstra_cost = nx.shortest_path_length(G, start_node, end_node, weight='weight')
        except nx.NetworkXNoPath:
            continue # Skip disconnected components if they happen
            
        for algo_name, algo_fn in ALGORITHMS.items():
            start_time = time.perf_counter()
            
            # Run algorithm (consume generator)
            gen = algo_fn(G, start_node, end_node)
            final_step = None
            nodes_expanded = 0
            
            try:
                for step in gen:
                    final_step = step
                    nodes_expanded += 1
            except Exception:
                pass
                
            end_time = time.perf_counter()
            
            # Analyze result
            if final_step and final_step['current_node'] == end_node:
                cost = final_step['distances'][end_node]
                results[algo_name]["success_count"] += 1
                results[algo_name]["total_cost"] += cost
                results[algo_name]["costs"].append(cost)
                results[algo_name]["total_nodes_expanded"] += nodes_expanded
                results[algo_name]["execution_times"].append(end_time - start_time)
            else:
                 # Didn't finish??
                 pass

    # Aggregation
    final_stats = []
    
    # Need to handle empty results if all graphs failed
    
    for algo, data in results.items():
        count = data["success_count"]
        if count == 0:
             final_stats.append({
                "algorithm": algo,
                "success_rate": 0,
                "avg_cost": 0,
                "avg_nodes": 0,
                "avg_time": 0
            })
             continue
             
        final_stats.append({
            "algorithm": algo,
            "success_rate": count / request.num_graphs,
            "avg_cost": data["total_cost"] / count,
            "avg_nodes": data["total_nodes_expanded"] / count,
            "avg_time": sum(data["execution_times"]) / count
        })
        
    return {"stats": final_stats}
