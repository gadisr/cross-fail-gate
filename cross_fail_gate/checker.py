"""Core logic for cross-episode failure validation."""

from collections import defaultdict
from typing import Any


def check_cross_episode_support(
    failures: list[dict[str, Any]],
    claimed_signatures: list[str],
    min_episodes: int,
) -> dict[str, Any]:
    """Check if claimed signatures have cross-episode support.
    
    Args:
        failures: List of failure records with episode_id and failure_signature
        claimed_signatures: List of signatures the proposal claims to address
        min_episodes: Minimum number of distinct episodes required
    
    Returns:
        Dict with 'allowed' (bool), 'details' (dict of signature -> episode count),
        and 'reasons' (list of rejection reasons if not allowed)
    """
    signature_episodes: dict[str, set[str]] = defaultdict(set)
    
    for failure in failures:
        sig = failure.get("failure_signature")
        ep = failure.get("episode_id")
        if sig is not None and ep is not None:
            signature_episodes[sig].add(str(ep))
    
    details = {}
    reasons = []
    
    for sig in claimed_signatures:
        if sig not in signature_episodes:
            episode_count = 0
            reasons.append(f"Signature '{sig}' not found in failure set")
        else:
            episode_count = len(signature_episodes[sig])
            if episode_count < min_episodes:
                reasons.append(
                    f"Signature '{sig}' appears in {episode_count} episode(s), "
                    f"need {min_episodes}"
                )
        
        details[sig] = episode_count
    
    allowed = len(reasons) == 0
    
    return {
        "allowed": allowed,
        "details": details,
        "reasons": reasons,
    }
