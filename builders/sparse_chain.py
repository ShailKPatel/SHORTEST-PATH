import networkx as nx
import random

def generate_sparse_chain(num_nodes: int, weighted: bool = True, seed: int = None) -> nx.DiGraph:
    """
    Generates a long chain graph: 0->1->2->...->n-1.
    Adds a few random noise edges to make it interesting but still sparse.
    """
    if seed is not None:
        random.seed(seed)
        
    G = nx.DiGraph()
    G.add_nodes_from(range(num_nodes))
    
    # Create main chain
    for i in range(num_nodes - 1):
        w = random.randint(1, 10) if weighted else 1
        G.add_edge(i, i+1, weight=w, label=str(w))
        
    # Add sparse noise (5% chance)
    for u in range(num_nodes):
        for v in range(num_nodes):
            if u != v and not G.has_edge(u, v):
                if random.random() < 0.05:
                    w = random.randint(1, 10) if weighted else 1
                    G.add_edge(u, v, weight=w, label=str(w))
                    
    return G
