from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.schemas.knowledge_graph import (
    Community,
    EntityAnalysis,
    HiddenConnection,
    NetworkData,
    PathResult,
)
from app.services import knowledge_graph

router = APIRouter()


@router.get("/network", response_model=NetworkData)
def get_network(
    node_types: str = Query("all", description="Filter by node types: cooperative, roaster, region, certification"),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
) -> NetworkData:
    """Get the complete knowledge graph network data for visualization."""
    return knowledge_graph.get_network_data(db, node_types=node_types)


@router.get("/analysis/{entity_type}/{entity_id}", response_model=EntityAnalysis)
def get_entity_analysis(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
) -> EntityAnalysis:
    """Get graph analysis for a specific entity."""
    try:
        return knowledge_graph.get_entity_analysis(db, entity_type, entity_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/communities", response_model=list[Community])
def get_communities(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst")),
) -> list[Community]:
    """Detect and return communities in the knowledge graph."""
    return knowledge_graph.get_communities(db)


@router.get("/path/{source_type}/{source_id}/{target_type}/{target_id}", response_model=PathResult)
def get_shortest_path(
    source_type: str,
    source_id: int,
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
) -> PathResult:
    """Find shortest path between two entities in the knowledge graph."""
    try:
        return knowledge_graph.get_shortest_path(
            db, source_type, source_id, target_type, target_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/hidden-connections/{entity_type}/{entity_id}", response_model=list[HiddenConnection])
def get_hidden_connections(
    entity_type: str,
    entity_id: int,
    max_hops: int = Query(3, ge=2, le=5, description="Maximum hops to search"),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analyst", "viewer")),
) -> list[HiddenConnection]:
    """Find hidden connections to entities 2-3 hops away."""
    try:
        return knowledge_graph.get_hidden_connections(db, entity_type, entity_id, max_hops)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
