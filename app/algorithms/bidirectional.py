import heapq
import networkx as nx

def bidirectional_dijkstra_generator(G, start_node, end_node):
    # Forward search
    f_distances = {node: float('inf') for node in G.nodes()}
    f_distances[start_node] = 0
    f_parents = {node: None for node in G.nodes()}
    f_visited = set()
    f_frontier = {start_node}
    f_pq = [(0, start_node)]
    
    # Backward search
    # Note: For directed graphs, backward search usually runs on G.reverse()
    # But if input is undirected, G is same. We should handle this.
    if G.is_directed():
        R = G.reverse()
    else:
        R = G
        
    b_distances = {node: float('inf') for node in G.nodes()}
    b_distances[end_node] = 0
    b_parents = {node: None for node in G.nodes()}
    b_visited = set()
    b_frontier = {end_node}
    b_pq = [(0, end_node)]
    
    # We yield a merged state
    def get_state(current, direction):
        return {
            "visited": list(f_visited.union(b_visited)),
            "frontier": list(f_frontier.union(b_frontier)),
            "current_node": current,
            "distances": {n: min(f_distances[n], b_distances[n]) for n in G.nodes()}, # visual merge
            "parents": {**f_parents, **b_parents}, # This might clash but just for visual
            "description": f"{direction}: Processing {current}",
            "best_cost": mu if mu != float('inf') else float('inf')
        }

    mu = float('inf') # Best path found so far
    
    yield get_state(start_node, "Init")
    
    while f_pq and b_pq:
        # Check termination condition: 
        # If top(f_pq) + top(b_pq) >= mu, we are done
        if f_pq[0][0] + b_pq[0][0] >= mu:
            yield {
                 "visited": list(f_visited.union(b_visited)),
                 "frontier": [],
                 "current_node": start_node,
                 "distances": {n: min(f_distances[n], b_distances[n]) for n in G.nodes()},
                 "parents": {**f_parents, **b_parents},
                 "description": f"Optimal path found with cost {mu}",
                 "best_cost": mu
            }
            break

        # Forward Step
        if f_pq:
            dist_u, u = heapq.heappop(f_pq)
            if u not in f_visited:
                f_visited.add(u)
                if u in f_frontier: f_frontier.remove(u)
                
                # Check connection
                if u in b_visited:
                    mu = min(mu, f_distances[u] + b_distances[u])

                yield get_state(u, "Forward")

                for v in G.neighbors(u):
                    weight = G.edges[u, v].get('weight', 1)
                    if f_distances[u] + weight < f_distances[v]:
                        f_distances[v] = f_distances[u] + weight
                        f_parents[v] = u
                        heapq.heappush(f_pq, (f_distances[v], v))
                        f_frontier.add(v)
                        
                        # Update mu if connected
                        if v in b_visited:
                             mu = min(mu, f_distances[v] + b_distances[v])
                             
        # Backward Step
        if b_pq:
            dist_v, v = heapq.heappop(b_pq)
            if v not in b_visited:
                b_visited.add(v)
                if v in b_frontier: b_frontier.remove(v)
                
                 # Check connection
                if v in f_visited:
                    mu = min(mu, f_distances[v] + b_distances[v])

                yield get_state(v, "Backward")

                for w in R.neighbors(v):
                    weight = R.edges[v, w].get('weight', 1)
                    if b_distances[v] + weight < b_distances[w]:
                        b_distances[w] = b_distances[v] + weight
                        b_parents[w] = v
                        heapq.heappush(b_pq, (b_distances[w], w))
                        b_frontier.add(w)
                        
                        if w in f_visited:
                             mu = min(mu, f_distances[w] + b_distances[w])
