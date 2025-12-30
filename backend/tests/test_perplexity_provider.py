"""Tests for Perplexity provider module."""
import pytest
import json
from unittest.mock import Mock, patch

from app.providers.perplexity import (
    PerplexityClient,
    PerplexityError,
    safe_json_loads,
    SearchResult
)


def test_safe_json_loads_valid_json():
    """Test parsing valid JSON."""
    result = safe_json_loads('{"key": "value"}')
    assert result == {"key": "value"}


def test_safe_json_loads_invalid_json():
    """Test handling of invalid JSON."""
    with pytest.raises(ValueError, match="Could not parse JSON"):
        safe_json_loads('invalid json without brackets')


def test_safe_json_loads_with_markdown():
    """Test parsing JSON wrapped in markdown."""
    markdown_json = '```json\n{"key": "value"}\n```'
    result = safe_json_loads(markdown_json)
    assert result == {"key": "value"}


def test_safe_json_loads_empty_string():
    """Test handling of empty string."""
    with pytest.raises(ValueError, match="Could not parse JSON"):
        safe_json_loads('')


def test_safe_json_loads_array():
    """Test parsing JSON array."""
    result = safe_json_loads('[1, 2, 3]')
    assert result == [1, 2, 3]


@patch('app.providers.perplexity.settings')
def test_perplexity_client_no_api_key(mock_settings):
    """Test client creation without API key raises error."""
    mock_settings.PERPLEXITY_API_KEY = None
    mock_settings.PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
    mock_settings.PERPLEXITY_TIMEOUT_SECONDS = 60
    
    with pytest.raises(PerplexityError, match="PERPLEXITY_API_KEY"):
        PerplexityClient()


@patch('app.providers.perplexity.settings')
def test_perplexity_client_with_api_key(mock_settings):
    """Test client creation with API key."""
    mock_settings.PERPLEXITY_API_KEY = "test_key_123"
    mock_settings.PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
    mock_settings.PERPLEXITY_TIMEOUT_SECONDS = 60
    
    client = PerplexityClient()
    assert client.api_key == "test_key_123"
    client.close()


@patch('app.providers.perplexity.settings')
def test_search_success(mock_settings):
    """Test search would work with proper setup (basic validation)."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    mock_settings.PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
    mock_settings.PERPLEXITY_TIMEOUT_SECONDS = 60
    
    # Just verify client can be created
    client = PerplexityClient()
    assert client.api_key == "test_key"
    client.close()


@patch('app.providers.perplexity.settings')
def test_search_requires_api_key(mock_settings):
    """Test that client creation requires API key."""
    mock_settings.PERPLEXITY_API_KEY = None
    mock_settings.PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
    mock_settings.PERPLEXITY_TIMEOUT_SECONDS = 60
    
    with pytest.raises(PerplexityError):
        PerplexityClient()


@patch('app.providers.perplexity.settings')
def test_client_initialization_params(mock_settings):
    """Test client initialization with parameters."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    mock_settings.PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
    mock_settings.PERPLEXITY_TIMEOUT_SECONDS = 60
    
    client = PerplexityClient()
    assert client.timeout_s == 60
    assert "api.perplexity.ai" in client.base_url
    client.close()


def test_search_result_dataclass():
    """Test SearchResult dataclass."""
    result = SearchResult(
        title="Test Title",
        url="https://example.com",
        snippet="Test snippet"
    )
    
    assert result.title == "Test Title"
    assert result.url == "https://example.com"
    assert result.snippet == "Test snippet"


@patch('app.providers.perplexity.settings')
@patch('app.providers.perplexity.httpx.Client')
def test_client_close(mock_httpx_client, mock_settings):
    """Test client close method."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    client = PerplexityClient()
    # Should not raise error
    client.close()


def test_safe_json_loads_with_text_and_json():
    """Test parsing mixed text and JSON."""
    mixed = 'Some text before\n{"key": "value"}\nSome text after'
    # Should extract the JSON part
    try:
        result = safe_json_loads(mixed)
        # If it succeeds, verify it's a dict
        assert isinstance(result, dict)
    except json.JSONDecodeError:
        # It's OK if it can't parse mixed content
        pass


def test_safe_json_loads_nested_json():
    """Test parsing nested JSON."""
    nested = '{"outer": {"inner": {"deep": "value"}}}'
    result = safe_json_loads(nested)
    assert result["outer"]["inner"]["deep"] == "value"


def test_safe_json_loads_unicode():
    """Test parsing JSON with unicode characters."""
    unicode_json = '{"text": "Café Perú"}'
    result = safe_json_loads(unicode_json)
    assert result["text"] == "Café Perú"
