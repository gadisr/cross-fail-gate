# cross-fail-gate

**Cluster holdout failures; allow rules/skills diffs only if the pattern spans ≥N episodes.**

Prevents overfitting to single-episode failures by enforcing cross-episode evidence. A proposed fix (rules patch, skill update, policy diff) is kept only if every claimed failure signature appears in at least N distinct episodes. Refuses single-episode "fixes" that would tune to noise.

## Use cases

### 1. SWE-bench skill/rules evolution gate

You're evolving agent skills across SWE-bench episodes. An agent proposes a new retry rule claiming to fix `ImportError: module X not found`. Before merging:

```bash
# failures.json: all episodes with their normalized failure signatures
cross-fail-gate check \
  --failures holdout_failures.json \
  --proposal skill_patch_v42.json \
  --min-episodes 3
```

**Example failures.json:**

```json
[
  {"episode_id": "django_123", "failure_signature": "ImportError_module_X"},
  {"episode_id": "flask_456", "failure_signature": "ImportError_module_X"},
  {"episode_id": "pandas_789", "failure_signature": "ImportError_module_X"},
  {"episode_id": "pytest_012", "failure_signature": "timeout_after_30s"}
]
```

**Example proposal:**

```json
{
  "diff_id": "add_import_retry_skill",
  "claimed_signatures": ["ImportError_module_X"]
}
```

**Exit 0**: All claimed signatures found in ≥3 episodes. Merge the skill.  
**Exit 2**: Signature appears in <3 episodes or not found. Reject as single-episode overfitting.

---

### 2. Meta-harness evolution refusing one-off patches

You're iterating on a harness that runs code-generation benchmarks. A proposed harness patch claims to fix `FileNotFoundError: workspace/temp` by adding `mkdir -p`. Gate it:

```bash
cross-fail-gate check \
  --failures benchmark_failures.json \
  --proposal harness_patch_mkdir.json \
  --min-episodes 2
```

**Example:**

```json
// benchmark_failures.json
[
  {"episode_id": "run_001", "failure_signature": "FileNotFoundError_workspace_temp"},
  {"episode_id": "run_072", "failure_signature": "PermissionError_write"}
]

// harness_patch_mkdir.json
{
  "claimed_signatures": ["FileNotFoundError_workspace_temp"],
  "note": "Add mkdir -p workspace/temp before test"
}
```

**Exit 2**: Signature appears in only 1 episode. Refuse the patch — likely environment-specific noise.

---

### 3. CI scoreboard promotion gate

You track agent scoreboard wins/losses. Before promoting a rule diff to prod, verify it fixes a cross-run pattern:

```bash
cross-fail-gate check \
  --failures ci_run_failures.json \
  --proposal rule_diff_429.json \
  --min-episodes 5 \
  --json > gate_result.json
```

**JSON output** (for downstream CI):

```json
{
  "allowed": false,
  "details": {
    "AssertionError_line_42": 2
  },
  "reasons": [
    "Signature 'AssertionError_line_42' appears in 2 episode(s), need 5"
  ]
}
```

CI reads `allowed: false` and blocks promotion.

---

## Install

```bash
pip install -e .
# or for development:
pip install -e ".[dev]"
```

**Requirements:** Python 3.11+, stdlib only (no dependencies).

## CLI

```bash
cross-fail-gate check \
  --failures <path>     # JSON list: [{"episode_id": str, "failure_signature": str, ...}, ...]
  --proposal <path>     # JSON: {"claimed_signatures": [str, ...], ...}
  --min-episodes N      # (default: 2)
  --json                # Output result as JSON
```

### Exit codes

- **0**: Allowed — all claimed signatures have ≥N episodes
- **2**: Refused — at least one signature has <N episodes or not found
- **1**: Error — invalid inputs or file not found

---

## With failstrata

`cross-fail-gate` is designed to compose with failstrata holdout validation. After a failstrata holdout run:

1. Export `failures.json` from holdout episodes
2. Cluster failures by normalized signature (error class, stack fingerprint, or tags)
3. Gate proposed rule/skill diffs with `cross-fail-gate` before merging

This prevents "fixes" that only address single-episode noise.

---

## Examples

See `examples/` for sample JSON files:

```bash
# Allowed: signature appears in 3 episodes
cross-fail-gate check \
  --failures examples/failures.json \
  --proposal examples/proposal_allowed.json \
  --min-episodes 3

# Refused: signature appears in 1 episode
cross-fail-gate check \
  --failures examples/failures.json \
  --proposal examples/proposal_refused.json \
  --min-episodes 2
```

---

## Tests

```bash
pytest -v
```

---

## License

MIT
