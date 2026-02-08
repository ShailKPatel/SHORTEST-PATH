"""
BELLMAN-FORD SHORTEST PATH ALGORITHM
=====================================

Single-source shortest path algorithm that handles negative edge weights.
Uses dynamic programming with edge relaxation.

Time Complexity: O(V * E)
Space Complexity: O(V)

Algorithm Steps:
1. Initialize distances to all nodes as infinity, except source (0)
2. Relax all edges V-1 times
3. Check for negative cycles (optional)

Key Advantage: Can detect negative weight cycles
"""

def bellman_ford(graph, start, end):
    """
    Find shortest path using Bellman-Ford algorithm.
    
    Args:
        graph: Dictionary where graph[node] = [(neighbor, weight), ...]
        start: Starting node
        end: Destination node
    
    Returns:
        (distance, path): Shortest distance and path, or None if negative cycle
    """
    # Get all nodes
    nodes = set(graph.keys())
    for neighbors in graph.values():
        for neighbor, _ in neighbors:
            nodes.add(neighbor)
    
    # Initialize distances and parents
    distances = {node: float('infinity') for node in nodes}
    distances[start] = 0
    parents = {node: None for node in nodes}
    
    # Relax edges V-1 times
    for _ in range(len(nodes) - 1):
        for node in graph:
            for neighbor, weight in graph.get(node, []):
                if distances[node] + weight < distances[neighbor]:
                    distances[neighbor] = distances[node] + weight
                    parents[neighbor] = node
    
    # Check for negative cycles
    for node in graph:
        for neighbor, weight in graph.get(node, []):
            if distances[node] + weight < distances[neighbor]:
                return None, []  # Negative cycle detected
    
    # Reconstruct path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = parents[node]
    path.reverse()
    
    return distances[end], path
