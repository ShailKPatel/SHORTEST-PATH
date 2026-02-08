"""
A* SEARCH ALGORITHM
===================

Informed search algorithm that uses heuristics to guide the search.
Combines actual cost g(n) with estimated cost h(n) to goal.

Time Complexity: O(b^d) in worst case, much better with good heuristic
Space Complexity: O(b^d)

Algorithm Steps:
1. Maintain f(n) = g(n) + h(n) for each node
   - g(n): actual cost from start to n
   - h(n): heuristic estimate from n to goal
2. Expand node with lowest f(n)
3. Update costs when better path found

Key Property: If h(n) is admissible (never overestimates), A* is optimal
"""

import heapq

def a_star(graph, start, goal, heuristic):
    """
    Find shortest path using A* search.
    
    Args:
        graph: Dictionary where graph[node] = [(neighbor, cost), ...]
        start: Starting node
        goal: Goal node
        heuristic: Function h(node) estimating cost to goal
    
    Returns:
        (cost, path): Total cost and path as list of nodes
    """
    # Priority queue: (f_score, g_score, node, path)
    # f_score = g_score + h_score
    h_start = heuristic(start)
    pq = [(h_start, 0, start, [start])]
    
    # Track best g_score for each node
    g_scores = {start: 0}
    
    while pq:
        f_score, g_score, node, path = heapq.heappop(pq)
        
        # Goal test
        if node == goal:
            return g_score, path
        
        # Skip if we've found a better path to this node
        if g_score > g_scores.get(node, float('infinity')):
            continue
        
        # Expand neighbors
        for neighbor, edge_cost in graph.get(node, []):
            new_g = g_score + edge_cost
            
            # Only consider if this is a better path
            if new_g < g_scores.get(neighbor, float('infinity')):
                g_scores[neighbor] = new_g
                h_score = heuristic(neighbor)
                f_score = new_g + h_score
                new_path = path + [neighbor]
                heapq.heappush(pq, (f_score, new_g, neighbor, new_path))
    
    # No path found
    return float('infinity'), []
