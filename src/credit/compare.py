"""make compare : les trois modèles sur le pli de test, une seule fois, au jalon 2.

Règle du cours : on n'ouvre ce fichier qu'après avoir écrit dans DECISIONS.md la règle du
champion (quel modèle gagne, à quelle condition, avec quel intervalle). Le script le vérifie
grossièrement : il refuse de tourner si DECISIONS.md ne contient pas la ligne « Règle du champion ».
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from credit.config import ROOT, load_config
from credit.evaluate import metrics
from credit.features import split_xy
from credit.model import heavy, load_model, save_model
from credit.split import load_fold


def main(cfg: dict, out: Path) -> dict:
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    if "Règle du champion" not in decisions:
        raise SystemExit("Écrivez d'abord la « Règle du champion » dans DECISIONS.md, puis relancez make compare.")
    df = load_fold("test")
    X, y = split_xy(df, cfg)
    c_fp, c_fn, t = cfg["costs"]["c_fp"], cfg["costs"]["c_fn"], cfg["threshold"]
    out_d = {"pli": "test", "graine": cfg["seed"], "modeles": {}}
    for name in ("naive", "baseline"):
        out_d["modeles"][name] = metrics(y, load_model(name).predict_proba(X)[:, 1], t, c_fp, c_fn)
    try:
        hv = load_model("heavy")
    except FileNotFoundError:
        hv = heavy(cfg)  # lève NotImplementedError tant que le jalon 2 n'est pas fait
        save_model(hv, "heavy")
    out_d["modeles"]["heavy"] = metrics(y, hv.predict_proba(X)[:, 1], t, c_fp, c_fn)
    out.write_text(json.dumps(out_d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_d


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--out", type=Path, default=ROOT / "compare.json")
    a = p.parse_args()
    res = main(load_config(a.config), a.out)
    for name, m in res["modeles"].items():
        print(f"{name:9s} AUC {m['auc']}  Brier {m['brier']}  coût/dossier {m['cout_attendu_par_dossier']} €")
