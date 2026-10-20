#!/usr/bin/env python3
"""Initialize all three SQLite databases from schema files."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_all_dbs

if __name__ == "__main__":
    init_all_dbs()
    print("All databases initialized.")
