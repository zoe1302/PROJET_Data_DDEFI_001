"""Les métriques : deux lecteurs, deux familles.

Pour l'ingénieur : AUC (l'ordre), log-loss et Brier (la calibration), courbe de calibration.
Pour le comité : le coût attendu en euros au seuil choisi, et la courbe de coût C(t).

Attention : une métrique se calcule sur le pli de validation pendant tout le cours.
Le pli de test ne sert qu'une fois, à make compare (jalon 2), après que la règle du champion
a été écrite dans DECISIONS.md.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score

from credit.config import ROOT, load_config
from credit.features import split_xy
from credit.model import load_model
from credit.split import load_fold


def expected_cost(y: np.ndarray, p: np.ndarray, t: float, c_fp: float, c_fn: float) -> float:
    """Coût moyen par dossier au seuil t : on refuse si p >= t.

    Faux positif : refusé (p >= t) alors que y = 0, coûte c_fp.
    Faux négatif : accepté (p < t) alors que y = 1, coûte c_fn.
    """
    y = np.asarray(y)
    p = np.asarray(p)
    refuse = p >= t
    fp = np.sum(refuse & (y == 0))
    fn = np.sum(~refuse & (y == 1))
    return float((c_fp * fp + c_fn * fn) / len(y))


def cost_curve(y, p, c_fp: float, c_fn: float, grid: np.ndarray | None = None) -> pd.DataFrame:
    """C(t) sur une grille de seuils : la courbe qu'on montre au comité."""
    grid = np.linspace(0.0, 1.0, 201) if grid is None else grid
    return pd.DataFrame({"t": grid, "cost": [expected_cost(y, p, t, c_fp, c_fn) for t in grid]})


def best_threshold(y, p, c_fp: float, c_fn: float) -> float:
    """L'argmin de C(t) sur la grille : le seuil qu'on écrit ensuite dans config.yaml."""
    curve = cost_curve(y, p, c_fp, c_fn)
    return float(curve.loc[curve["cost"].idxmin(), "t"])


def confusion(y, p, t: float) -> dict[str, int]:
    y = np.asarray(y)
    refuse = np.asarray(p) >= t
    return {
        "VP": int(np.sum(refuse & (y == 1))),
        "FP": int(np.sum(refuse & (y == 0))),
        "FN": int(np.sum(~refuse & (y == 1))),
        "VN": int(np.sum(~refuse & (y == 0))),
    }


def calibration_table(y, p, bins: int = 10) -> list[dict]:
    """Par tranche de probabilité prédite : la fréquence observée. Calibré = les deux se suivent."""
    df = pd.DataFrame({"y": np.asarray(y), "p": np.asarray(p)})
    df["bin"] = pd.cut(df["p"], bins=np.linspace(0, 1, bins + 1), include_lowest=True)
    out = []
    for b, g in df.groupby("bin", observed=True):
        out.append({"tranche": str(b), "n": int(len(g)), "p_moyen": round(float(g["p"].mean()), 4), "taux_observe": round(float(g["y"].mean()), 4)})
    return out


def metrics(y, p, t: float, c_fp: float, c_fn: float) -> dict:
    """Le bloc de métriques complet pour un modèle sur un pli."""
    y = np.asarray(y)
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1 - 1e-12)
    cm = confusion(y, p, t)
    precision = cm["VP"] / (cm["VP"] + cm["FP"]) if cm["VP"] + cm["FP"] else 0.0
    recall = cm["VP"] / (cm["VP"] + cm["FN"]) if cm["VP"] + cm["FN"] else 0.0
    return {
        "n": int(len(y)),
        "taux_defaut": round(float(y.mean()), 4),
        "auc": round(float(roc_auc_score(y, p)), 4) if len(np.unique(y)) > 1 else None,
        "log_loss": round(float(log_loss(y, p)), 4),
        "brier": round(float(brier_score_loss(y, p)), 4),
        "seuil": t,
        "matrice": cm,
        "precision": round(precision, 4),
        "rappel": round(recall, 4),
        "cout_attendu_par_dossier": round(expected_cost(y, p, t, c_fp, c_fn), 2),
        "cout_attendu_total": round(expected_cost(y, p, t, c_fp, c_fn) * len(y), 0),
    }


def evaluate_models(cfg: dict, fold: str = "validation") -> dict:
    """Tous les modèles sauvés, sur un pli : le contenu de metrics.json."""
    df = load_fold(fold)
    X, y = split_xy(df, cfg)
    c_fp, c_fn = cfg["costs"]["c_fp"], cfg["costs"]["c_fn"]
    t = cfg["threshold"]
    out = {"pli": fold, "graine": cfg["seed"], "couts": cfg["costs"], "modeles": {}}
    for name in ("naive", "baseline"):
        model = load_model(name)
        p = model.predict_proba(X)[:, 1]
        out["modeles"][name] = metrics(y, p, t, c_fp, c_fn)
        out["modeles"][name]["calibration"] = calibration_table(y, p)
    out["seuil_optimal_validation"] = best_threshold(y, load_model("baseline").predict_proba(X)[:, 1], c_fp, c_fn)
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Les métriques des modèles sauvés, sur la validation.")
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--fold", default="validation", help="validation (toujours) ; test seulement via make compare")
    p.add_argument("--out", type=Path, default=ROOT / "metrics.json")
    a = p.parse_args()
    if a.fold == "test":
        raise SystemExit("Le pli de test ne se lit qu'avec make compare, une seule fois, au jalon 2.")
    cfg = load_config(a.config)
    res = evaluate_models(cfg, a.fold)
    a.out.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, m in res["modeles"].items():
        print(f"{name:9s} AUC {m['auc']}  log-loss {m['log_loss']}  Brier {m['brier']}  coût/dossier {m['cout_attendu_par_dossier']} €")
    print(f"seuil optimal sur la validation : {res['seuil_optimal_validation']:.4f} (config.yaml : {cfg['threshold']})")
