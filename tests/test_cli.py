"""Tests for CLI interface."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def temp_files(tmp_path):
    """Create temporary JSON files for testing."""
    failures_file = tmp_path / "failures.json"
    proposal_file = tmp_path / "proposal.json"
    return failures_file, proposal_file


def test_cli_allow(temp_files):
    """Test CLI with allowed proposal."""
    failures_file, proposal_file = temp_files
    
    failures_file.write_text(json.dumps([
        {"episode_id": "ep1", "failure_signature": "timeout"},
        {"episode_id": "ep2", "failure_signature": "timeout"},
    ]))
    
    proposal_file.write_text(json.dumps({
        "claimed_signatures": ["timeout"],
    }))
    
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cross_fail_gate",
            "check",
            "--failures",
            str(failures_file),
            "--proposal",
            str(proposal_file),
            "--min-episodes",
            "2",
        ],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    assert "ALLOWED" in result.stdout


def test_cli_refuse(temp_files):
    """Test CLI with refused proposal."""
    failures_file, proposal_file = temp_files
    
    failures_file.write_text(json.dumps([
        {"episode_id": "ep1", "failure_signature": "timeout"},
    ]))
    
    proposal_file.write_text(json.dumps({
        "claimed_signatures": ["timeout"],
    }))
    
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cross_fail_gate",
            "check",
            "--failures",
            str(failures_file),
            "--proposal",
            str(proposal_file),
            "--min-episodes",
            "2",
        ],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 2
    assert "REFUSED" in result.stderr


def test_cli_json_output(temp_files):
    """Test CLI with JSON output."""
    failures_file, proposal_file = temp_files
    
    failures_file.write_text(json.dumps([
        {"episode_id": "ep1", "failure_signature": "timeout"},
        {"episode_id": "ep2", "failure_signature": "timeout"},
    ]))
    
    proposal_file.write_text(json.dumps({
        "claimed_signatures": ["timeout"],
    }))
    
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cross_fail_gate",
            "check",
            "--failures",
            str(failures_file),
            "--proposal",
            str(proposal_file),
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["allowed"] is True
    assert "timeout" in output["details"]


def test_cli_missing_file(tmp_path):
    """Test CLI with missing file."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cross_fail_gate",
            "check",
            "--failures",
            str(tmp_path / "missing.json"),
            "--proposal",
            str(tmp_path / "proposal.json"),
        ],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 1
    assert "not found" in result.stderr


def test_cli_default_min_episodes(temp_files):
    """Test CLI with default min-episodes value."""
    failures_file, proposal_file = temp_files
    
    failures_file.write_text(json.dumps([
        {"episode_id": "ep1", "failure_signature": "timeout"},
        {"episode_id": "ep2", "failure_signature": "timeout"},
    ]))
    
    proposal_file.write_text(json.dumps({
        "claimed_signatures": ["timeout"],
    }))
    
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cross_fail_gate",
            "check",
            "--failures",
            str(failures_file),
            "--proposal",
            str(proposal_file),
        ],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
