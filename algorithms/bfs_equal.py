import collections
import time
import networkx as nx
from metrics import Metrics

def run_bfs_equal(G: nx.DiGraph, start_node, end_node):
    """
    BFS for Shortest Path (Unweighted/Equal Weights).
    Yields: (graph_state, metrics, log_message)
    """
    metrics = Metrics()
    metrics.start_time = time.perf_counter()
    
    distances = {node: float('inf') for node in G.nodes()}
    distances[start_node] = 0
    parents = {node: None for node in G.nodes()}
    visited = set([start_node])
    queue = collections.deque([start_node])
    
    yield {
        "visited": visited.copy(),
        "processing": {start_node},
        "distances": distances.copy(),
        "parents": parents.copy(),
        "q_nodes": list(queue)
    }, metrics, f"Initialized BFS. Start node: {start_node}"
    
    while queue:
        current_node = queue.popleft()
        
        yield {
            "visited": visited.copy(),
            "processing": {current_node},
            "distances": distances.copy(),
            "parents": parents.copy(),
            "q_nodes": list(queue)
        }, metrics, f"Processing {current_node} (dist: {distances[current_node]})"
        
        if current_node == end_node:
            metrics.path_found = True
            metrics.final_cost = distances[end_node]
            metrics.end_time = time.perf_counter()
            yield {
                "visited": visited.copy(),
                "processing": set(),
                "distances": distances.copy(),
                "parents": parents.copy(),
                "q_nodes": []
            }, metrics, f"Target {end_node} reached!"
            break
            
        for neighbor in G.neighbors(current_node):
            if neighbor not in visited:
                visited.add(neighbor)
                distances[neighbor] = distances[current_node] + 1
                parents[neighbor] = current_node
                queue.append(neighbor)
                
                metrics.comparisons += 1 # Conceptually checking if visited
                metrics.relaxations += 1 # "Relaxing" by finding shortest path in unweighted
                
                yield {
                    "visited": visited.copy(),
                    "processing": {current_node, neighbor},
                    "distances": distances.copy(),
                    "parents": parents.copy(),
                    "q_nodes": list(queue)
                }, metrics, f"Discovered {neighbor}. Dist: {distances[neighbor]}"
    
    metrics.end_time = time.perf_counter()
    if distances[end_node] == float('inf'):
         yield {
            "visited": visited.copy(),
            "processing": set(),
            "distances": distances.copy(),
            "parents": parents.copy(),
             "q_nodes": []
        }, metrics, f"Target {end_node} unreachable."
