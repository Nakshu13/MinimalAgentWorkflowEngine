from typing import Dict
from app.core.models import Graph, Run


GRAPHS: Dict[str, Graph] = {}
RUNS: Dict[str, Run] = {}


def save_graph(graph: Graph) -> None:
    GRAPHS[graph.id] = graph


def get_graph(graph_id: str) -> Graph:
    if graph_id not in GRAPHS:
        raise KeyError(f"Graph '{graph_id}' not found")
    return GRAPHS[graph_id]


def save_run(run: Run) -> None:
    RUNS[run.id] = run


def get_run(run_id: str) -> Run:
    if run_id not in RUNS:
        raise KeyError(f"Run '{run_id}' not found")
    return RUNS[run_id]
