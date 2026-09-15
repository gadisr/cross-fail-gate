"""Allow execution via python -m cross_fail_gate."""

import sys

from cross_fail_gate.cli import main

if __name__ == "__main__":
    sys.exit(main())
