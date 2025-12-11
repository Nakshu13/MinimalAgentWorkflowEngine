from fastapi import FastAPI

from app.api.graph_routes import router as graph_router
from app.api.ws_routes import router as ws_router

import app.workflows.data_quality  # register tools
from app.core.registry import tool_registry

app = FastAPI(title="Minimal Workflow Engine - Data Quality Pipeline")


@app.on_event("startup")
async def startup_event():
    print("Registered tools:", tool_registry.list_tools())


@app.get("/")
def root():
    return {"message": "Workflow engine is running"}


app.include_router(graph_router)
app.include_router(ws_router)
