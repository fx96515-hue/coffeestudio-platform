"""Tests for knowledge base service module."""
import pytest
from app.services.kb import seed_default_kb, DEFAULT_DOCS
from app.models.knowledge_doc import KnowledgeDoc


def test_default_docs_exist():
    """Test that default documents are defined."""
    assert len(DEFAULT_DOCS) > 0
    for doc in DEFAULT_DOCS:
        assert 'category' in doc
        assert 'key' in doc
        assert 'title' in doc
        assert 'content_md' in doc


def test_seed_default_kb_creates_docs(db):
    """Test that seed creates knowledge base documents."""
    result = seed_default_kb(db)
    
    assert result['status'] == 'ok'
    assert result['created'] >= 0
    assert result['updated'] >= 0
    
    # Check that documents were created
    docs = db.query(KnowledgeDoc).all()
    assert len(docs) >= len(DEFAULT_DOCS)


def test_seed_default_kb_idempotent(db):
    """Test that seeding is idempotent."""
    # First seed
    result1 = seed_default_kb(db)
    initial_created = result1['created']
    
    # Second seed
    result2 = seed_default_kb(db)
    
    # Should not create duplicates
    assert result2['created'] == 0
    total_docs = db.query(KnowledgeDoc).count()
    assert total_docs == initial_created


def test_seed_default_kb_updates_changed_content(db):
    """Test that changed content gets updated."""
    # First seed
    seed_default_kb(db)
    
    # Modify a document
    doc = db.query(KnowledgeDoc).first()
    if doc:
        original_title = doc.title
        doc.title = "Modified Title"
        doc.content_md = "Modified content"
        db.commit()
        
        # Re-seed
        result = seed_default_kb(db)
        
        # Should update the modified document
        db.refresh(doc)
        assert result['updated'] >= 1 or doc.title != "Modified Title"


def test_default_docs_structure():
    """Test that default docs have required structure."""
    for doc in DEFAULT_DOCS:
        assert isinstance(doc['category'], str)
        assert isinstance(doc['key'], str)
        assert isinstance(doc['title'], str)
        assert isinstance(doc['content_md'], str)
        assert len(doc['category']) > 0
        assert len(doc['key']) > 0


def test_seed_default_kb_language_handling(db):
    """Test that language field is properly handled."""
    result = seed_default_kb(db)
    
    docs = db.query(KnowledgeDoc).all()
    for doc in docs:
        assert doc.language is not None
        assert isinstance(doc.language, str)
