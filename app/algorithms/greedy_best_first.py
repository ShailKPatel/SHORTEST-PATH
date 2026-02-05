import heapq
import networkx as nx
import math

def heuristic(a, b, G):
     pos_a = G.nodes[a]
     pos_b = G.nodes[b]
     if 'x' in pos_a and 'y' in pos_a:
          return math.sqrt((pos_a['x'] - pos_b['x'])**2 + (pos_a['y'] - pos_b['y'])**2)
     return 0

def greedy_best_first_generator(G, start_node, end_node):
    parents = {node: None for node in G.nodes()}
    visited = set()
    frontier_set = {start_node}
    
    # Priority queue stores (h_cost, node)
    h_start = heuristic(start_node, end_node, G)
    pq = [(h_start, start_node)]
    
    # We maintain distances just for visual consistency, though greedy doesn't use "g" score for sorting
    distances = {node: float('inf') for node in G.nodes()} 
    distances[start_node] = 0

    yield {
        "visited": list(visited),
        "frontier": list(frontier_set),
        "current_node": start_node,
        "distances": distances.copy(),
        "parents": parents.copy(),
        "description": f"Initialized Greedy Best-First. Start: {start_node}"
    }
    
    while pq:
        _, current_node = heapq.heappop(pq)
        
        if current_node in visited:
            continue
            
        visited.add(current_node)
        if current_node in frontier_set:
            frontier_set.remove(current_node)
            
        yield {
            "visited": list(visited),
            "frontier": list(frontier_set),
            "current_node": current_node,
            "distances": distances.copy(),
            "parents": parents.copy(),
            "description": f"Processing {current_node} (heuristic only)"
        }
        
        if current_node == end_node:
            yield {
                "visited": list(visited),
                "frontier": list(frontier_set),
                "current_node": current_node,
                "distances": distances.copy(),
                "parents": parents.copy(),
                "description": f"Goal {end_node} reached!"
            }
            break
            
        for neighbor in G.neighbors(current_node):
            if neighbor not in visited and neighbor not in frontier_set: # Greedy usually doesn't revisit? 
                # Standard Greedy Best First *can* visit nodes, but typically we just add unseen neighbors
                # depending on implementation. Standard graph search version:
                
                weight = G.edges[current_node, neighbor].get('weight', 1)
                distances[neighbor] = distances[current_node] + weight # Just tracking path length
                parents[neighbor] = current_node
                
                h = heuristic(neighbor, end_node, G)
                heapq.heappush(pq, (h, neighbor))
                frontier_set.add(neighbor)
                
                yield {
                    "visited": list(visited),
                    "frontier": list(frontier_set),
                    "current_node": neighbor,
                    "distances": distances.copy(),
                    "parents": parents.copy(),
                    "description": f"Discovered {neighbor}. h: {h:.2f}"
                }
