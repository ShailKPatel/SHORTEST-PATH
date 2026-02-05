import streamlit as st
import pandas as pd
import sys
import os

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

st.set_page_config(layout="wide", page_title="Algorithm Comparison")

st.title("Algorithm Comparison Lab")

if 'graph' not in st.session_state or st.session_state['graph'] is None:
    st.warning("No graph loaded. Please go to the Simulator page to generate a graph first.")
    st.stop()
    
G = st.session_state['graph']

ALGO_MAP = {
    "Dijkstra": run_dijkstra,
    "Bellman-Ford": run_bellman_ford,
    "BFS (Unweighted)": run_bfs_equal,
    "DAG Shortest Path": run_dag_shortest,
    "A* (A-Star)": run_a_star,
    "SPFA": run_spfa
}

c1, c2, c3 = st.columns([2,1,1])

with c1:
    selected_algos = st.multiselect("Select Algorithms", list(ALGO_MAP.keys()), default=["Dijkstra", "Bellman-Ford"])
    # Defaults
    if not selected_algos:
        # Just to prevent empty list errors if user clears it
        selected_algos = ["Dijkstra"]

with c2:
    node_options = list(G.nodes())
    start_node = st.selectbox("Source", node_options, index=0)

with c3:
    node_options = list(G.nodes())
    end_node = st.selectbox("Destination", node_options, index=min(len(node_options)-1, 10))

if st.button("Compare"):
    results = []
    
    G_run = G
    
    st.divider()
    
    cols = st.columns(len(selected_algos))
    
    for i, algo_name in enumerate(selected_algos):
        func = ALGO_MAP[algo_name]
        
        # Run Algorithm
        gen = func(G_run, start_node, end_node)
        
        # Exhaust generator to get final state
        final_state = None
        final_metrics = None
        for s, m, l in gen:
            final_state = s
            final_metrics = m
            
        # Collect results
        res = final_metrics.to_dict()
        res['Algorithm'] = algo_name
        results.append(res)
        
        # Visualize Final State
        with cols[i]:
            st.subheader(algo_name)
            
            # Reconstruct path for highlighting
            path_nodes = set()
            if final_metrics.path_found:
                parents = final_state.get('parents', {})
                curr = end_node
                while curr is not None:
                    path_nodes.add(curr)
                    curr = parents.get(curr)
                    if curr == start_node:
                        path_nodes.add(start_node)
                        break
            
            # Render small
            html = render_graph_html(G_run, final_state, path_nodes=path_nodes, height="300px")
            st.components.v1.html(html, height=320)
            
            # Mini stats
            st.caption(f"Cost: {res['Final Cost']}")
            st.caption(f"Time: {res['Time (s)']}s")

    st.divider()
    st.subheader("Comparison Table")
    df = pd.DataFrame(results)
    # Reorder columns
    cols_order = ['Algorithm', 'Final Cost', 'Time (s)', 'Relaxations', 'Comparisons', 'Path Found']
    st.dataframe(df[cols_order], use_container_width=True, hide_index=True)


