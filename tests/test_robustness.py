"""Tests de robustesse : un modèle n'est pas « bon » parce que son AUC est bonne.

Il est robuste quand il se comporte comme on l'attend quand les données bougent un peu :
du bruit sur les montants, une variable qui augmente, une valeur absurde, un autre tirage du
pli d'entraînement, un sous-groupe plutôt qu'un autre. Chaque test ci-dessous est une propriété
qu'on peut écrire AVANT de voir les résultats. Ils ne tournent que si make train a produit
models/baseline.pkl (en CI, make reproduce le fait).
"""

import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from credit.features import make_pipeline, split_xy
from credit.model import MODELS_DIR, load_model
from credit.split import load_fold

pytestmark = pytest.mark.skipif(not (MODELS_DIR / "baseline.pkl").exists(), reason="lancez make train")


@pytest.fixture(scope="module")
def val(cfg):
    df = load_fold("validation")
    X, y = split_xy(df, cfg)
    return df, X, y.to_numpy(), load_model("baseline")


def test_auc_confidence_interval_excludes_chance(val):
    """Bootstrap : l'AUC sur 1 000 rééchantillons de la validation reste loin de 0,5."""
    _, X, y, m = val
    p = m.predict_proba(X)[:, 1]
    rng = np.random.default_rng(0)
    aucs = [roc_auc_score(y[i], p[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(1000))]
    lo, hi = np.percentile(aucs, [2.5, 97.5])
    assert lo > 0.65, f"borne basse de l'IC à 95 % trop faible : {lo:.3f}"
    assert hi - lo < 0.06, f"IC trop large : [{lo:.3f}, {hi:.3f}]"


def test_small_noise_on_amounts_changes_little(val):
    """1 % de bruit sur les montants : aucune probabilité ne bouge de plus de 2 points, l'AUC de plus de 0,005."""
    _, X, y, m = val
    rng = np.random.default_rng(1)
    Xn = X.copy()
    for c in [c for c in X.columns if "AMT" in c or c == "LIMIT_BAL"]:
        Xn[c] = Xn[c] * (1 + rng.normal(0, 0.01, len(Xn)))
    p, pn = m.predict_proba(X)[:, 1], m.predict_proba(Xn)[:, 1]
    assert np.abs(pn - p).max() < 0.02
    assert abs(roc_auc_score(y, pn) - roc_auc_score(y, p)) < 0.005


def test_more_delay_means_more_risk(val):
    """Monotonie : un mois de retard en plus (PAY_0 + 1) ne doit jamais faire baisser le risque prédit."""
    _, X, _, m = val
    X2 = X.copy()
    X2["PAY_0"] = X2["PAY_0"] + 1
    p, p2 = m.predict_proba(X)[:, 1], m.predict_proba(X2)[:, 1]
    assert (p2 >= p - 1e-12).all()


def test_absurd_inputs_give_valid_probabilities(val):
    """Des valeurs absurdes (plafond d'un milliard, 200 ans) ne font pas planter et restent dans [0, 1]."""
    _, X, _, m = val
    Xe = X.iloc[:5].copy()
    Xe["LIMIT_BAL"] = 1e9
    Xe["AGE"] = 200
    pe = m.predict_proba(Xe)[:, 1]
    assert np.isfinite(pe).all() and (pe >= 0).all() and (pe <= 1).all()


def test_stable_across_training_resamples(val, cfg):
    """Cinq rééchantillons bootstrap du pli d'entraînement : l'AUC de validation bouge de moins de 0,01."""
    _, X, y, _ = val
    Xt, yt = split_xy(load_fold("train"), cfg)
    aucs = []
    for s in range(5):
        i = np.random.default_rng(s).integers(0, len(Xt), len(Xt))
        pipe = make_pipeline(LogisticRegression(max_iter=2000), cfg).fit(Xt.iloc[i], yt.iloc[i])
        aucs.append(roc_auc_score(y, pipe.predict_proba(X)[:, 1]))
    assert max(aucs) - min(aucs) < 0.01, aucs


def test_no_subgroup_is_left_behind(val):
    """Tranches : l'AUC par statut marital (groupes de plus de 500 clients) reste au-dessus de 0,65."""
    df, X, y, m = val
    for g, grp in df.groupby("MARRIAGE"):
        if len(grp) < 500:
            continue
        pg = m.predict_proba(grp[X.columns])[:, 1]
        assert roc_auc_score(grp["default"], pg) > 0.65, f"MARRIAGE={g}"
