"""
FLOYD-WARSHALL ALL-PAIRS SHORTEST PATH ALGORITHM
=================================================

Finds shortest paths between all pairs of nodes using dynamic programming.
Works with negative edges but not negative cycles.

Time Complexity: O(V³)
Space Complexity: O(V²)

Algorithm Steps:
1. Initialize distance matrix with direct edge weights
2. For each intermediate node k, update distances[i][j]
3. If path through k is shorter, update the distance

Key Idea: dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
"""

def floyd_warshall(graph):
    """
    Find all-pairs shortest paths using Floyd-Warshall algorithm.
    
    Args:
        graph: Dictionary where graph[node] = [(neighbor, weight), ...]
    
    Returns:
        (distances, next_node): Distance matrix and path reconstruction matrix
    """
    # Get all nodes
    nodes = list(set(graph.keys()) | {n for neighbors in graph.values() for n, _ in neighbors})
    n = len(nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    
    # Initialize distance matrix
    INF = float('infinity')
    dist = [[INF] * n for _ in range(n)]
    next_node = [[None] * n for _ in range(n)]
    
    # Distance from node to itself is 0
    for i in range(n):
        dist[i][i] = 0
    
    # Set direct edge weights
    for node in graph:
        i = node_to_idx[node]
        for neighbor, weight in graph[node]:
            j = node_to_idx[neighbor]
            dist[i][j] = weight
            next_node[i][j] = neighbor
    
    # Floyd-Warshall: try all intermediate nodes
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_node[i][j] = next_node[i][k]
    
    return dist, next_node, nodes, node_to_idx
