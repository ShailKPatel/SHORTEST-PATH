import networkx as nx
import random

def generate_erdos_renyi(num_nodes: int, probability: float, weighted: bool = True, min_weight: int = 1, max_weight: int = 10, seed: int = None) -> nx.DiGraph:
    """
    Generates a generic Erdős-Rényi random graph.
    
    Args:
        num_nodes: Number of nodes.
        probability: Probability for edge creation.
        weighted: If True, assigns random weights to edges.
        min_weight: Minimum edge weight.
        max_weight: Maximum edge weight.
        seed: Random seed.
        
    Returns:
        A NetworkX DiGraph.
    """
    if seed is not None:
        random.seed(seed)
    
    # Generate the graph topology using NetworkX's generator
    # directed=True for our use case always
    G = nx.fast_gnp_random_graph(num_nodes, probability, seed=seed, directed=True)
    
    # Assign weights if needed
    if weighted:
        for u, v in G.edges():
            G.edges[u, v]['weight'] = random.randint(min_weight, max_weight)
            G.edges[u, v]['label'] = str(G.edges[u, v]['weight'])
    else:
        for u, v in G.edges():
            G.edges[u, v]['weight'] = 1
            G.edges[u, v]['label'] = "1"
            
    return G
