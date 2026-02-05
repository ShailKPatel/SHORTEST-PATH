from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GraphGenerateRequest(BaseModel):
    num_nodes: int = 20
    density: float = 0.2
    directed: bool = False
    weight_min: int = 1
    weight_max: int = 10
    allow_disconnected: bool = False

class AlgorithmRunRequest(BaseModel):
    algorithm: str
    start_node: int
    end_node: int
    graph: Dict[str, Any] # Full graph structure passed back (stateless API preference)
    # Alternatively, we could store graph in memory/ID, but passing it is stateless.
    # For large graphs, ID is better. For < 100 nodes, passing JSON is fine.
    
class BatchRunRequest(BaseModel):
    num_graphs: int = 30
    num_nodes: int = 30
    density: float = 0.3
    directed: bool = False
    algorithms: Optional[List[str]] = None
