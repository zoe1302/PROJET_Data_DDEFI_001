"""Tests 3 à 5 : le code d'entraînement n'est pas cassé, la prédiction est stable, le modèle sauvé est le modèle entraîné."""

import pickle

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from credit.features import feature_columns, make_pipeline, split_xy
from credit.model import BaseRate, MODELS_DIR, load_model
from credit.split import load_fold


def _separable(cfg, n=400, seed=0):
    """Des données artificielles où la cible se lit directement sur LIMIT_BAL : AUC doit valoir 1."""
    rng = np.random.default_rng(seed)
    cols = feature_columns(cfg)
    df = pd.DataFrame({c: rng.integers(-1, 3, n) for c in cols})
    df["EDUCATION"] = rng.integers(1, 4, n)
    df["MARRIAGE"] = rng.integers(1, 3, n)
    df["AGE"] = rng.integers(21, 70, n)
    df["LIMIT_BAL"] = rng.uniform(10_000, 500_000, n)
    df["default"] = (df["LIMIT_BAL"] > 250_000).astype(int)
    return df


def test_auc_is_one_on_separable_data(cfg):
    df = _separable(cfg)
    X, y = split_xy(df, cfg)
    pipe = make_pipeline(LogisticRegression(max_iter=2000, random_state=cfg["seed"]), cfg).fit(X, y)
    assert roc_auc_score(y, pipe.predict_proba(X)[:, 1]) == 1.0


def test_predict_invariant_to_row_permutation(cfg):
    df = _separable(cfg, seed=1)
    X, y = split_xy(df, cfg)
    pipe = make_pipeline(LogisticRegression(max_iter=2000, random_state=cfg["seed"]), cfg).fit(X, y)
    perm = np.random.default_rng(2).permutation(len(X))
    p1 = pipe.predict_proba(X)[:, 1][perm]
    p2 = pipe.predict_proba(X.iloc[perm])[:, 1]
    assert np.allclose(p1, p2)


def test_loaded_pipeline_matches_trained(cfg, tmp_path):
    df = _separable(cfg, seed=3)
    X, y = split_xy(df, cfg)
    pipe = make_pipeline(LogisticRegression(max_iter=2000, random_state=cfg["seed"]), cfg).fit(X, y)
    path = tmp_path / "m.pkl"
    with open(path, "wb") as f:
        pickle.dump(pipe, f)
    with open(path, "rb") as f:
        again = pickle.load(f)
    assert np.max(np.abs(pipe.predict_proba(X) - again.predict_proba(X))) < 1e-12


def test_naive_predicts_base_rate(cfg):
    y = np.array([0, 0, 0, 1])
    m = BaseRate().fit(np.zeros((4, 1)), y)
    assert np.allclose(m.predict_proba(np.zeros((3, 1)))[:, 1], 0.25)


def test_baseline_beats_naive_on_validation(cfg):
    """Si make train a tourné : la logistique doit battre nettement le taux de base, sinon fuite ou bug."""
    if not (MODELS_DIR / "baseline.pkl").exists():
        return  # pas encore entraîné (CI sans make train) : rien à vérifier
    X, y = split_xy(load_fold("validation"), cfg)
    p = load_model("baseline").predict_proba(X)[:, 1]
    assert roc_auc_score(y, p) > 0.70
