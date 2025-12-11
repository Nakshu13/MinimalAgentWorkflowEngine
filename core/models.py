from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


def generate_id() -> str:
    return uuid.uuid4().hex


class NodeConfig(BaseModel):
    id: str
    tool: str
    next: Optional[str] = None  # id of next node or null


class GraphCreateRequest(BaseModel):
    name: str
    start_node: str
    max_steps: int = 20
    nodes: List[NodeConfig]


class Graph(BaseModel):
    id: str
    name: str
    start_node: str
    max_steps: int
    nodes: Dict[str, NodeConfig]


class Run(BaseModel):
    id: str
    graph_id: str
    status: str
    state: Dict[str, Any] = Field(default_factory=dict)
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    logs: List[Dict[str, Any]]
    status: str
    error: Optional[str] = None
