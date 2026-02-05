import networkx as nx
import random
from .random_dag import generate_random_dag

def generate_negative_edge_dag_graph(num_nodes: int, probability: float, min_weight: int = -5, max_weight: int = 10, seed: int = None) -> nx.DiGraph:
    """
    Generates a graph with possible negative weights but NO negative cycles.
    Implementation: Uses a DAG structure to guarantee no cycles at all.
    """
    # Reuse DAG generator but allow negative weights
    return generate_random_dag(num_nodes, probability, weighted=True, min_weight=min_weight, max_weight=max_weight, seed=seed)
