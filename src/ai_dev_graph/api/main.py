from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import time
from datetime import datetime
import logging

from ai_dev_graph.domain.models import NodeData, NodeType
from ai_dev_graph.application.manager import GraphManager

logger = logging.getLogger(__name__)

# Determine the absolute path for the 'graphs' directory
STORAGE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "graphs")
)

app = FastAPI(
    title="AI Dev Graph API",
    description="Interfaz de consulta y administración de conocimiento para agentes IA",
    version="0.3.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize graph manager
graph_manager = GraphManager(storage_dir=STORAGE_DIR)


def get_kg():
    """Get the knowledge graph."""
    if graph_manager.current_graph is None:
        graph_manager.load_or_create()
    return graph_manager.current_graph


# --- Logging System ---
class LogEntry(BaseModel):
    timestamp: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    ip: str


# In-memory log storage (Last 1000 actions)
action_logs: List[LogEntry] = []


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    path = request.url.path
    if request.url.query:
        path += f"?{request.url.query}"

    log = LogEntry(
        timestamp=datetime.now().isoformat(),
        method=request.method,
        path=path,
        status_code=response.status_code,
        duration_ms=round(process_time, 2),
        ip=request.client.host if request.client else "unknown",
    )

    action_logs.insert(0, log)
    if len(action_logs) > 1000:
        action_logs.pop()

    return response


# Request/Response Models
class NodeRequest(BaseModel):
    id: str
    type: NodeType
    content: str
    metadata: Dict[str, Any] = {}
    parents: List[str] = []


class NodeUpdateRequest(BaseModel):
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NodeResponse(BaseModel):
    id: str
    data: Dict[str, Any]
    parents: List[str]
    children: List[str]


# API Endpoints


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.3.0"}


@app.get("/logs", response_model=List[LogEntry])
async def get_logs(limit: int = 100):
    return action_logs[:limit]


@app.get("/graph")
async def get_full_graph():
    """Devuelve la estructura completa del grafo en formato compatible con D3.js."""
    kg = get_kg()

    # Get all nodes and edges from the repository
    nodes_data = kg.repo.get_all_nodes()
    edges_data = kg.repo.get_all_edges()

    # Convert to D3.js compatible format
    nodes = []
    for node in nodes_data:
        nodes.append(
            {
                "id": node.id,
                "type": node.type.value,
                "content": node.content,
                "metadata": node.metadata,
            }
        )

    links = []
    for source, target in edges_data:
        links.append({"source": source, "target": target})

    return {
        "directed": True,
        "multigraph": False,
        "graph": {},
        "nodes": nodes,
        "links": links,
    }


@app.get("/graph/stats")
async def get_graph_stats():
    kg = get_kg()
    return kg.get_graph_stats()


@app.get("/graph/advanced-stats")
async def get_advanced_stats():
    return graph_manager.get_statistics()


@app.get("/nodes")
async def list_nodes(
    type: Optional[str] = Query(None, description="Filtrar por tipo de nodo"),
    content_match: Optional[str] = Query(None, description="Buscar en contenido"),
):
    kg = get_kg()
    filters = {}
    if type:
        filters["type"] = type
    if content_match:
        filters["content_match"] = content_match

    node_ids = kg.find_nodes(**filters)
    nodes = []
    for node_id in node_ids:
        node = kg.get_node_data(node_id)
        if node:
            nodes.append({"id": node_id, "data": node.model_dump()})
    return nodes


@app.get("/nodes/{node_id}")
async def get_node(node_id: str, depth: int = Query(1, ge=1, le=3)):
    kg = get_kg()
    node = kg.get_node_data(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Nodo '{node_id}' no encontrado")

    context = kg.get_context(node_id, depth)

    return {"id": node_id, "data": node.model_dump(), "context": context}


@app.post("/nodes")
async def create_node(node_req: NodeRequest):
    kg = get_kg()

    if kg.has_node(node_req.id):
        raise HTTPException(status_code=409, detail=f"Nodo '{node_req.id}' ya existe")

    node = NodeData(
        id=node_req.id,
        type=node_req.type,
        content=node_req.content,
        metadata=node_req.metadata,
    )
    kg.add_knowledge(node, parents=node_req.parents)
    logger.info(f"Nodo creado: {node_req.id}")
    graph_manager.save_with_backup()
    return {"id": node_req.id, "status": "created"}


@app.put("/nodes/{node_id}")
async def update_node(node_id: str, update: NodeUpdateRequest):
    kg = get_kg()

    if not kg.has_node(node_id):
        raise HTTPException(status_code=404, detail=f"Nodo '{node_id}' no encontrado")

    success = kg.update_node(node_id, content=update.content, metadata=update.metadata)

    if success:
        logger.info(f"Nodo actualizado: {node_id}")
        graph_manager.save_with_backup()
        return {"id": node_id, "status": "updated"}
    else:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el nodo")


@app.delete("/nodes/{node_id}")
async def delete_node(node_id: str):
    kg = get_kg()

    if not kg.has_node(node_id):
        raise HTTPException(status_code=404, detail=f"Nodo '{node_id}' no encontrado")

    success = kg.delete_node(node_id)

    if success:
        logger.info(f"Nodo eliminado: {node_id}")
        graph_manager.save_with_backup()
        return {"id": node_id, "status": "deleted"}
    else:
        raise HTTPException(status_code=400, detail="No se pudo eliminar el nodo")


@app.post("/graph/save")
async def save_graph():
    success = graph_manager.save_with_backup()
    if success:
        return {"status": "saved"}
    else:
        raise HTTPException(status_code=500, detail="Error al guardar grafo")


@app.post("/graph/load")
async def load_graph():
    try:
        graph_manager.load_or_create()
        return {"status": "loaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar: {str(e)}")


@app.post("/graph/reset")
async def reset_graph():
    from ai_dev_graph.init_meta_graph import init_project_graph

    graph_manager.current_graph = init_project_graph()
    logger.info("Grafo reiniciado")
    return {"status": "reset"}


# Servir la interfaz web
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/admin")
async def admin_interface():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Interfaz no disponible"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
