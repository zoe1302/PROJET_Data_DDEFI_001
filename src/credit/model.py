"""Les trois modèles : naïf, meilleur, lourd.

  naïf      : le taux de base. Prédit 22,1 % à tout le monde. Log-loss = entropie de la cible, 0,528 nats.
              Si votre meilleur modèle ne bat pas ça nettement, il y a un bug ou une fuite.
  meilleur  : régression logistique sur un Pipeline (standardisation apprise sur l'entraînement),
              puis calibration de Platt sur le pli de validation ; seuil choisi par les coûts.
  lourd     : à vous (jalon 2). La fonction heavy() dit quoi faire et refuse de tourner tant qu'elle
              n'est pas écrite. Ne la copiez pas d'un assistant sans pouvoir l'expliquer ligne par ligne.

Attention : on sauve le Pipeline entier (prétraitement + modèle). Un modèle sauvé sans son
prétraitement ne sert à rien : personne ne sait plus quelles moyennes il attend.
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression

from credit.config import ROOT, load_config
from credit.features import make_pipeline, split_xy
from credit.split import load_fold

MODELS_DIR = ROOT / "models"


class BaseRate(BaseEstimator, ClassifierMixin):
    """Le modèle naïf : la même probabilité pour tout le monde, le taux de défaut de l'entraînement."""

    def fit(self, X, y):
        y = np.asarray(y)
        self.classes_ = np.array([0, 1])
        self.rate_ = float(np.mean(y))
        return self

    def predict_proba(self, X):
        n = len(X)
        return np.column_stack([np.full(n, 1 - self.rate_), np.full(n, self.rate_)])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


def naive(cfg: dict):
    """Entraîne le modèle naïf sur le pli d'entraînement."""
    X, y = split_xy(load_fold("train"), cfg)
    return BaseRate().fit(X, y)


def baseline(cfg: dict):
    """La logistique calibrée : Pipeline sur l'entraînement, calibration sur la validation.

    class_weight n'est pas utilisé : la calibration rendrait les probabilités fausses.
    On garde des probabilités honnêtes et on déplace le seuil (séance 4).
    """
    X_tr, y_tr = split_xy(load_fold("train"), cfg)
    X_val, y_val = split_xy(load_fold("validation"), cfg)
    pipe = make_pipeline(LogisticRegression(max_iter=2000, random_state=cfg["seed"]), cfg)
    pipe.fit(X_tr, y_tr)
    # Platt : une sigmoïde ajustée sur la validation, par-dessus le Pipeline déjà entraîné (FrozenEstimator :
    # le Pipeline ne se réentraîne pas, seule la sigmoïde apprend).
    # Attention : la validation sert ici à calibrer, donc le seuil choisi ensuite sur la même
    # validation est légèrement optimiste. On le sait, on l'écrit dans DECISIONS.md, et le test
    # tranchera une fois au jalon 2.
    cal = CalibratedClassifierCV(FrozenEstimator(pipe), method="sigmoid")
    cal.fit(X_val, y_val)
    return cal


def heavy(cfg: dict):
    """Le modèle lourd : jalon 2, à vous.

    Ce qu'on attend (voir d6) :
      1. un XGBClassifier dans le même make_pipeline(), avec random_state=cfg["seed"] ;
      2. ses hyperparamètres choisis par validation croisée sur le pli d'entraînement SEULEMENT
         (n_estimators, max_depth, learning_rate : trois valeurs chacun suffisent) ;
      3. la même calibration que la baseline, sur la validation ;
      4. la règle du champion écrite dans DECISIONS.md AVANT de lancer make compare ;
      5. un test apparié corrigé (Nadeau et Bengio) entre baseline et lourd sur les plis.
    Pièges : ne pas chercher les hyperparamètres sur la validation (elle sert à calibrer et à
    choisir le seuil) ; ne pas lire le test ; ne pas comparer des AUC sans intervalle.
    """
    raise NotImplementedError("Le modèle lourd est le travail du jalon 2 : lisez la docstring de heavy().")


def save_model(model, name: str) -> Path:
    MODELS_DIR.mkdir(exist_ok=True)
    path = MODELS_DIR / f"{name}.pkl"
    with open(path, "wb") as f:
        pickle.dump(model, f)
    return path


def load_model(name: str):
    path = MODELS_DIR / f"{name}.pkl"
    if not path.exists():
        raise FileNotFoundError(f"{path.name} manque : lancez make train")
    with open(path, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Entraîne le modèle naïf et la logistique calibrée.")
    p.add_argument("--config", default="config.yaml")
    a = p.parse_args()
    cfg = load_config(a.config)
    # On passe par le module importé, pas par __main__ : sinon le pickle du modèle naïf
    # retiendrait « __main__.BaseRate » et ne se rechargerait plus depuis les autres scripts.
    import credit.model as mod

    for name, fn in (("naive", mod.naive), ("baseline", mod.baseline)):
        m = fn(cfg)
        path = mod.save_model(m, name)
        print(f"{name:9s} entraîné, sauvé dans {path.relative_to(ROOT)}")
