"""Tests for outreach service module."""
import pytest
from unittest.mock import Mock, patch

from app.services.outreach import generate_outreach, _template
from app.models.cooperative import Cooperative
from app.models.roaster import Roaster
from app.models.entity_event import EntityEvent


def test_template_sourcing_pitch_de():
    """Test German sourcing pitch template."""
    entity = Mock()
    entity.name = "Test Cooperative"
    entity.website = "https://test-coop.com"
    entity.region = "Cajamarca"
    entity.contact_email = "contact@test.com"
    
    result = _template("de", purpose="sourcing_pitch", entity=entity, counterpart="Max")
    
    assert "Hallo Max" in result
    assert "Test Cooperative" in result
    assert "Peru" in result
    assert "CoffeeStudio" in result


def test_template_sourcing_pitch_en():
    """Test English sourcing pitch template."""
    entity = Mock()
    entity.name = "Test Cooperative"
    entity.website = "https://test-coop.com"
    entity.region = "Cajamarca"
    entity.contact_email = None
    
    result = _template("en", purpose="sourcing_pitch", entity=entity, counterpart="John")
    
    assert "Hi John" in result
    assert "Test Cooperative" in result
    assert "Peru" in result
    assert "CoffeeStudio" in result


def test_template_sourcing_pitch_es():
    """Test Spanish sourcing pitch template."""
    entity = Mock()
    entity.name = "Cooperativa Test"
    entity.website = None
    entity.region = "Cusco"
    entity.contact_email = None
    
    result = _template("es", purpose="sourcing_pitch", entity=entity, counterpart="Maria")
    
    assert "Hola Maria" in result
    assert "Cooperativa Test" in result
    assert "CoffeeStudio" in result


def test_template_sample_request_de():
    """Test German sample request template."""
    entity = Mock()
    entity.name = "Test Cooperative"
    entity.website = "https://test-coop.com"
    entity.region = "Junín"
    entity.contact_email = "info@test.com"
    
    result = _template("de", purpose="sample_request", entity=entity, counterpart=None)
    
    assert "Hallo Team" in result
    assert "Junín" in result or "Peru" in result
    assert "CoffeeStudio" in result


def test_template_sample_request_en():
    """Test English sample request template."""
    entity = Mock()
    entity.name = "Test Roastery"
    entity.website = "https://roastery.com"
    entity.region = "Berlin"
    entity.contact_email = None
    
    result = _template("en", purpose="sample_request", entity=entity, counterpart="Team")
    
    assert "Hi Team" in result
    assert "samples" in result.lower()
    assert "CoffeeStudio" in result


def test_template_sample_request_es():
    """Test Spanish sample request template."""
    entity = Mock()
    entity.name = "Cooperativa Ejemplo"
    entity.website = None
    entity.region = "Puno"
    entity.contact_email = None
    
    result = _template("es", purpose="sample_request", entity=entity, counterpart="Equipo")
    
    assert "Hola Equipo" in result
    assert "CoffeeStudio" in result


def test_generate_outreach_invalid_entity_type(db):
    """Test error with invalid entity type."""
    with pytest.raises(ValueError, match="entity_type must be cooperative|roaster"):
        generate_outreach(db, entity_type="invalid", entity_id=1)


def test_generate_outreach_entity_not_found(db):
    """Test error when entity doesn't exist."""
    with pytest.raises(ValueError, match="entity not found"):
        generate_outreach(db, entity_type="cooperative", entity_id=99999)


def test_generate_outreach_cooperative_success(db):
    """Test successful outreach generation for cooperative."""
    coop = Cooperative(
        name="Test Coop",
        region="Cajamarca",
        website="https://test.com"
    )
    db.add(coop)
    db.commit()
    db.refresh(coop)
    
    result = generate_outreach(
        db,
        entity_type="cooperative",
        entity_id=coop.id,
        language="en",
        purpose="sourcing_pitch"
    )
    
    assert result['status'] == 'ok'
    assert result['entity_type'] == 'cooperative'
    assert result['entity_id'] == coop.id
    assert result['language'] == 'en'
    assert result['purpose'] == 'sourcing_pitch'
    assert 'text' in result
    assert "Test Coop" in result['text']


def test_generate_outreach_roaster_success(db):
    """Test successful outreach generation for roaster."""
    roaster = Roaster(
        name="Test Roastery",
        city="Berlin",
        website="https://roastery.com"
    )
    db.add(roaster)
    db.commit()
    db.refresh(roaster)
    
    result = generate_outreach(
        db,
        entity_type="roaster",
        entity_id=roaster.id,
        language="de",
        purpose="sample_request"
    )
    
    assert result['status'] == 'ok'
    assert result['entity_type'] == 'roaster'
    assert 'text' in result


def test_generate_outreach_creates_event(db):
    """Test that outreach generation creates an event."""
    coop = Cooperative(name="Event Test Coop")
    db.add(coop)
    db.commit()
    db.refresh(coop)
    
    initial_count = db.query(EntityEvent).count()
    
    generate_outreach(
        db,
        entity_type="cooperative",
        entity_id=coop.id
    )
    
    # Should create one event
    assert db.query(EntityEvent).count() == initial_count + 1
    
    event = db.query(EntityEvent).filter(
        EntityEvent.entity_type == "cooperative",
        EntityEvent.entity_id == coop.id,
        EntityEvent.event_type == "outreach_generated"
    ).first()
    
    assert event is not None
    assert event.payload['language'] == 'de'  # Default
    assert event.payload['purpose'] == 'sourcing_pitch'  # Default


def test_generate_outreach_with_counterpart_name(db):
    """Test outreach with custom counterpart name."""
    coop = Cooperative(name="Test Coop")
    db.add(coop)
    db.commit()
    db.refresh(coop)
    
    result = generate_outreach(
        db,
        entity_type="cooperative",
        entity_id=coop.id,
        language="en",
        counterpart_name="Alice"
    )
    
    assert "Alice" in result['text']


@patch('app.services.outreach.settings')
@patch('app.services.outreach.PerplexityClient')
def test_generate_outreach_with_llm_refinement(mock_client_class, mock_settings, db):
    """Test outreach refinement with LLM."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.chat_completions.return_value = "Refined outreach text with LLM"
    
    coop = Cooperative(name="LLM Test Coop")
    db.add(coop)
    db.commit()
    db.refresh(coop)
    
    result = generate_outreach(
        db,
        entity_type="cooperative",
        entity_id=coop.id,
        refine_with_llm=True
    )
    
    assert result['used_llm'] is True
    assert result['text'] == "Refined outreach text with LLM"
    mock_client.close.assert_called_once()


@patch('app.services.outreach.settings')
def test_generate_outreach_llm_without_api_key(mock_settings, db):
    """Test that LLM refinement is skipped without API key."""
    mock_settings.PERPLEXITY_API_KEY = None
    
    coop = Cooperative(name="No API Key Coop")
    db.add(coop)
    db.commit()
    db.refresh(coop)
    
    result = generate_outreach(
        db,
        entity_type="cooperative",
        entity_id=coop.id,
        refine_with_llm=True  # Request LLM but no key
    )
    
    assert result['used_llm'] is False


@patch('app.services.outreach.settings')
@patch('app.services.outreach.PerplexityClient')
def test_generate_outreach_llm_error_handled(mock_client_class, mock_settings, db):
    """Test that LLM errors propagate but client is closed."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.chat_completions.side_effect = Exception("LLM Error")
    
    coop = Cooperative(name="LLM Error Coop")
    db.add(coop)
    db.commit()
    db.refresh(coop)
    
    # Should raise error but close client properly
    with pytest.raises(Exception, match="LLM Error"):
        generate_outreach(
            db,
            entity_type="cooperative",
            entity_id=coop.id,
            refine_with_llm=True
        )
    
    # Client should still be closed even on error
    mock_client.close.assert_called_once()


def test_generate_outreach_default_language(db):
    """Test that language defaults to German."""
    coop = Cooperative(name="Default Lang Coop")
    db.add(coop)
    db.commit()
    db.refresh(coop)
    
    result = generate_outreach(
        db,
        entity_type="cooperative",
        entity_id=coop.id
    )
    
    assert result['language'] == 'de'


def test_generate_outreach_default_purpose(db):
    """Test that purpose defaults to sourcing_pitch."""
    coop = Cooperative(name="Default Purpose Coop")
    db.add(coop)
    db.commit()
    db.refresh(coop)
    
    result = generate_outreach(
        db,
        entity_type="cooperative",
        entity_id=coop.id
    )
    
    assert result['purpose'] == 'sourcing_pitch'


def test_template_entity_without_website():
    """Test template with entity missing website."""
    entity = Mock()
    entity.name = "No Website Coop"
    entity.website = None
    entity.region = "Cajamarca"
    entity.contact_email = None
    
    result = _template("en", purpose="sourcing_pitch", entity=entity, counterpart="Bob")
    
    assert "No Website Coop" in result
    # Should not include website placeholder
    assert "(https://" not in result or "(" not in result


def test_template_entity_without_region():
    """Test template with entity missing region."""
    entity = Mock()
    entity.name = "No Region Coop"
    entity.website = "https://test.com"
    entity.region = None
    entity.contact_email = None
    
    result = _template("de", purpose="sample_request", entity=entity, counterpart=None)
    
    assert "No Region Coop" in result or "Peru" in result
