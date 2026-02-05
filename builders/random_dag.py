import networkx as nx
import random

def generate_random_dag(num_nodes: int, probability: float, weighted: bool = True, min_weight: int = 1, max_weight: int = 10, seed: int = None) -> nx.DiGraph:
    """
    Generates a Random Directed Acyclic Graph (DAG).
    Enforces structure by allowing edges (u, v) only if u < v.
    """
    if seed is not None:
        random.seed(seed)
        
    G = nx.DiGraph()
    G.add_nodes_from(range(num_nodes))
    
    for u in range(num_nodes):
        for v in range(u + 1, num_nodes):
            if random.random() < probability:
                if weighted:
                    w = random.randint(min_weight, max_weight)
                    G.add_edge(u, v, weight=w, label=str(w))
                else:
                    G.add_edge(u, v, weight=1, label="1")
    
    return G
