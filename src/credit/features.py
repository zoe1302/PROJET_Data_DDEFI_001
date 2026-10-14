"""Les variables : ce qui entre dans le modèle, et comment.

Trois familles de colonnes dans les données UCI :
  - des montants (LIMIT_BAL, BILL_AMT1-6, PAY_AMT1-6) et l'âge : des nombres, standardisés ;
  - des statuts de retard (PAY_0, PAY_2 à PAY_6) : des entiers ordonnés (-2 à 8), gardés tels quels ;
  - des catégories (EDUCATION, MARRIAGE) : encodées en indicatrices.

Attention à trois choses.
  1. SEX est exclue : c'est un garde-fou (directive 2004/113/CE), pas un choix de performance.
     MARRIAGE est autorisée, à condition d'auditer l'équité au jalon 2 (voir d7).
  2. Le Pipeline apprend ses moyennes et ses écarts-types sur le pli d'entraînement seulement :
     c'est lui qui empêche la fuite. Ne standardisez jamais le jeu entier avant la coupe.
  3. Pas de variable qui regarde le futur : ici la cible est le défaut d'octobre, toutes les
     colonnes sont d'avril à septembre, donc la carte des fuites est vide. Sur votre propre sujet,
     c'est la première chose à vérifier.
"""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from credit.data import TARGET

NUMERIC = ["LIMIT_BAL", "AGE"] + [f"BILL_AMT{i}" for i in range(1, 7)] + [f"PAY_AMT{i}" for i in range(1, 7)]
ORDINAL = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
CATEGORICAL = ["EDUCATION", "MARRIAGE"]


def feature_columns(cfg: dict) -> list[str]:
    """Toutes les colonnes utilisées, dans un ordre fixe, moins celles exclues par config.yaml."""
    cols = NUMERIC + ORDINAL + CATEGORICAL
    return [c for c in cols if c not in cfg["excluded_features"]]


def split_xy(df: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.Series]:
    """Sépare les variables et la cible d'un pli."""
    cols = feature_columns(cfg)
    forbidden = [c for c in cfg["excluded_features"] if c in cols]
    if forbidden:
        raise ValueError(f"colonnes interdites dans les variables : {forbidden}")
    return df[cols], df[TARGET].astype(int)


def preprocessor(cfg: dict) -> ColumnTransformer:
    """Le prétraitement, à placer en tête d'un Pipeline : il n'apprend que sur ce qu'on lui donne en fit."""
    cols = feature_columns(cfg)
    return ColumnTransformer(
        [
            ("num", StandardScaler(), [c for c in NUMERIC if c in cols]),
            ("ord", "passthrough", [c for c in ORDINAL if c in cols]),
            ("cat", OneHotEncoder(handle_unknown="ignore"), [c for c in CATEGORICAL if c in cols]),
        ]
    )


def make_pipeline(estimator, cfg: dict) -> Pipeline:
    """Prétraitement puis modèle, dans un seul objet : ce qu'on entraîne, sauve et recharge."""
    return Pipeline([("prep", preprocessor(cfg)), ("model", estimator)])
