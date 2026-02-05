import heapq
import networkx as nx

def uniform_cost_search_generator(G, start_node, end_node):
    # Uniform Cost Search is identical to Dijkstra's Algorithm for this context.
    # It explores the path with the lowest cumulative cost (distance) using a Priority Queue.
    
    distances = {node: float('inf') for node in G.nodes()}
    distances[start_node] = 0
    parents = {node: None for node in G.nodes()}
    visited = set()
    frontier_set = {start_node}
    pq = [(0, start_node)]
    
    yield {
        "visited": list(visited),
        "frontier": list(frontier_set),
        "current_node": start_node,
        "distances": distances.copy(),
        "parents": parents.copy(),
        "description": f"Initialized UCS. Start: {start_node}"
    }
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
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
            "description": f"Processing node {current_node} (Cost: {current_dist})"
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
            new_dist = current_dist + weight
            
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parents[neighbor] = current_node
                heapq.heappush(pq, (new_dist, neighbor))
                frontier_set.add(neighbor)
                
                yield {
                    "visited": list(visited),
                    "frontier": list(frontier_set),
                    "current_node": neighbor, # Highlight the neighbor being updated
                    "distances": distances.copy(),
                    "parents": parents.copy(),
                    "description": f"Updated neighbor {neighbor}. New cost: {new_dist}"
                }
