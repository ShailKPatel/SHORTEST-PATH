from .dijkstra import dijkstra_generator
from .bellman_ford import bellman_ford_generator
from .a_star import a_star_generator
from .uniform_cost_search import uniform_cost_search_generator
from .floyd_warshall import floyd_warshall_generator

ALGORITHMS = {
    "Dijkstra": dijkstra_generator,
    "Bellman-Ford": bellman_ford_generator,
    "A*": a_star_generator,
    "Uniform Cost Search": uniform_cost_search_generator,
    "Floyd-Warshall": floyd_warshall_generator
}
