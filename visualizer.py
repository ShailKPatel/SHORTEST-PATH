from pyvis.network import Network
import networkx as nx

def get_node_color(node, state, path_nodes=None):
    """
    Determines the color of a node based on the current state.
    Priority:
    1. Processing (Blue)
    2. Path (Green) - Final path
    3. In Queue (Yellow)
    4. Visited (Red)
    5. Default (Grey)
    """
    if node in state.get('processing', set()):
        return '#4B4BFF' # Blue
    
    if path_nodes and node in path_nodes:
        return '#00CC00' # Green
        
    if node in state.get('q_nodes', []):
        return '#FFD700' # Yellow
        
    if node in state.get('visited', set()):
        return '#FF4B4B' # Red
        
    return '#E0E0E0' # Grey

def render_graph_html(G: nx.DiGraph, state: dict, path_nodes: set = None, height="500px", width="100%"):
    """
    Converts graph and state to a PyVis HTML string.
    """
    # Create PyVis Network
    # Create PyVis Network
    nt = Network(height=height, width=width, directed=True, notebook=False)
    
    # Grid Layout Check
    has_pos = any('pos' in G.nodes[n] for n in G.nodes())
    
    if not has_pos:
        nt.force_atlas_2based() # Default layout for non-grid graphs
    
    for node in G.nodes():
        color = get_node_color(node, state, path_nodes)
        
        # Label with distance if available
        dist = state.get('distances', {}).get(node, float('inf'))
        dist_str = "∞" if dist == float('inf') else str(dist)
        label = f"{node}\n(d={dist_str})"
        
        # Physics setup
        x, y = None, None
        if has_pos and 'pos' in G.nodes[node]:
             # Scale positions for PyVis
             r, c = G.nodes[node]['pos']
             x = c * 100 
             y = r * 100
             
        nt.add_node(node, label=label, shape='circle', title=f"Node {node}", color=color, x=x, y=y, physics=not has_pos)

    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 1)
        
        # Edge Color
        # if u, v in path -> Green
        edge_color = '#888888'
        width_val = 1
        if path_nodes and u in path_nodes and v in path_nodes:
             # Check if this edge is actually part of the path logic
             # This is a heuristic: if both nodes are in path, frame it green? 
             # No, could be a cross edge. 
             # Better check parents: v in path, and parent[v] == u
             parents = state.get('parents', {})
             if parents.get(v) == u:
                 edge_color = '#00CC00'
                 width_val = 3
        
        nt.add_edge(u, v, label=str(weight), color=edge_color, width=width_val)
    
    # Options
    physics_enabled = "false" if has_pos else "true"
    
    nt.set_options(f"""
    var options = {{
      "physics": {{
        "enabled": {physics_enabled},
        "hierarchicalRepulsion": {{
          "centralGravity": 0,
          "springLength": 100,
          "springConstant": 0.01,
          "nodeDistance": 120,
          "damping": 0.09
        }},
        "solver": "forceAtlas2Based"
      }}
    }}
    """)
        
    return nt.generate_html()
