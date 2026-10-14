"""Une interface minimale : on entre un client, le modèle répond.

    make app      (ou : streamlit run app/app.py)

Attention : l'interface ne contient aucune logique métier. Elle charge le même Pipeline que le
batch et applique le même seuil que config.yaml. Si vous modifiez un calcul ici, il diverge du
reste du projet sans que personne ne s'en aperçoive.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from credit.config import load_config  # noqa: E402
from credit.features import feature_columns  # noqa: E402
from credit.model import load_model  # noqa: E402

cfg = load_config()
st.title("Score de défaut : un client, une décision")
st.caption("Régression logistique calibrée, seuil fixé par les coûts d'erreur de config.yaml.")

cols = feature_columns(cfg)
defaults = {"LIMIT_BAL": 50_000, "AGE": 35, "EDUCATION": 2, "MARRIAGE": 2}
values = {}
c1, c2, c3 = st.columns(3)
for i, c in enumerate(cols):
    col = (c1, c2, c3)[i % 3]
    if c in ("EDUCATION", "MARRIAGE"):
        values[c] = col.selectbox(c, [1, 2, 3, 4, 5, 6, 0], index=[1, 2, 3, 4, 5, 6, 0].index(defaults[c]))
    elif c.startswith("PAY_") and not c.startswith("PAY_AMT"):
        values[c] = col.slider(c, -2, 8, 0)
    else:
        values[c] = col.number_input(c, value=float(defaults.get(c, 0)), step=1000.0 if "AMT" in c or c == "LIMIT_BAL" else 1.0)

if st.button("Scorer ce client"):
    try:
        model = load_model("baseline")
    except FileNotFoundError:
        st.error("Aucun modèle entraîné : lancez make reproduce.")
    else:
        p = float(model.predict_proba(pd.DataFrame([values])[cols])[:, 1][0])
        t = cfg["threshold"]
        st.metric("Probabilité de défaut", f"{p:.1%}")
        st.write("Décision au seuil", t, ":", "**refuser**" if p >= t else "**accorder**")
        st.caption(f"Coûts : {cfg['costs']['c_fp']} € un refus à tort, {cfg['costs']['c_fn']} € un défaut accepté.")
