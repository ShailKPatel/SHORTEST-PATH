import networkx as nx
from .erdos_renyi import generate_erdos_renyi

def generate_equal_weight_graph(num_nodes: int, probability: float, seed: int = None) -> nx.DiGraph:
    """
    Generates a graph where all edge weights are 1.
    Useful for comparing Dijkstra vs BFS.
    """
    return generate_erdos_renyi(num_nodes, probability, weighted=False, seed=seed)
