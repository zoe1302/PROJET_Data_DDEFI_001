"""Batch 3 : prédire. Score un fichier CSV de clients et écrit la décision.

    python batch/predict.py --in data/processed/validation.csv --out predictions.csv

C'est ce qu'une banque ferait chaque nuit : un fichier entre, un fichier sort, avec pour chaque
client la probabilité de défaut et la décision au seuil de config.yaml. Le CSV d'entrée doit
avoir les colonnes du schéma (la cible peut manquer : on prédit, on ne mesure pas).

Attention : ne changez pas le seuil ici. Il vit dans config.yaml, avec sa justification dans
DECISIONS.md. Un seuil modifié à la main dans un script de nuit, c'est une décision que personne
n'a prise.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from credit.config import load_config  # noqa: E402
from credit.features import feature_columns  # noqa: E402
from credit.model import load_model  # noqa: E402

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True, help="CSV de clients à scorer")
    p.add_argument("--out", default="predictions.csv")
    p.add_argument("--model", default="baseline", choices=["naive", "baseline", "heavy"])
    a = p.parse_args()
    cfg = load_config()
    df = pd.read_csv(a.inp)
    cols = feature_columns(cfg)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise SystemExit(f"colonnes manquantes dans {a.inp} : {missing}")
    model = load_model(a.model)
    proba = model.predict_proba(df[cols])[:, 1]
    out = pd.DataFrame({"ID": df["ID"] if "ID" in df.columns else range(len(df)), "p_defaut": proba.round(4)})
    out["decision"] = ["refuser" if x >= cfg["threshold"] else "accepter" for x in proba]
    out.to_csv(a.out, index=False)
    print(f"{len(out)} clients scorés avec « {a.model} », seuil {cfg['threshold']} : {(out['decision'] == 'refuser').mean():.1%} refusés → {a.out}")
