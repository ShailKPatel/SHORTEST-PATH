from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class Metrics:
    relaxations: int = 0
    comparisons: int = 0  # Number of times we checked if dist[v] > dist[u] + w
    start_time: float = 0.0
    end_time: float = 0.0
    final_cost: float = float('inf')
    path_found: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "Relaxations": self.relaxations,
            "Comparisons": self.comparisons,
            "Time (s)": round(self.end_time - self.start_time, 5) if self.end_time > 0 else 0,
            "Final Cost": self.final_cost if self.final_cost != float('inf') else "∞",
            "Path Found": "✅" if self.path_found else "❌"
        }
