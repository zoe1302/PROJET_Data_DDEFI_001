"""Batch 1 : préparer. Télécharge les données, vérifie l'empreinte, écrit la coupe figée.

    python batch/prepare.py

Équivalent de `make data split`. Les scripts de batch/ enchaînent les modules de src/credit ;
ils ne contiennent pas de logique : si vous écrivez du code ici, c'est qu'il manque dans src/.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from credit.config import ROOT, load_config  # noqa: E402
from credit.data import check_hash  # noqa: E402
from credit.split import write_split  # noqa: E402

if __name__ == "__main__":
    cfg = load_config()
    check_hash(ROOT / "data" / "sha256.txt")
    hashes = write_split(cfg)
    print("coupe écrite :", ", ".join(f"{k} {v[:8]}…" for k, v in hashes.items()))
