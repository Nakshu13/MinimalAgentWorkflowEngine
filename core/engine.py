import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.registry import tool_registry
from app.core.storage import save_run, get_graph, get_run
from app.core.models import Run, GraphRunResponse, Graph, generate_id
from app.core.ws_manager import ws_manager  # <-- WebSocket Manager

# Special key used for branching/looping
NEXT_NODE_KEY = "__next_node__"


async def _maybe_await(result):
    """Await coro if necessary, otherwise return value."""
    if asyncio.iscoroutine(result):
        return await result
    return result


async def run_graph(graph: Graph, initial_state: Dict[str, Any]) -> GraphRunResponse:
    """Execute the graph step-by-step with logging + WebSocket streaming."""

    # Initialize run
    run = Run(
        id=generate_id(),
        graph_id=graph.id,
        status="RUNNING",
        state=initial_state.copy(),
        logs=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        error=None,
    )
    save_run(run)

    current_node_id: Optional[str] = graph.start_node
    steps = 0

    try:
        while current_node_id is not None and steps < graph.max_steps:

            # Resolve node + tool function
            node = graph.nodes[current_node_id]
            tool_func = tool_registry.get(node.tool)

            # Execute node
            start_time = datetime.utcnow()
            result = await _maybe_await(tool_func(run.state))
            end_time = datetime.utcnow()

            # Merge returned state (if dict)
            if isinstance(result, dict):
                run.state.update(result)

            # Increase step counter
            steps += 1

            # Create log entry
            step_log = {
                "step": steps,
                "node_id": node.id,
                "tool": node.tool,
                "started_at": start_time.isoformat(),
                "finished_at": end_time.isoformat(),
                "state_snapshot": run.state.copy(),
                "message": f"Executed node '{node.id}'"
            }
            run.logs.append(step_log)

            # Save run
            run.updated_at = end_time
            save_run(run)

            #  WebSocket broadcast to all clients listening to /ws/logs
            await ws_manager.broadcast({
                "run_id": run.id,
                "step": steps,
                "node": node.id,
                "tool": node.tool,
                "state": run.state.copy()
            })

            # Handle branching/loop override
            next_override = run.state.pop(NEXT_NODE_KEY, None)
            if next_override:
                current_node_id = next_override
            else:
                current_node_id = node.next

        # Completed successfully
        run.status = "COMPLETED"

    except Exception as e:
        # Workflow crashed
        run.status = "FAILED"
        run.error = str(e)
        run.updated_at = datetime.utcnow()
        save_run(run)

    # Return final output
    return GraphRunResponse(
        run_id=run.id,
        final_state=run.state,
        logs=run.logs,
        status=run.status,
        error=run.error,
    )


def get_run_state(run_id: str) -> Run:
    """Return the latest state of a workflow execution."""
    return get_run(run_id)
