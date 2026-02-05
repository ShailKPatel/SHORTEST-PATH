import networkx as nx

def floyd_warshall_generator(G, start_node, end_node):
    # Floyd-Warshall is O(N^3), very slow for visualization but requested.
    # It computes ALL pairs. We will just yield progress.
    
    nodes = list(G.nodes())
    n = len(nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    
    # Initialize dist matrix
    dist = [[float('inf')] * n for _ in range(n)]
    
    # Set init distances
    for i in range(n):
        dist[i][i] = 0
        
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 1)
        dist[node_to_idx[u]][node_to_idx[v]] = weight
        if not G.is_directed():
             dist[node_to_idx[v]][node_to_idx[u]] = weight

    # Visualization: yield snapshots occasionally
    count = 0
    yield_freq = max(1, n * n // 100) # limit yields
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    
                count += 1
                if count % yield_freq == 0:
                     # Convert current dist row for start_node to our standard 'distances' dict
                    start_idx = node_to_idx[start_node]
                    curr_dists = {nodes[x]: dist[start_idx][x] for x in range(n)}
                    
                    yield {
                        "visited": [],
                        "frontier": [nodes[k]], # Show k as the pivot
                        "current_node": nodes[i] if count % 5 == 0 else nodes[j], # Just some activity
                        "distances": curr_dists,
                        "parents": {}, # FW doesn't easily track parents without extra matrix
                        "description": f"Pivot k={nodes[k]}, checking i={nodes[i]}, j={nodes[j]}"
                    }

    # Final yield
    start_idx = node_to_idx[start_node]
    curr_dists = {nodes[x]: dist[start_idx][x] for x in range(n)}
    yield {
        "visited": nodes,
        "frontier": [],
        "current_node": end_node,
        "distances": curr_dists,
        "parents": {},
        "description": "Floyd-Warshall Completed"
    }
