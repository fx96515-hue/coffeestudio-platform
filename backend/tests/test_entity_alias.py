"""Tests for entity alias model."""

import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app.models.entity_alias import EntityAlias


def test_create_entity_alias(db):
    """Test creating an entity alias."""
    alias = EntityAlias(
        entity_type="cooperative",
        entity_id=1,
        alias="Test Coop Alternative Name",
        kind="name",
        observed_at=datetime.now(timezone.utc),
    )
    db.add(alias)
    db.commit()

    assert alias.id is not None
    assert alias.entity_type == "cooperative"
    assert alias.entity_id == 1
    assert alias.alias == "Test Coop Alternative Name"
    assert alias.kind == "name"
    assert alias.observed_at is not None


def test_entity_alias_unique_constraint(db):
    """Test that duplicate aliases are prevented."""
    alias1 = EntityAlias(
        entity_type="cooperative", entity_id=1, alias="Duplicate Name", kind="name"
    )
    db.add(alias1)
    db.commit()

    # Try to add duplicate
    alias2 = EntityAlias(
        entity_type="cooperative", entity_id=1, alias="Duplicate Name", kind="name"
    )
    db.add(alias2)

    with pytest.raises(IntegrityError):
        db.commit()


def test_entity_alias_different_types(db):
    """Test aliases for different entity types."""
    coop_alias = EntityAlias(
        entity_type="cooperative", entity_id=1, alias="Coop Name", kind="name"
    )
    roaster_alias = EntityAlias(
        entity_type="roaster", entity_id=1, alias="Roaster Name", kind="name"
    )

    db.add_all([coop_alias, roaster_alias])
    db.commit()

    assert coop_alias.id is not None
    assert roaster_alias.id is not None
    assert coop_alias.entity_type == "cooperative"
    assert roaster_alias.entity_type == "roaster"


def test_entity_alias_different_kinds(db):
    """Test different alias kinds."""
    alias_name = EntityAlias(
        entity_type="cooperative", entity_id=1, alias="Cooperative Name", kind="name"
    )
    alias_domain = EntityAlias(
        entity_type="cooperative", entity_id=1, alias="coop-domain.com", kind="domain"
    )
    alias_social = EntityAlias(
        entity_type="cooperative", entity_id=1, alias="@coophandle", kind="social"
    )

    db.add_all([alias_name, alias_domain, alias_social])
    db.commit()

    assert alias_name.kind == "name"
    assert alias_domain.kind == "domain"
    assert alias_social.kind == "social"


def test_entity_alias_optional_fields(db):
    """Test that optional fields can be None."""
    alias = EntityAlias(entity_type="cooperative", entity_id=1, alias="Simple Alias")
    db.add(alias)
    db.commit()

    assert alias.kind is None
    assert alias.observed_at is None


def test_entity_alias_timestamp_mixin(db):
    """Test that TimestampMixin fields work."""
    alias = EntityAlias(entity_type="cooperative", entity_id=1, alias="Test Alias")
    db.add(alias)
    db.commit()

    # TimestampMixin should add created_at and updated_at
    assert hasattr(alias, "created_at")
    assert hasattr(alias, "updated_at")


def test_query_aliases_by_entity(db):
    """Test querying aliases for a specific entity."""
    # Create multiple aliases for same entity
    for i in range(3):
        alias = EntityAlias(
            entity_type="cooperative", entity_id=1, alias=f"Alias {i}", kind="name"
        )
        db.add(alias)

    # Create alias for different entity
    other_alias = EntityAlias(
        entity_type="cooperative", entity_id=2, alias="Other Alias", kind="name"
    )
    db.add(other_alias)
    db.commit()

    # Query aliases for entity_id=1
    aliases = (
        db.query(EntityAlias)
        .filter(EntityAlias.entity_type == "cooperative", EntityAlias.entity_id == 1)
        .all()
    )

    assert len(aliases) == 3
    assert all(a.entity_id == 1 for a in aliases)
