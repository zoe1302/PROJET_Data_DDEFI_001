"""Batch 4 : évaluer. Les métriques des modèles sauvés sur la validation, dans metrics.json.

    python batch/evaluate.py

Le pli de test est interdit ici : il ne se lit qu'avec make compare, une fois, au jalon 2.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from credit.config import ROOT, load_config  # noqa: E402
from credit.evaluate import evaluate_models  # noqa: E402

if __name__ == "__main__":
    cfg = load_config()
    res = evaluate_models(cfg, "validation")
    (ROOT / "metrics.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, m in res["modeles"].items():
        print(f"{name:9s} AUC {m['auc']}  Brier {m['brier']}  coût/dossier {m['cout_attendu_par_dossier']} €")
