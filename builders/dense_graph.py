import networkx as nx
from .erdos_renyi import generate_erdos_renyi

def generate_dense_graph(num_nodes: int, weighted: bool = True, seed: int = None) -> nx.DiGraph:
    """
    Generates a dense graph (high probability of edges).
    Fixed probability of 0.8
    """
    return generate_erdos_renyi(num_nodes, probability=0.8, weighted=weighted, seed=seed)
