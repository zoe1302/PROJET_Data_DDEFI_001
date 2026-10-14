"""La coupe figée : entraînement, validation, test, stratifiée sur la cible, par la graine.

Attention : la coupe se fait une fois, avant toute exploration. Tout ce qu'on apprend des données
(moyennes, seuils, choix de variables) s'apprend sur le pli d'entraînement. Le pli de test ne se lit
qu'au jalon 2, une seule fois, avec make compare.

Chaque pli est haché : le test test_split_is_frozen vérifie que la coupe n'a pas bougé.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from credit.config import ROOT, load_config
from credit.data import TARGET, load_raw

PROCESSED = ROOT / "data" / "processed"
FOLDS = ("train", "validation", "test")


def make_split(df: pd.DataFrame, cfg: dict) -> dict[str, pd.DataFrame]:
    """Deux coupes stratifiées successives : d'abord le test, puis la validation dans le reste."""
    seed = cfg["seed"]
    parts = cfg["split"]
    rest, test = train_test_split(df, test_size=parts["test"], stratify=df[TARGET], random_state=seed)
    val_share = parts["validation"] / (parts["train"] + parts["validation"])
    train, val = train_test_split(rest, test_size=val_share, stratify=rest[TARGET], random_state=seed)
    return {"train": train, "validation": val, "test": test}


def fold_hash(df: pd.DataFrame) -> str:
    """L'empreinte d'un pli : la liste triée de ses identifiants suffit."""
    ids = ",".join(map(str, sorted(df["ID"].tolist())))
    return hashlib.sha256(ids.encode()).hexdigest()


def write_split(cfg: dict) -> dict[str, str]:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    folds = make_split(load_raw(), cfg)
    hashes = {}
    for name in FOLDS:
        folds[name].to_csv(PROCESSED / f"{name}.csv", index=False)
        hashes[name] = fold_hash(folds[name])
    (PROCESSED / "hashes.txt").write_text("".join(f"{k} {v}\n" for k, v in hashes.items()), encoding="utf-8")
    return hashes


def load_fold(name: str) -> pd.DataFrame:
    if name not in FOLDS:
        raise ValueError(f"pli inconnu : {name}")
    path = PROCESSED / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError("la coupe n'existe pas : lancez make split")
    return pd.read_csv(path)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="La coupe figée train / validation / test.")
    p.add_argument("--config", default="config.yaml")
    a = p.parse_args()
    cfg = load_config(a.config)
    h = write_split(cfg)
    for name in FOLDS:
        df = load_fold(name)
        print(f"{name:11s} {len(df):6d} lignes, taux de défaut {df[TARGET].mean():.4f}, empreinte {h[name][:12]}…")
