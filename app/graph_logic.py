import networkx as nx
import random

class GraphGenerator:
    @staticmethod
    def generate_graph(num_nodes: int, density: float, directed: bool = False, weight_range: tuple = (1, 10), allow_disconnected: bool = False):
        """
        Generates a random graph with the specified parameters.
        """
        if directed:
            # G = nx.gnp_random_graph(num_nodes, density, directed=True) # gnp doesn't guarantee connectivity easily
             # Better control:
            G = nx.DiGraph()
            nodes = range(num_nodes)
            G.add_nodes_from(nodes)
            
            # Random edges based on density
            max_edges = num_nodes * (num_nodes - 1)
            num_edges = int(max_edges * density)
            
            # Using random_geometric_graph might be better for "visual" graphs, but for strict node-link:
            # Let's stick to random edges but ensure connectivity if requested.
            
            # To ensure connectivity for Directed graphs is hard (Strongly connected? Weakly?). 
            # Usually for Shortest Path, we just want a "path" explicitly or a connected underlying undirected graph.
            # Let's use a method that guarantees a spanning tree first to ensure connectedness.
            
        else:
            G = nx.Graph()
            nodes = range(num_nodes)
            G.add_nodes_from(nodes)
        
        # Ensure connectivity if required
        if not allow_disconnected:
             # Create a path 0->1->2...->N-1 to guarantee connectivity (weakly connected for directed)
            path = list(range(num_nodes))
            random.shuffle(path)
            for i in range(num_nodes - 1):
                u, v = path[i], path[i+1]
                weight = random.randint(*weight_range)
                G.add_edge(u, v, weight=weight)
                if directed:
                    # Maybe add back edge optionally? No, let's keep it minimal connected.
                    pass

        # Add remaining edges to satisfy density
        start_edges = G.number_of_edges()
        if directed:
            possible_edges = num_nodes * (num_nodes - 1)
        else:
            possible_edges = num_nodes * (num_nodes - 1) // 2
            
        target_edges = int(possible_edges * density)
        edges_to_add = target_edges - start_edges
        
        if edges_to_add > 0:
            while edges_to_add > 0:
                u = random.randint(0, num_nodes - 1)
                v = random.randint(0, num_nodes - 1)
                if u != v and not G.has_edge(u, v):
                    weight = random.randint(*weight_range)
                    G.add_edge(u, v, weight=weight)
                    edges_to_add -= 1
        
        # Assign random positions for visualization
        pos = nx.spring_layout(G, scale=100) # scale to 0-100 or screen coords
        # Store pos in node attributes
        for node, (x, y) in pos.items():
            G.nodes[node]['x'] = (x + 1) * 400 # Map -1..1 to 0..800 roughly (will normalize in frontend)
            G.nodes[node]['y'] = (y + 1) * 300
            
        return G

    @staticmethod
    def to_json(G):
        """Converts graph to JSON serializable format."""
        nodes = []
        for n, data in G.nodes(data=True):
            nodes.append({
                "id": n,
                "x": data.get('x', 0),
                "y": data.get('y', 0)
            })
            
        edges = []
        for u, v, data in G.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "weight": data.get('weight', 1)
            })
            
        return {"nodes": nodes, "edges": edges, "directed": G.is_directed()}
