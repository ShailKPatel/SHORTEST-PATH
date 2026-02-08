"""
UNIFORM COST SEARCH (UCS)
==========================

A variant of Dijkstra's algorithm commonly used in AI/search problems.
Expands nodes in order of increasing path cost.

Time Complexity: O(b^(C*/ε)) where C* is optimal cost, ε is min edge cost
Space Complexity: O(b^(C*/ε))

Algorithm Steps:
1. Start with source node in priority queue (cost 0)
2. Pop node with lowest cost
3. If goal, return path
4. Expand neighbors and add to queue with cumulative cost

Difference from Dijkstra: UCS is goal-directed and stops when goal is found
"""

import heapq

def uniform_cost_search(graph, start, goal):
    """
    Find shortest path using Uniform Cost Search.
    
    Args:
        graph: Dictionary where graph[node] = [(neighbor, cost), ...]
        start: Starting node
        goal: Goal node
    
    Returns:
        (cost, path): Total cost and path as list of nodes
    """
    # Priority queue: (cost, node, path)
    pq = [(0, start, [start])]
    visited = set()
    
    while pq:
        cost, node, path = heapq.heappop(pq)
        
        # Skip if already visited
        if node in visited:
            continue
        
        visited.add(node)
        
        # Goal test: check when expanding, not when generating
        if node == goal:
            return cost, path
        
        # Expand neighbors
        for neighbor, edge_cost in graph.get(node, []):
            if neighbor not in visited:
                new_cost = cost + edge_cost
                new_path = path + [neighbor]
                heapq.heappush(pq, (new_cost, neighbor, new_path))
    
    # No path found
    return float('infinity'), []
