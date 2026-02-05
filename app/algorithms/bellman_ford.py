import networkx as nx

def bellman_ford_generator(G, start_node, end_node):
    distances = {node: float('inf') for node in G.nodes()}
    distances[start_node] = 0
    parents = {node: None for node in G.nodes()}
    
    nodes = list(G.nodes())
    num_nodes = len(nodes)
    
    yield {
        "visited": [],
        "frontier": [],
        "current_node": start_node,
        "distances": distances.copy(),
        "parents": parents.copy(),
        "description": "Initialized Bellman-Ford"
    }
    
    # Relax edges |V| - 1 times
    for i in range(num_nodes - 1):
        changed = False
        iteration_nodes = set()
        
        for u, v, data in G.edges(data=True):
            weight = data.get('weight', 1)
            iteration_nodes.add(u)
            iteration_nodes.add(v)
            
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                parents[v] = u
                changed = True
                
                yield {
                    "visited": list(iteration_nodes), # Not really "visited" in same sense, but "touched"
                    "frontier": [],
                    "current_node": v,
                    "distances": distances.copy(),
                    "parents": parents.copy(),
                    "description": f"Round {i+1}: Relaxed {u}->{v}"
                }
                
        if not changed:
            yield {
                "visited": nodes,
                "frontier": [],
                "current_node": end_node,
                "distances": distances.copy(),
                "parents": parents.copy(),
                "description": f"Converged early at round {i+1}"
            }
            break
            
    # Check for negative cycles (optional, though user said +ve weights only)
    # But for completeness:
    for u, v, data in G.edges(data=True):
        if distances[u] + data.get('weight', 1) < distances[v]:
             yield {
                "visited": nodes,
                "frontier": [],
                "current_node": v,
                "distances": distances.copy(),
                "parents": parents.copy(),
                "description": "Negative cycle detected!"
            }
