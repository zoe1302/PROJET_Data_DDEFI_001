"""Test 1, le contrat de schéma : les données qui entrent sont celles qu'on attend.

Un test de ML n'est pas « l'AUC est bonne ». C'est une propriété qui doit être vraie quoi qu'il
arrive : les bornes, les types, les manquants, le nombre de lignes.
"""

from credit.data import SCHEMA, TARGET


def test_schema_contract(raw):
    assert list(raw.columns) == SCHEMA["columns"]
    assert len(raw) == SCHEMA["n_rows"]
    assert raw["LIMIT_BAL"].min() > 0
    assert raw[TARGET].isin([0, 1]).all()
    assert raw.isna().mean().max() < 0.05
    # Le taux de défaut connu du jeu UCI : 6 636 défauts sur 30 000, soit 22,12 %.
    assert abs(raw[TARGET].mean() - 0.2212) < 0.001
