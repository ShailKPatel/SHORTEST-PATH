import heapq
import time
import networkx as nx
from metrics import Metrics

def manhattan_distance(u_pos, v_pos):
    return abs(u_pos[0] - v_pos[0]) + abs(u_pos[1] - v_pos[1])

def run_a_star(G: nx.DiGraph, start_node, end_node):
    """
    A* Algorithm generator.
    heuristic: Manhattan distance if nodes have 'pos' attribute (grid), else 0.
    Yields: (graph_state, metrics, log_message)
    """
    metrics = Metrics()
    metrics.start_time = time.perf_counter()
    
    # Check if nodes have 'pos' attribute
    has_pos = 'pos' in G.nodes[start_node]
    end_pos = G.nodes[end_node].get('pos') if has_pos else None
    
    def h(n):
        if has_pos and end_pos and 'pos' in G.nodes[n]:
            return manhattan_distance(G.nodes[n]['pos'], end_pos)
        return 0
    
    distances = {node: float('inf') for node in G.nodes()}
    distances[start_node] = 0
    parents = {node: None for node in G.nodes()}
    visited = set()
    
    # Priority Queue stores (f_score, node) where f = g + h
    pq = [(0 + h(start_node), start_node)]
    
    yield {
        "visited": visited.copy(),
        "processing": {start_node},
        "distances": distances.copy(),
        "parents": parents.copy(),
        "q_nodes": [x[1] for x in pq]
    }, metrics, f"Initialized A*. h(start)={h(start_node)}"
    
    while pq:
        _, current_node = heapq.heappop(pq)
        
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        yield {
            "visited": visited.copy(),
            "processing": {current_node},
            "distances": distances.copy(),
            "parents": parents.copy(),
            "q_nodes": [x[1] for x in pq]
        }, metrics, f"Processing {current_node} (g={distances[current_node]}, h={h(current_node)})"
        
        if current_node == end_node:
            metrics.path_found = True
            metrics.final_cost = distances[end_node]
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
            new_g = distances[current_node] + weight
            
            metrics.comparisons += 1
            
            if new_g < distances[neighbor]:
                distances[neighbor] = new_g
                parents[neighbor] = current_node
                f_score = new_g + h(neighbor)
                heapq.heappush(pq, (f_score, neighbor))
                metrics.relaxations += 1
                
                yield {
                    "visited": visited.copy(),
                    "processing": {current_node, neighbor},
                    "distances": distances.copy(),
                    "parents": parents.copy(),
                    "q_nodes": [x[1] for x in pq]
                }, metrics, f"Relaxing {current_node}->{neighbor}. New g: {new_g}"
    
    metrics.end_time = time.perf_counter()
    if distances[end_node] == float('inf'):
         yield {
            "visited": visited.copy(),
            "processing": set(),
            "distances": distances.copy(),
            "parents": parents.copy(),
             "q_nodes": []
        }, metrics, f"Target {end_node} unreachable."
