import time
import networkx as nx
from metrics import Metrics

def run_dag_shortest(G: nx.DiGraph, start_node, end_node):
    """
    DAG Shortest Path using Topological Sort.
    Yields: (graph_state, metrics, log_message)
    """
    metrics = Metrics()
    metrics.start_time = time.perf_counter()
    
    distances = {node: float('inf') for node in G.nodes()}
    distances[start_node] = 0
    parents = {node: None for node in G.nodes()}
    
    try:
        topo_order = list(nx.topological_sort(G))
    except nx.NetworkXUnfeasible:
        metrics.end_time = time.perf_counter()
        yield {}, metrics, "Error: Graph is not a DAG (Cycle detected)."
        return

    yield {
        "visited": set(),
        "processing": set(),
        "distances": distances.copy(),
        "parents": parents.copy(),
        "q_nodes": topo_order
    }, metrics, f"Topological Sort Computed: {topo_order}"
    
    # Process in topological order
    for u in topo_order:
        # If we can't reach u, we can't reach its neighbors via u
        if distances[u] == float('inf'):
            continue
            
        yield {
            "visited": set(),
            "processing": {u},
            "distances": distances.copy(),
            "parents": parents.copy(),
            "q_nodes": []
        }, metrics, f"Processing {u} (dist: {distances[u]})"

        for v in G.neighbors(u):
            weight = G.edges[u, v].get('weight', 1)
            metrics.comparisons += 1
            
            if distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                parents[v] = u
                metrics.relaxations += 1
                
                yield {
                    "visited": set(),
                    "processing": {u, v},
                    "distances": distances.copy(),
                    "parents": parents.copy(),
                    "q_nodes": []
                }, metrics, f"Relaxed {u}->{v}. New dist: {distances[v]}"
        
    metrics.final_cost = distances[end_node]
    metrics.path_found = (distances[end_node] != float('inf'))
    metrics.end_time = time.perf_counter()
    
    yield {
        "visited": set(G.nodes()),
        "processing": set(),
        "distances": distances.copy(),
        "parents": parents.copy(),
        "q_nodes": []
    }, metrics, "DAG Shortest Path Complete"
