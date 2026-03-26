from __future__ import annotations

import uuid


def generate_run_id() -> str:
    return f"run_{uuid.uuid4().hex}"
