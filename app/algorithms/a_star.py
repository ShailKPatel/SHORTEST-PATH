import heapq
import networkx as nx
import math

def heuristic(a, b, G):
    # Simple Euclidean distance heuristic (assuming x, y coords exist)
    # If not, return 0 (dijkstra fallback)
    pos_a = G.nodes[a]
    pos_b = G.nodes[b]
    if 'x' in pos_a and 'y' in pos_a:
         return math.sqrt((pos_a['x'] - pos_b['x'])**2 + (pos_a['y'] - pos_b['y'])**2)
    return 0

def a_star_generator(G, start_node, end_node):
    distances = {node: float('inf') for node in G.nodes()} # g_score
    distances[start_node] = 0
    f_scores = {node: float('inf') for node in G.nodes()}
    
    h_start = heuristic(start_node, end_node, G)
    f_scores[start_node] = h_start
    
    parents = {node: None for node in G.nodes()}
    visited = set()
    frontier_set = {start_node}
    pq = [(h_start, start_node)] # Sort by f_score
    
    yield {
        "visited": list(visited),
        "frontier": list(frontier_set),
        "current_node": start_node,
        "distances": distances.copy(),
        "parents": parents.copy(),
        "description": f"Initialized A*. Start: {start_node}, h: {h_start:.2f}"
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
            "description": f"Processing {current_node}. g: {distances[current_node]:.2f}"
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
            weight = G.edges[current_node, neighbor].get('weight', 1)
            tentative_g = distances[current_node] + weight
            
            if tentative_g < distances[neighbor]:
                distances[neighbor] = tentative_g
                parents[neighbor] = current_node
                h = heuristic(neighbor, end_node, G)
                f = tentative_g + h
                f_scores[neighbor] = f
                
                heapq.heappush(pq, (f, neighbor))
                frontier_set.add(neighbor)
                
                yield {
                    "visited": list(visited),
                    "frontier": list(frontier_set),
                    "current_node": neighbor,
                    "distances": distances.copy(),
                    "parents": parents.copy(),
                    "description": f"Updated {neighbor}. g: {tentative_g:.2f}, h: {h:.2f}, f: {f:.2f}"
                }
