import heapq
import time
import networkx as nx
from metrics import Metrics

def run_dijkstra(G: nx.DiGraph, start_node, end_node):
    """
    Dijkstra's Algorithm generator.
    Yields: (graph_state, metrics, log_message)
    """
    metrics = Metrics()
    metrics.start_time = time.perf_counter()
    
    # Initialization
    distances = {node: float('inf') for node in G.nodes()}
    distances[start_node] = 0
    parents = {node: None for node in G.nodes()}
    visited = set()
    pq = [(0, start_node)]  # (distance, node)
    
    # Initial Yield
    yield {
        "visited": visited.copy(),
        "processing": {start_node},
        "distances": distances.copy(),
        "parents": parents.copy(),
        "q_nodes": [x[1] for x in pq]
    }, metrics, f"Initialized Dijkstra. Start node: {start_node}"
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
        # Optimization: If we found end_node, we can stop (for single pair)
        # But for full visualization, we might want to continue or stop.
        # Let's stop early for now if target is found and processed.
        
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        yield {
            "visited": visited.copy(),
            "processing": {current_node},
            "distances": distances.copy(),
            "parents": parents.copy(),
            "q_nodes": [x[1] for x in pq]
        }, metrics, f"Processing node {current_node} (dist: {current_dist})"
        
        if current_node == end_node:
            metrics.path_found = True
            metrics.final_cost = current_dist
            yield {
                "visited": visited.copy(),
                "processing": set(),
                "distances": distances.copy(),
                "parents": parents.copy(),
                "q_nodes": []
            }, metrics, f"Target {end_node} reached!"
            break
            
        for neighbor in G.neighbors(current_node):
            weight = G.edges[current_node, neighbor].get('weight', 1)
            new_dist = current_dist + weight
            
            metrics.comparisons += 1
            
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parents[neighbor] = current_node
                heapq.heappush(pq, (new_dist, neighbor))
                metrics.relaxations += 1
                
                yield {
                    "visited": visited.copy(),
                    "processing": {current_node, neighbor},
                    "distances": distances.copy(),
                    "parents": parents.copy(),
                    "q_nodes": [x[1] for x in pq]
                }, metrics, f"Relaxing edge {current_node}->{neighbor}. New dist: {new_dist}"
    
    metrics.end_time = time.perf_counter()
    if distances[end_node] == float('inf'):
         yield {
            "visited": visited.copy(),
            "processing": set(),
            "distances": distances.copy(),
            "parents": parents.copy(),
             "q_nodes": []
        }, metrics, f"Target {end_node} unreachable."
