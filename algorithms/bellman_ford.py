import time
import networkx as nx
from metrics import Metrics

def run_bellman_ford(G: nx.DiGraph, start_node, end_node):
    """
    Bellman-Ford Algorithm generator.
    Yields: (graph_state, metrics, log_message)
    """
    metrics = Metrics()
    metrics.start_time = time.perf_counter()
    
    distances = {node: float('inf') for node in G.nodes()}
    distances[start_node] = 0
    parents = {node: None for node in G.nodes()}
    
    nodes = list(G.nodes())
    num_nodes = len(nodes)
    edges = list(G.edges(data=True))
    
    yield {
        "visited": set(),
        "processing": {start_node},
        "distances": distances.copy(),
        "parents": parents.copy(),
        "q_nodes": []
    }, metrics, f"Initialized Bellman-Ford. Start node: {start_node}"
    
    # Relax edges |V| - 1 times
    for i in range(num_nodes - 1):
        changed = False
        epoch_log = f"Iteration {i+1}/{num_nodes-1}"
        
        yield {
            "visited": set(),
            "processing": set(),
            "distances": distances.copy(),
            "parents": parents.copy(),
            "q_nodes": []
        }, metrics, f"Starting {epoch_log}"
        
        for u, v, data in edges:
            weight = data.get('weight', 1)
            metrics.comparisons += 1
            
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                parents[v] = u
                metrics.relaxations += 1
                changed = True
                
                yield {
                    "visited": set(),
                    "processing": {u, v},
                    "distances": distances.copy(),
                    "parents": parents.copy(),
                    "q_nodes": []
                }, metrics, f"Relaxed {u}->{v}. New dist: {distances[v]}"
        
        if not changed:
            yield {
                "visited": set(),
                "processing": set(),
                "distances": distances.copy(),
                "parents": parents.copy(),
                "q_nodes": []
            }, metrics, "Optimization: No changes in this iteration. Stopping early."
            break
            
    # Check for negative value cycles
    has_negative_cycle = False
    for u, v, data in edges:
        weight = data.get('weight', 1)
        if distances[u] != float('inf') and distances[u] + weight < distances[v]:
             has_negative_cycle = True
             yield {
                "visited": set(),
                "processing": {u, v},
                "distances": distances.copy(),
                "parents": parents.copy(),
                "q_nodes": []
            }, metrics, f"Negative Cycle Detected at {u}->{v}!"
             break

    metrics.end_time = time.perf_counter()
    metrics.final_cost = distances[end_node]
    metrics.path_found = (distances[end_node] != float('inf')) and not has_negative_cycle
