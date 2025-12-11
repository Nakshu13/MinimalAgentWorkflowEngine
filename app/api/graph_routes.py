from fastapi import APIRouter, HTTPException

from app.core.models import (
    GraphCreateRequest,
    GraphRunRequest,
    Graph,
    generate_id,
)
from app.core.storage import save_graph, get_graph
from app.core.engine import run_graph, get_run_state

router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/create")
async def create_graph(req: GraphCreateRequest):
    nodes_map = {n.id: n for n in req.nodes}
    graph = Graph(
        id=generate_id(),
        name=req.name,
        start_node=req.start_node,
        max_steps=req.max_steps,
        nodes=nodes_map,
    )
    save_graph(graph)
    return {"graph_id": graph.id}


@router.post("/run")
async def run_graph_endpoint(req: GraphRunRequest):
    try:
        graph = get_graph(req.graph_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Graph not found")

    result = await run_graph(graph, req.initial_state)
    return result


@router.get("/state/{run_id}")
async def get_state_endpoint(run_id: str):
    try:
        run = get_run_state(run_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "run_id": run.id,
        "status": run.status,
        "state": run.state,
        "logs": run.logs,
        "error": run.error,
    }
