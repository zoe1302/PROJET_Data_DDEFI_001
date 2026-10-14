"""Lecture de config.yaml : une seule graine, des coûts, un seuil, des colonnes exclues."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_config(path: str | Path = "config.yaml") -> dict:
    """Lit la configuration et vérifie les champs dont le reste du code dépend."""
    with open(ROOT / path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    for key in ("seed", "split", "costs", "threshold", "excluded_features"):
        if key not in cfg:
            raise KeyError(f"config.yaml : la clé « {key} » manque")
    total = sum(cfg["split"].values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"config.yaml : les parts de la coupe font {total}, pas 1")
    return cfg
