"""Batch 2 : entraîner. Le modèle naïf et la logistique calibrée, sauvés dans models/.

    python batch/train.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from credit.config import load_config  # noqa: E402
from credit.model import baseline, naive, save_model  # noqa: E402

if __name__ == "__main__":
    cfg = load_config()
    for name, fn in (("naive", naive), ("baseline", baseline)):
        print(name, "→", save_model(fn(cfg), name))
