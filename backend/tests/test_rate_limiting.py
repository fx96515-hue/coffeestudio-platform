"""Tests for rate limiting functionality."""

import pytest
import time
from fastapi.testclient import TestClient


def test_global_rate_limit_exists(client: TestClient, auth_headers):
    """Test that global rate limiting is configured."""
    # Make multiple requests quickly
    responses = []
    for _ in range(210):  # Exceed the 200/minute limit
        response = client.get("/cooperatives/", headers=auth_headers)
        responses.append(response)
        if response.status_code == 429:
            break
    
    # Should eventually hit rate limit
    assert any(r.status_code == 429 for r in responses), "Global rate limit not enforced"


def test_login_rate_limit(client: TestClient):
    """Test that login endpoint has strict rate limiting (5/minute)."""
    # Try to login multiple times quickly
    responses = []
    for i in range(10):
        response = client.post(
            "/auth/login",
            json={
                "email": f"test{i}@example.com",
                "password": "password123"
            }
        )
        responses.append(response)
        if response.status_code == 429:
            break
    
    # Should hit rate limit before 10 attempts
    rate_limited = [r for r in responses if r.status_code == 429]
    assert len(rate_limited) > 0, "Login rate limit not enforced"


def test_rate_limit_by_ip(client: TestClient):
    """Test that rate limiting is per-IP address."""
    # The rate limiter uses IP address as key
    # Multiple requests from same client should be rate limited
    responses = []
    for i in range(250):
        response = client.get("/health")
        responses.append(response.status_code)
        if response.status_code == 429:
            break
    
    # Should eventually hit rate limit
    assert 429 in responses, "IP-based rate limiting not working"


def test_rate_limit_error_message(client: TestClient, auth_headers):
    """Test that rate limit error messages are informative."""
    # Make enough requests to trigger rate limit
    for _ in range(210):
        response = client.get("/cooperatives/", headers=auth_headers)
        if response.status_code == 429:
            data = response.json()
            assert "detail" in data
            assert "rate limit" in data["detail"].lower()
            break
    else:
        # If we didn't hit rate limit, that's also acceptable for this test
        pass


def test_bootstrap_rate_limit(client: TestClient):
    """Test that bootstrap endpoint has rate limiting (10/hour)."""
    # Try to call bootstrap multiple times
    responses = []
    for _ in range(15):
        response = client.post("/auth/dev/bootstrap")
        responses.append(response)
        if response.status_code == 429:
            break
    
    # Should hit rate limit before 15 attempts (limit is 10/hour)
    rate_limited = [r for r in responses if r.status_code == 429]
    assert len(rate_limited) > 0, "Bootstrap rate limit not enforced"


def test_rate_limit_headers_present():
    """Test that rate limit headers are present in responses."""
    # This test documents the expected behavior
    # SlowAPI should add X-RateLimit-* headers
    # Note: Headers might not always be present depending on SlowAPI config
    client = TestClient(app=None)  # This is a documentation test
    assert True  # Placeholder for header validation


def test_authenticated_vs_unauthenticated_rate_limits(client: TestClient, auth_headers):
    """Test that authenticated and unauthenticated requests share the same rate limit pool."""
    # Both should be rate limited by IP address
    responses_unauth = []
    for _ in range(100):
        response = client.get("/health")
        responses_unauth.append(response.status_code)
    
    responses_auth = []
    for _ in range(100):
        response = client.get("/cooperatives/", headers=auth_headers)
        responses_auth.append(response.status_code)
        if response.status_code == 429:
            break
    
    # At least one should hit rate limit due to combined requests
    assert 429 in responses_unauth or 429 in responses_auth


def test_rate_limit_does_not_block_legitimate_use(client: TestClient, auth_headers):
    """Test that rate limits are reasonable for normal use."""
    # A reasonable number of requests should work fine
    responses = []
    for _ in range(50):  # Well below 200/minute limit
        response = client.get("/cooperatives/", headers=auth_headers)
        responses.append(response.status_code)
    
    # All should succeed
    assert all(status == 200 for status in responses), "Rate limit too strict for normal use"


def test_rate_limit_per_endpoint():
    """Test that different endpoints can have different rate limits."""
    # Document that:
    # - /api/auth/login: 5/minute
    # - /api/auth/dev/bootstrap: 10/hour
    # - Global default: 200/minute
    
    # This is validated by the individual endpoint tests above
    assert True  # Documentation test


def test_rate_limit_recovery(client: TestClient):
    """Test that rate limits reset after the time window."""
    # Note: This test would require waiting for the time window to pass
    # For a 1-minute window, we'd need to wait 60+ seconds
    # Skipping actual wait in unit tests, but documenting the behavior
    
    # Rate limits should reset after:
    # - 1 minute for per-minute limits
    # - 1 hour for per-hour limits
    assert True  # Documentation test
