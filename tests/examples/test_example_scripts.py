"""Smoke tests asserting every example script runs cleanly."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = PACKAGE_ROOT / "examples"
SRC_DIR = PACKAGE_ROOT / "src"

EXAMPLE_SCRIPTS = sorted(path.name for path in EXAMPLES_DIR.glob("*.py"))


@pytest.fixture(autouse=True)
def _remove_generated_outputs() -> Iterator[None]:
    """Delete any ``*.output.*`` files an example writes during the test."""
    yield
    for output in EXAMPLES_DIR.glob("*.output.*"):
        output.unlink()


@pytest.mark.parametrize("script", EXAMPLE_SCRIPTS)
def test_example_runs_cleanly(script: str) -> None:
    """Each example script should run to completion and print something."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(part for part in (str(SRC_DIR), env.get("PYTHONPATH", "")) if part)

    result = subprocess.run(
        [sys.executable, str(EXAMPLES_DIR / script)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), "example produced no stdout"
