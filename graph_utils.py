import networkx as nx

def parse_edge_list(edge_list_str: str, directed: bool = True) -> nx.DiGraph:
    """
    Parses a string of edges (u v w) into a NetworkX graph.
    Format: "u v w" (node1 node2 weight) or "u v" (weight=1).
    """
    G = nx.DiGraph() if directed else nx.Graph()
    
    lines = edge_list_str.strip().split('\n')
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            u, v = parts[0], parts[1]
            if len(parts) >= 3:
                try:
                    w = int(parts[2])
                except ValueError:
                    w = 1
            else:
                w = 1
            
            G.add_edge(u, v, weight=w, label=str(w))
            
    return G

def reverse_graph(G: nx.DiGraph) -> nx.DiGraph:
    """
    Reverses the direction of all edges in the graph.
    Used for Single-Destination shortest path problems.
    """
    return G.reverse(copy=True)
