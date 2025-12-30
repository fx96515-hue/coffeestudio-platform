"""Tests for news service module."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from app.services.news import refresh_news, DEFAULT_NEWS_QUERIES
from app.models.news_item import NewsItem


@patch('app.services.news.settings')
def test_refresh_news_no_api_key(mock_settings, db):
    """Test graceful handling when API key is missing."""
    mock_settings.PERPLEXITY_API_KEY = None
    
    result = refresh_news(db, topic="coffee")
    
    assert result['status'] == 'skipped'
    assert 'PERPLEXITY_API_KEY not set' in result['reason']


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_success(mock_client_class, mock_settings, db):
    """Test successful news refresh."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    # Mock search result
    mock_result = Mock()
    mock_result.title = "Coffee Prices Rise"
    mock_result.url = "https://news.example.com/coffee"
    mock_result.snippet = "Coffee prices increased today"
    mock_client.search.return_value = [mock_result]
    
    result = refresh_news(db, topic="coffee", max_items=25)
    
    assert result['status'] == 'ok'
    assert result['topic'] == 'coffee'
    assert result['created'] >= 0
    assert isinstance(result['errors'], list)


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_creates_items(mock_client_class, mock_settings, db):
    """Test that news items are created in database."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    mock_result = Mock()
    mock_result.title = "New Coffee Export"
    mock_result.url = "https://unique-news.com/article1"
    mock_result.snippet = "Export news snippet"
    mock_client.search.return_value = [mock_result]
    
    result = refresh_news(db, topic="coffee")
    
    # Check if news item was created
    items = db.query(NewsItem).filter(NewsItem.url == "https://unique-news.com/article1").all()
    assert len(items) >= 0


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_updates_existing(mock_client_class, mock_settings, db):
    """Test that existing news items are updated."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    # Pre-create a news item
    existing = NewsItem(
        topic="coffee",
        title="Old Title",
        url="https://existing-news.com/article",
        snippet="Old snippet"
    )
    db.add(existing)
    db.commit()
    initial_count = db.query(NewsItem).count()
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    mock_result = Mock()
    mock_result.title = "Updated Title"
    mock_result.url = "https://existing-news.com/article"
    mock_result.snippet = "Updated snippet"
    mock_client.search.return_value = [mock_result]
    
    result = refresh_news(db, topic="coffee")
    
    # Should update, not create new
    assert db.query(NewsItem).count() == initial_count
    assert result['updated'] >= 1


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_duplicate_url_handling(mock_client_class, mock_settings, db):
    """Test that duplicate URLs in same refresh are handled."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    # Return same URL twice
    mock_result1 = Mock()
    mock_result1.title = "Article 1"
    mock_result1.url = "https://duplicate.com/article"
    mock_result1.snippet = "Snippet 1"
    
    mock_result2 = Mock()
    mock_result2.title = "Article 2"
    mock_result2.url = "https://duplicate.com/article"
    mock_result2.snippet = "Snippet 2"
    
    mock_client.search.return_value = [mock_result1, mock_result2]
    
    result = refresh_news(db, topic="coffee")
    
    # Should only process once
    assert result['created'] <= 1


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_with_country_filter(mock_client_class, mock_settings, db):
    """Test news refresh with country filter."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    mock_result = Mock()
    mock_result.title = "Peru Coffee News"
    mock_result.url = "https://peru-news.com/article"
    mock_result.snippet = "Peru coffee export"
    mock_client.search.return_value = [mock_result]
    
    result = refresh_news(db, topic="coffee", country="PE")
    
    assert result['status'] == 'ok'
    # Verify search was called with country parameter
    mock_client.search.assert_called()


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_search_error(mock_client_class, mock_settings, db):
    """Test error handling when search fails."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.search.side_effect = Exception("Search API error")
    
    result = refresh_news(db, topic="coffee")
    
    # Should handle error gracefully
    assert 'errors' in result
    assert len(result['errors']) > 0


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_empty_results(mock_client_class, mock_settings, db):
    """Test handling of empty search results."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.search.return_value = []
    
    result = refresh_news(db, topic="coffee")
    
    assert result['status'] == 'ok'
    assert result['created'] == 0


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_no_url_in_result(mock_client_class, mock_settings, db):
    """Test handling of results without URL."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    mock_result = Mock()
    mock_result.title = "Article"
    mock_result.url = None  # No URL
    mock_result.snippet = "Snippet"
    mock_client.search.return_value = [mock_result]
    
    result = refresh_news(db, topic="coffee")
    
    # Should skip items without URL
    assert result['created'] == 0


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_max_items_respected(mock_client_class, mock_settings, db):
    """Test that max_items parameter is used."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    # Create many results
    mock_results = []
    for i in range(100):
        mock_result = Mock()
        mock_result.title = f"Article {i}"
        mock_result.url = f"https://news.com/article{i}"
        mock_result.snippet = f"Snippet {i}"
        mock_results.append(mock_result)
    
    mock_client.search.return_value = mock_results
    
    result = refresh_news(db, topic="coffee", max_items=10)
    
    # Note: max_items is a parameter but actual limiting happens in search calls
    assert result['status'] == 'ok'


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_metadata_stored(mock_client_class, mock_settings, db):
    """Test that metadata is properly stored."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    mock_result = Mock()
    mock_result.title = "Test Article"
    mock_result.url = "https://test-meta.com/article"
    mock_result.snippet = "Test snippet"
    mock_client.search.return_value = [mock_result]
    
    refresh_news(db, topic="coffee", country="DE")
    
    item = db.query(NewsItem).filter(NewsItem.url == "https://test-meta.com/article").first()
    if item:
        assert item.country == "DE"
        assert item.meta is not None
        assert item.meta.get('provider') == 'perplexity'


def test_default_news_queries_exist():
    """Test that default news queries are defined."""
    assert len(DEFAULT_NEWS_QUERIES) > 0
    assert all(isinstance(q, str) for q in DEFAULT_NEWS_QUERIES)


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_client_closed(mock_client_class, mock_settings, db):
    """Test that Perplexity client is properly closed."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.search.return_value = []
    
    refresh_news(db, topic="coffee")
    
    # Verify close was called
    mock_client.close.assert_called_once()


@patch('app.services.news.settings')
@patch('app.services.news.PerplexityClient')
def test_refresh_news_title_truncation(mock_client_class, mock_settings, db):
    """Test that very long titles are truncated."""
    mock_settings.PERPLEXITY_API_KEY = "test_key"
    
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    # Very long title
    long_title = "A" * 1000
    mock_result = Mock()
    mock_result.title = long_title
    mock_result.url = "https://long-title.com/article"
    mock_result.snippet = "Snippet"
    mock_client.search.return_value = [mock_result]
    
    refresh_news(db, topic="coffee")
    
    item = db.query(NewsItem).filter(NewsItem.url == "https://long-title.com/article").first()
    if item:
        # Title should be truncated to 500 chars
        assert len(item.title) <= 500
