#!/usr/bin/env python3
"""Tests for QA configuration."""

from qa.config import QAConfig


def test_qa_config_default():
    """Test default QA configuration."""
    config = QAConfig()
    assert config is not None
