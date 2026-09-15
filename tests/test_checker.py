"""Tests for core checker logic."""

import pytest

from cross_fail_gate.checker import check_cross_episode_support


def test_allow_with_sufficient_episodes():
    """Test that signatures with ≥N episodes are allowed."""
    failures = [
        {"episode_id": "ep1", "failure_signature": "timeout"},
        {"episode_id": "ep2", "failure_signature": "timeout"},
        {"episode_id": "ep3", "failure_signature": "timeout"},
    ]
    claimed = ["timeout"]
    
    result = check_cross_episode_support(failures, claimed, min_episodes=2)
    
    assert result["allowed"] is True
    assert result["details"]["timeout"] == 3
    assert result["reasons"] == []


def test_refuse_with_insufficient_episodes():
    """Test that signatures with <N episodes are refused."""
    failures = [
        {"episode_id": "ep1", "failure_signature": "timeout"},
    ]
    claimed = ["timeout"]
    
    result = check_cross_episode_support(failures, claimed, min_episodes=2)
    
    assert result["allowed"] is False
    assert result["details"]["timeout"] == 1
    assert len(result["reasons"]) == 1
    assert "appears in 1 episode" in result["reasons"][0]


def test_refuse_missing_signature():
    """Test that claimed signatures not in failures are refused."""
    failures = [
        {"episode_id": "ep1", "failure_signature": "timeout"},
    ]
    claimed = ["missing_sig"]
    
    result = check_cross_episode_support(failures, claimed, min_episodes=2)
    
    assert result["allowed"] is False
    assert result["details"]["missing_sig"] == 0
    assert "not found in failure set" in result["reasons"][0]


def test_multiple_signatures_mixed():
    """Test multiple claimed signatures with mixed support."""
    failures = [
        {"episode_id": "ep1", "failure_signature": "timeout"},
        {"episode_id": "ep2", "failure_signature": "timeout"},
        {"episode_id": "ep3", "failure_signature": "crash"},
    ]
    claimed = ["timeout", "crash"]
    
    result = check_cross_episode_support(failures, claimed, min_episodes=2)
    
    assert result["allowed"] is False
    assert result["details"]["timeout"] == 2
    assert result["details"]["crash"] == 1
    assert len(result["reasons"]) == 1
    assert "crash" in result["reasons"][0]


def test_empty_inputs():
    """Test with empty failure list."""
    result = check_cross_episode_support([], ["sig"], min_episodes=2)
    
    assert result["allowed"] is False
    assert result["details"]["sig"] == 0


def test_duplicate_episodes_counted_once():
    """Test that same episode appearing multiple times counts as one."""
    failures = [
        {"episode_id": "ep1", "failure_signature": "timeout"},
        {"episode_id": "ep1", "failure_signature": "timeout"},
        {"episode_id": "ep2", "failure_signature": "timeout"},
    ]
    claimed = ["timeout"]
    
    result = check_cross_episode_support(failures, claimed, min_episodes=2)
    
    assert result["allowed"] is True
    assert result["details"]["timeout"] == 2


def test_no_claimed_signatures():
    """Test with no claimed signatures."""
    failures = [
        {"episode_id": "ep1", "failure_signature": "timeout"},
    ]
    
    result = check_cross_episode_support(failures, [], min_episodes=2)
    
    assert result["allowed"] is True
    assert result["details"] == {}
    assert result["reasons"] == []


def test_all_signatures_allowed():
    """Test when all claimed signatures meet threshold."""
    failures = [
        {"episode_id": "ep1", "failure_signature": "timeout"},
        {"episode_id": "ep2", "failure_signature": "timeout"},
        {"episode_id": "ep3", "failure_signature": "crash"},
        {"episode_id": "ep4", "failure_signature": "crash"},
    ]
    claimed = ["timeout", "crash"]
    
    result = check_cross_episode_support(failures, claimed, min_episodes=2)
    
    assert result["allowed"] is True
    assert result["details"]["timeout"] == 2
    assert result["details"]["crash"] == 2
    assert result["reasons"] == []
