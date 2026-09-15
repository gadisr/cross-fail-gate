"""Command-line interface for cross-fail-gate."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from cross_fail_gate.checker import check_cross_episode_support


def load_json(path: Path) -> Any:
    """Load and parse JSON file."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def check_command(args: argparse.Namespace) -> int:
    """Execute the check command."""
    failures_data = load_json(args.failures)
    proposal_data = load_json(args.proposal)
    
    if not isinstance(failures_data, list):
        print("Error: failures.json must contain a list", file=sys.stderr)
        return 1
    
    claimed_signatures = proposal_data.get("claimed_signatures", [])
    if not isinstance(claimed_signatures, list):
        print("Error: proposal must have 'claimed_signatures' list", file=sys.stderr)
        return 1
    
    result = check_cross_episode_support(
        failures=failures_data,
        claimed_signatures=claimed_signatures,
        min_episodes=args.min_episodes,
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["allowed"]:
            print("✓ ALLOWED: All claimed signatures have cross-episode support")
            for sig, count in result["details"].items():
                print(f"  • {sig}: {count} episode(s)")
        else:
            print("✗ REFUSED: Insufficient cross-episode support", file=sys.stderr)
            for reason in result["reasons"]:
                print(f"  • {reason}", file=sys.stderr)
            if result["details"]:
                print("\nSignature details:", file=sys.stderr)
                for sig, count in result["details"].items():
                    print(f"  • {sig}: {count} episode(s)", file=sys.stderr)
    
    return 0 if result["allowed"] else 2


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="cross-fail-gate",
        description="Cluster holdout failures; allow diffs only if pattern spans ≥N episodes",
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    check_parser = subparsers.add_parser(
        "check",
        help="Check if proposal has cross-episode support",
    )
    check_parser.add_argument(
        "--failures",
        type=Path,
        required=True,
        help="Path to failures.json",
    )
    check_parser.add_argument(
        "--proposal",
        type=Path,
        required=True,
        help="Path to proposal.json",
    )
    check_parser.add_argument(
        "--min-episodes",
        type=int,
        default=2,
        help="Minimum distinct episodes required (default: 2)",
    )
    check_parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    
    args = parser.parse_args()
    
    if args.command == "check":
        return check_command(args)
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
