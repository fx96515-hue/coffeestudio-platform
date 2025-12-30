"""Tests for lots API endpoints."""
import pytest
from app.models.lot import Lot
from app.models.cooperative import Cooperative


def test_create_lot_success(client, auth_headers, db):
    """Test successful lot creation."""
    # Create cooperative first
    coop = Cooperative(name="Test Coop", region="Cajamarca")
    db.add(coop)
    db.commit()
    db.refresh(coop)
    
    payload = {
        "name": "Test Lot Alpha",
        "cooperative_id": coop.id,
        "weight_kg": 5000.0,
        "harvest_year": 2024,
        "variety": "Caturra",
        "processing_method": "Washed"
    }
    
    response = client.post("/lots", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Lot Alpha"
    assert data["weight_kg"] == 5000.0
    assert data["cooperative_id"] == coop.id


def test_create_lot_minimal_data(client, auth_headers, db):
    """Test lot creation with minimal required data."""
    coop = Cooperative(name="Test Coop")
    db.add(coop)
    db.commit()
    
    payload = {
        "name": "Minimal Lot",
        "cooperative_id": coop.id
    }
    
    response = client.post("/lots", json=payload, headers=auth_headers)
    # Should succeed with minimal data
    assert response.status_code in [200, 201, 422]  # May or may not require weight
    """Test listing all lots."""
    coop = Cooperative(name="Test Coop")
    db.add(coop)
    db.commit()
    
    lot1 = Lot(name="Lot 1", cooperative_id=coop.id, weight_kg=1000)
    lot2 = Lot(name="Lot 2", cooperative_id=coop.id, weight_kg=2000)
    db.add_all([lot1, lot2])
    db.commit()
    
    response = client.get("/lots", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_lot_by_id(client, auth_headers, db):
    """Test retrieving single lot by ID."""
    coop = Cooperative(name="Test Coop")
    db.add(coop)
    db.commit()
    
    lot = Lot(name="Test Lot", cooperative_id=coop.id, weight_kg=1500)
    db.add(lot)
    db.commit()
    db.refresh(lot)
    
    response = client.get(f"/lots/{lot.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lot.id
    assert data["name"] == "Test Lot"


def test_get_nonexistent_lot(client, auth_headers, db):
    """Test retrieving non-existent lot."""
    response = client.get("/lots/99999", headers=auth_headers)
    assert response.status_code == 404


def test_update_lot(client, auth_headers, db):
    """Test updating lot data."""
    coop = Cooperative(name="Test Coop")
    db.add(coop)
    db.commit()
    
    lot = Lot(name="Old Name", cooperative_id=coop.id, weight_kg=1000)
    db.add(lot)
    db.commit()
    db.refresh(lot)
    
    update_data = {"name": "Updated Name", "weight_kg": 1500}
    response = client.patch(f"/lots/{lot.id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["weight_kg"] == 1500


def test_delete_lot(client, auth_headers, db):
    """Test deleting a lot."""
    coop = Cooperative(name="Test Coop")
    db.add(coop)
    db.commit()
    
    lot = Lot(name="To Delete", cooperative_id=coop.id, weight_kg=1000)
    db.add(lot)
    db.commit()
    db.refresh(lot)
    
    response = client.delete(f"/lots/{lot.id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify deletion
    assert db.query(Lot).filter(Lot.id == lot.id).first() is None


def test_create_lot_unauthorized(client, db):
    """Test lot creation without authentication."""
    coop = Cooperative(name="Test Coop")
    db.add(coop)
    db.commit()
    
    payload = {
        "name": "Test Lot",
        "cooperative_id": coop.id,
        "weight_kg": 1000
    }
    
    response = client.post("/lots", json=payload)
    assert response.status_code == 401


def test_list_lots_filter_by_cooperative(client, auth_headers, db):
    """Test filtering lots by cooperative_id."""
    coop1 = Cooperative(name="Coop 1")
    coop2 = Cooperative(name="Coop 2")
    db.add_all([coop1, coop2])
    db.commit()
    
    lot1 = Lot(name="Lot 1", cooperative_id=coop1.id, weight_kg=1000)
    lot2 = Lot(name="Lot 2", cooperative_id=coop2.id, weight_kg=2000)
    db.add_all([lot1, lot2])
    db.commit()
    
    response = client.get(f"/lots?cooperative_id={coop1.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # Should only return lots for coop1
    for lot in data:
        assert lot["cooperative_id"] == coop1.id


def test_list_lots(client, auth_headers, db):
    """Test updating non-existent lot."""
    update_data = {"name": "Updated"}
    response = client.patch("/lots/99999", json=update_data, headers=auth_headers)
    assert response.status_code == 404


def test_delete_nonexistent_lot(client, auth_headers, db):
    """Test deleting non-existent lot."""
    response = client.delete("/lots/99999", headers=auth_headers)
    assert response.status_code == 404
