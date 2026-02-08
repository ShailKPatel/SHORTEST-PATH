"""
DIJKSTRA'S SHORTEST PATH ALGORITHM
===================================

Classic single-source shortest path algorithm for graphs with non-negative edge weights.
Uses a priority queue to greedily select the closest unvisited node.

Time Complexity: O((V + E) log V) with binary heap
Space Complexity: O(V)

Algorithm Steps:
1. Initialize distances to all nodes as infinity, except source (0)
2. Use a min-heap priority queue to track nodes by distance
3. For each node, relax all outgoing edges
4. Continue until destination is reached or queue is empty
"""

import heapq

def dijkstra(graph, start, end):
    """
    Find shortest path from start to end using Dijkstra's algorithm.
    
    Args:
        graph: Dictionary where graph[node] = [(neighbor, weight), ...]
        start: Starting node
        end: Destination node
    
    Returns:
        (distance, path): Shortest distance and path as list of nodes
    """
    # Initialize distances and parent tracking
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    parents = {node: None for node in graph}
    
    # Priority queue: (distance, node)
    pq = [(0, start)]
    visited = set()
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        # Skip if already visited
        if current in visited:
            continue
        
        visited.add(current)
        
        # Found destination
        if current == end:
            break
        
        # Relax edges to neighbors
        for neighbor, weight in graph.get(current, []):
            new_dist = current_dist + weight
            
            # Update if we found a shorter path
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parents[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
    
    # Reconstruct path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = parents[node]
    path.reverse()
    
    return distances[end], path


# Example Usage:
if __name__ == "__main__":
    # Graph representation: node -> [(neighbor, weight), ...]
    graph = {
        'A': [('B', 4), ('C', 2)],
        'B': [('C', 1), ('D', 5)],
        'C': [('D', 8), ('E', 10)],
        'D': [('E', 2)],
        'E': []
    }
    
    distance, path = dijkstra(graph, 'A', 'E')
    print(f"Shortest distance: {distance}")
    print(f"Path: {' -> '.join(path)}")
