from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import time
from datetime import datetime
import logging

from ai_dev_graph.core.graph import NodeData, NodeType
from ai_dev_graph.models.manager import GraphManager

logger = logging.getLogger(__name__)

# Determine the absolute path for the 'graphs' directory
STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "graphs"))

app = FastAPI(
    title="AI Dev Graph API",
    description="Interfaz de consulta y administración de conocimiento para agentes IA",
    version="0.1.0"
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
    
    # Construct full path with query string if present
    path = request.url.path
    if request.url.query:
        path += f"?{request.url.query}"
    
    log = LogEntry(
        timestamp=datetime.now().isoformat(),
        method=request.method,
        path=path,
        status_code=response.status_code,
        duration_ms=round(process_time, 2),
        ip=request.client.host if request.client else "unknown"
    )
    
    # Store log (prepend)
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
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}

@app.get("/logs", response_model=List[LogEntry])
async def get_logs(limit: int = 100):
    """Get recent API activity logs."""
    return action_logs[:limit]

@app.get("/graph")
async def get_full_graph():
    """Devuelve la estructura completa del grafo."""
    from networkx import node_link_data
    kg = get_kg()
    return node_link_data(kg.graph)

@app.get("/graph/stats")
async def get_graph_stats():
    """Obtener estadísticas del grafo."""
    kg = get_kg()
    return kg.get_graph_stats()

@app.get("/graph/advanced-stats")
async def get_advanced_stats():
    """Get comprehensive statistics with recommendations."""
    return graph_manager.get_statistics()

@app.get("/graph/export")
async def export_graph(agent_type: str = Query("default", description="Target agent type")):
    """Export graph optimized for agent consumption."""
    return graph_manager.export_for_agent(agent_type)

@app.get("/graph/validate")
async def validate_graph():
    """Validate graph integrity."""
    return graph_manager.validate_graph()

@app.get("/nodes")
async def list_nodes(
    type: Optional[str] = Query(None, description="Filtrar por tipo de nodo"),
    content_match: Optional[str] = Query(None, description="Buscar en contenido")
):
    """Listar todos los nodos con filtros opcionales."""
    kg = get_kg()
    filters = {}
    if type:
        filters["type"] = type
    if content_match:
        filters["content_match"] = content_match
    
    node_ids = kg.find_nodes(**filters)
    nodes = []
    for node_id in node_ids:
        if kg.graph.has_node(node_id):
            nodes.append({
                "id": node_id,
                "data": kg.graph.nodes[node_id].get("data", {})
            })
    return nodes

@app.get("/nodes/{node_id}")
async def get_node(node_id: str, depth: int = Query(1, ge=1, le=3)):
    """Obtener un nodo específico con su contexto."""
    kg = get_kg()
    if not kg.graph.has_node(node_id):
        raise HTTPException(status_code=404, detail=f"Nodo '{node_id}' no encontrado")
    
    context = kg.get_context(node_id, depth)
    node_data = kg.graph.nodes[node_id].get("data", {})
    
    return {
        "id": node_id,
        "data": node_data,
        "context": context
    }

@app.post("/nodes")
async def create_node(node_req: NodeRequest):
    """Crear un nuevo nodo."""
    kg = get_kg()
    
    if kg.graph.has_node(node_req.id):
        raise HTTPException(status_code=409, detail=f"Nodo '{node_req.id}' ya existe")
    
    node = NodeData(
        id=node_req.id,
        type=node_req.type,
        content=node_req.content,
        metadata=node_req.metadata
    )
    kg.add_knowledge(node, parents=node_req.parents)
    logger.info(f"Nodo creado: {node_req.id}")
    
    # Auto-save
    graph_manager.save_with_backup()
    
    return {"id": node_req.id, "status": "created"}

@app.put("/nodes/{node_id}")
async def update_node(node_id: str, update: NodeUpdateRequest):
    """Actualizar un nodo existente."""
    kg = get_kg()
    
    if not kg.graph.has_node(node_id):
        raise HTTPException(status_code=404, detail=f"Nodo '{node_id}' no encontrado")
    
    success = kg.update_node(node_id, content=update.content, metadata=update.metadata)
    
    if success:
        logger.info(f"Nodo actualizado: {node_id}")
        # Auto-save
        graph_manager.save_with_backup()
        return {"id": node_id, "status": "updated"}
    else:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el nodo")

@app.delete("/nodes/{node_id}")
async def delete_node(node_id: str):
    """Eliminar un nodo."""
    kg = get_kg()
    
    if not kg.graph.has_node(node_id):
        raise HTTPException(status_code=404, detail=f"Nodo '{node_id}' no encontrado")
    
    success = kg.delete_node(node_id)
    
    if success:
        logger.info(f"Nodo eliminado: {node_id}")
        # Auto-save
        graph_manager.save_with_backup()
        return {"id": node_id, "status": "deleted"}
    else:
        raise HTTPException(status_code=400, detail="No se pudo eliminar el nodo")

@app.post("/graph/save")
async def save_graph():
    """Guardar el grafo actual."""
    success = graph_manager.save_with_backup()
    if success:
        return {"status": "saved"}
    else:
        raise HTTPException(status_code=500, detail="Error al guardar grafo")

@app.post("/graph/load")
async def load_graph():
    """Recargar el grafo desde archivo."""
    try:
        graph_manager.load_or_create()
        return {"status": "loaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar: {str(e)}")

@app.post("/graph/reset")
async def reset_graph():
    """Reinicializar el grafo con valores por defecto."""
    from ai_dev_graph.init_meta_graph import init_project_graph
    graph_manager.current_graph = init_project_graph()
    logger.info("Grafo reiniciado")
    return {"status": "reset"}

# Servir la interfaz web
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

@app.get("/admin")
async def admin_interface():
    """Servir la interfaz de administración."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Interfaz no disponible. Accede a /docs para la documentación de API"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)