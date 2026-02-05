import networkx as nx
import random

def generate_grid_graph(rows: int, cols: int, weighted: bool = True, seed: int = None) -> nx.DiGraph:
    """
    Generates a 2D Grid Graph.
    Nodes are labeled 0 to (rows*cols - 1).
    Edges connect to adjacent neighbors (Right, Down).
    """
    if seed is not None:
        random.seed(seed)
        
    G = nx.grid_2d_graph(rows, cols)
    G = nx.DiGraph(G) # Convert to directed
    
    # Relabel nodes from (r, c) to integer index
    mapping = { (r, c): r * cols + c for r in range(rows) for c in range(cols) }
    G = nx.relabel_nodes(G, mapping)
    
    for u, v in G.edges():
        w = random.randint(1, 10) if weighted else 1
        G.edges[u, v]['weight'] = w
        G.edges[u, v]['label'] = str(w)

    # Add position attributes for visualization and A*
    for r in range(rows):
        for c in range(cols):
            node_idx = r * cols + c
            # Store (r, c) or (c, -r) depending on desired visual layout
            # PyVis and general coordinate systems usually like (x, y) where y is up.
            # But matrix (r, c) is y down. Let's store logic (row, col) as tuple.
            if node_idx in G:
                G.nodes[node_idx]['pos'] = (r, c)

        
    return G
