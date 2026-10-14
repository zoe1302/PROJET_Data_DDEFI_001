"""Les tests importent src/credit sans installation : on ajoute src/ au chemin."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit.config import load_config  # noqa: E402
from credit.data import load_raw  # noqa: E402


@pytest.fixture(scope="session")
def cfg():
    return load_config("config.yaml")


@pytest.fixture(scope="session")
def raw():
    return load_raw()
