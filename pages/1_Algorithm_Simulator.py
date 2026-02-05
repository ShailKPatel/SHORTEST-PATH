import streamlit as st
import time
import networkx as nx
import sys
import os

# Add parent dir to path if needed (standard in Streamlit pages)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from builders import (
    generate_erdos_renyi, 
    generate_random_dag, 
    generate_negative_edge_dag_graph,
    generate_dense_graph,
    generate_sparse_chain,
    generate_equal_weight_graph,
    generate_grid_graph,
)

from algorithms import (
    run_dijkstra,
    run_bellman_ford,
    run_bfs_equal,
    run_dag_shortest,
    run_a_star,
    run_spfa
)

from visualizer import render_graph_html
from graph_utils import reverse_graph

st.set_page_config(layout="wide", page_title="Algorithm Simulator")

st.title("Algorithm Simulator Lab")

# --- Session State Initialization ---
if 'graph' not in st.session_state:
    st.session_state['graph'] = None
if 'steps' not in st.session_state:
    st.session_state['steps'] = []
if 'curr_step' not in st.session_state:
    st.session_state['curr_step'] = 0
if 'metrics' not in st.session_state:
    st.session_state['metrics'] = None
if 'generated_params' not in st.session_state:
    st.session_state['generated_params'] = {}

# --- Graph Generation Settings (Expander) ---
# Users configure the graph properties here BEFORE running any algorithm.
with st.expander("Graph Generator", expanded=True):

    BUILDER_MAP = {
        "Random Graph (Erdos–Renyi)": generate_erdos_renyi,
        "Random DAG": generate_random_dag,
        "Negative Edge DAG Graph": generate_negative_edge_dag_graph,
        "Dense Graph": generate_dense_graph,
        "Sparse Chain Graph": generate_sparse_chain,
        "Equal Weight Graph": generate_equal_weight_graph,
        "Grid Graph (A*)": generate_grid_graph,
    }

    DEFAULT_NODES = {
        "Random Graph (Erdos–Renyi)": 12,
        "Random DAG": 14,
        "Negative Edge DAG Graph": 8,
        "Dense Graph": 10,
        "Sparse Chain Graph": 18,
        "Equal Weight Graph": 14,
        "Grid Graph (A*)": 25,   # 5x5
    }
    
    col_type, col_nodes, col_seed = st.columns([3,1,1])
    
    with col_type:
        selected_builder_name = st.selectbox("Graph Type", list(BUILDER_MAP.keys()))
        
    with col_nodes:
        # Update default value based on selection
        default_val = DEFAULT_NODES[selected_builder_name]
        # We need a dynamic key to reset/update the widget when selection changes if we want it to auto-update
        # But Streamlit doesn't support changing default value of existing widget easily without key change.
        # Key change resets state. Let's try just setting value.
        num_nodes = st.number_input("Nodes", min_value=3, max_value=100, value=default_val)

    with col_seed:
        seed = st.number_input("Random Seed", 0, 999, 42)

    # Generator specific params
    prob = 0.2
    if "Erdos" in selected_builder_name or "DAG" in selected_builder_name or "Equal" in selected_builder_name:
        prob = st.slider("Edge Probability)", 0.05, 1.0, 0.2)
            
    rows, cols = 4, 4
    if "Grid" in selected_builder_name:
        rows = st.number_input("Rows", 2, 10, 4)
        cols = st.number_input("Cols", 2, 10, 4)
        num_nodes = rows * cols # Override
        
    if st.button("Generate Graph"):
        # Build the graph
        if "Grid" in selected_builder_name:
            G = generate_grid_graph(rows, cols, seed=seed)
        elif "Erdos" in selected_builder_name:
            G = generate_erdos_renyi(num_nodes, prob, seed=seed)
        elif "Random DAG" == selected_builder_name:
            G = generate_random_dag(num_nodes, prob, seed=seed)
        elif "Negative Edge DAG" in selected_builder_name:
            G = generate_negative_edge_dag_graph(num_nodes, prob, seed=seed)
        elif "Dense" in selected_builder_name:
            G = generate_dense_graph(num_nodes, seed=seed)
        elif "Sparse" in selected_builder_name:
            G = generate_sparse_chain(num_nodes, seed=seed)
        elif "Equal" in selected_builder_name:
            G = generate_equal_weight_graph(num_nodes, prob, seed=seed)
        else:
            G = generate_erdos_renyi(num_nodes, 0.2, seed=seed)
            
        st.session_state['graph'] = G
        st.session_state['steps'] = []
        st.session_state['curr_step'] = 0
        st.session_state['metrics'] = None
        st.session_state['generated_params'] = {'nodes': num_nodes}
        st.rerun()

# --- Simulation Controls ---

# Defaults
if st.session_state['graph'] is None:
    st.info("Please generate a graph to start.")
    st.stop()
    
G = st.session_state['graph']
num_nodes_actual = len(G.nodes)    


# --- Algorithm Execution Controls (Top Bar) ---
# Select algorithm, source, destination, and run.
c1, c2, c3, c4 = st.columns([2, 2, 2, 2])

with c1:
    ALGO_MAP = {
        "Dijkstra": run_dijkstra,
        "Bellman-Ford": run_bellman_ford,
        "BFS (Unweighted)": run_bfs_equal,
        "DAG Shortest Path": run_dag_shortest,
        "A* (A-Star)": run_a_star,
        "SPFA": run_spfa
    }
    selected_algo_name = st.selectbox("Algorithm", list(ALGO_MAP.keys()))   
with c2:
    node_options = list(G.nodes())
    start_node = st.selectbox("Source", node_options, index=0)
with c3:  
    node_options = list(G.nodes())
    end_node = st.selectbox("Dest", node_options, index=min(len(node_options)-1, 10))
with c4:
    # Run Algorithm Button
    st.caption("Run Algorithm")
    if st.button("Run Algorithm"):
        algo_func = ALGO_MAP[selected_algo_name]
        
        # Run Generator
        gen = algo_func(G, start_node, end_node)
        
        steps = []
        final_metrics = None
        for state, metrics, log in gen:
            steps.append((state, metrics, log))
            final_metrics = metrics
            
        st.session_state['steps'] = steps
        st.session_state['curr_step'] = 0
        st.session_state['metrics'] = final_metrics
        st.rerun()

# --- Main Visualization Area ---

st.markdown("---")

steps = st.session_state['steps']
curr_idx = st.session_state['curr_step']

# Helper to look ahead/behind for coloring path
path_nodes = set()
if steps and st.session_state['metrics'] and st.session_state['metrics'].path_found:
    # Reconstruct path from the FINAL step's parents
    final_step = steps[-1][0]
    parents = final_step.get('parents', {})
    
    # Trace back from end_node
    curr = end_node
    while curr is not None:
        path_nodes.add(curr)
        curr = parents.get(curr)
        if curr == start_node:
            path_nodes.add(start_node)
            break

    # Playback Slider & Buttons
if not steps:
    st.write("Graph generated. Ready to run algorithm.")
    # Render initial state (steps=0) equivalent
    html = render_graph_html(G, {}, path_nodes=None, height="500px")
    st.components.v1.html(html, height=520)
else:
    # Controls
    b1, b2, b3, b4, b5 = st.columns([0.1, 0.1, 0.6, 0.1, 0.1])
    if b1.button("Prev"):
        st.session_state['curr_step'] = max(0, curr_idx - 1)
        st.rerun()
    if b2.button("Next"):
        st.session_state['curr_step'] = min(len(steps) - 1, curr_idx + 1)
        st.rerun()
            
    # Slider
    # Slider
    if len(steps) > 1:
        st.session_state['curr_step'] = b3.slider("", 0, len(steps) - 1, st.session_state['curr_step'], label_visibility="collapsed")
    else:
        b3.write(f"Step 1/1")
        
    if b4.button("Reset"):
        st.session_state['curr_step'] = 0
        st.rerun()
    
    with b5:
        with b5.popover("Help"):
            st.badge("Processing", color="blue", icon=":material/clock_loader_40:")
            st.badge("Final path", color="green", icon=":material/check_circle:")
            st.badge("In Queue", color="orange", icon=":material/queue:")
            st.badge("Visited", color="red", icon=":material/visibility:")
            st.badge("Default", color="grey", icon=":material/circle:")

    # Current State
    current_state, current_metrics, current_log = steps[st.session_state['curr_step']]
        
    # Only show path if algorithm has finished AND we are at the last step (or path found)
    # Actually, showing partial path is cool if parents exist. 
    # But 'path_nodes' computed above is the FINAL path.
    # Should only highlight it if we reached the end?
    # User requested: "Green: Final shortest path" -> implies only at end.
    show_path = path_nodes if (st.session_state['curr_step'] == len(steps) - 1) else None
        
    html = render_graph_html(G, current_state, path_nodes=show_path, height="500px")
    st.components.v1.html(html, height=520)
        
    st.info(f"Step {st.session_state['curr_step'] + 1}/{len(steps)}: {current_log}")

if steps:
    state, metric_obj, _ = steps[st.session_state['curr_step']]

    c1, c2,  c3 = st.columns([1, 1, 1])
    with c1:
        st.header("Metrics")       
        # Current Distances Table
        dists = state.get('distances', {})
        # Filter for reachable/interesting nodes? or all?
        # Let's show all
        
        m_dict = metric_obj.to_dict()
        st.dataframe(m_dict, column_config={0: "Measures", 1: "Value"}, use_container_width=True)
    with c2:
        st.subheader("Distances")
        # Format as dataframe for better view?
        sorted_dists = sorted([(k, v) for k, v in dists.items()], key=lambda x: x[0])
        st.dataframe(sorted_dists, column_config={1: "Node", 2: "Cost"}, use_container_width=True, hide_index=True)    
    with c3:
        st.subheader("Parents")
        parents = state.get('parents', {})
        sorted_parents = sorted([(k, v) for k, v in parents.items() if v is not None], key=lambda x: x[0])
        st.dataframe(sorted_parents, column_config={1: "Node", 2: "Parent"}, use_container_width=True, hide_index=True)  
else:
    st.write("Run algorithm to see metrics.")
