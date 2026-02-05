import collections
import time
import networkx as nx
from metrics import Metrics

def run_spfa(G: nx.DiGraph, start_node, end_node):
    """
    Shortest Path Faster Algorithm (SPFA).
    Improvement of Bellman-Ford using a Queue.
    Yields: (graph_state, metrics, log_message)
    """
    metrics = Metrics()
    metrics.start_time = time.perf_counter()
    
    distances = {node: float('inf') for node in G.nodes()}
    distances[start_node] = 0
    parents = {node: None for node in G.nodes()}
    
    queue = collections.deque([start_node])
    in_queue = {node: False for node in G.nodes()}
    in_queue[start_node] = True
    
    # Cycle detection: count updates per node
    update_count = {node: 0 for node in G.nodes()}
    num_nodes = len(G.nodes())
    
    yield {
        "visited": set(),
        "processing": {start_node},
        "distances": distances.copy(),
        "parents": parents.copy(),
        "q_nodes": list(queue)
    }, metrics, f"Initialized SPFA. Start node: {start_node}"
    
    while queue:
        u = queue.popleft()
        in_queue[u] = False
        
        yield {
            "visited": set(),
            "processing": {u},
            "distances": distances.copy(),
            "parents": parents.copy(),
            "q_nodes": list(queue)
        }, metrics, f"Processing {u} (dist: {distances[u]})"
        
        for v in G.neighbors(u):
            weight = G.edges[u, v].get('weight', 1)
            metrics.comparisons += 1
            
            if distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                parents[v] = u
                metrics.relaxations += 1
                
                if not in_queue[v]:
                    queue.append(v)
                    in_queue[v] = True
                    update_count[v] += 1
                    
                    if update_count[v] > num_nodes:
                         yield {
                            "visited": set(),
                            "processing": {u, v},
                            "distances": distances.copy(),
                            "parents": parents.copy(),
                            "q_nodes": []
                        }, metrics, f"Negative Cycle Detected at {v}!"
                         metrics.end_time = time.perf_counter()
                         return
                    
                yield {
                    "visited": set(),
                    "processing": {u, v},
                    "distances": distances.copy(),
                    "parents": parents.copy(),
                    "q_nodes": list(queue)
                }, metrics, f"Relaxed {u}->{v}. New dist: {distances[v]}"

    metrics.final_cost = distances[end_node]
    metrics.path_found = (distances[end_node] != float('inf'))
    metrics.end_time = time.perf_counter()
    
    yield {
        "visited": set(),
        "processing": set(),
        "distances": distances.copy(),
        "parents": parents.copy(),
        "q_nodes": []
    }, metrics, "SPFA Complete"
