"""Les données : téléchargement, empreinte, chargement, contrat de schéma.

Source : Yeh, I-Cheng et Lien, Che-hui (2009), « Default of Credit Card Clients »,
UCI Machine Learning Repository, https://doi.org/10.24432/C55S3H, licence CC BY 4.0.
30 000 clients d'une banque taïwanaise, avril à septembre 2005. La cible vaut 1 si le client
fait défaut le mois suivant (octobre 2005).

Attention : les données brutes ne sont jamais versionnées. On versionne leur empreinte SHA-256
(data/sha256.txt) : si le fichier change, make reproduce s'arrête et le dit.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

from credit.config import ROOT

URL = "https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip"
RAW_DIR = ROOT / "data" / "raw"
RAW_XLS = RAW_DIR / "default of credit card clients.xls"
RAW_CSV = RAW_DIR / "credit.csv"
TARGET = "default"

# Le contrat de schéma : ce que les données doivent respecter pour que le reste tourne.
# Un test l'applique (tests/test_data.py). Si une borne tombe, on cherche pourquoi avant de modéliser.
SCHEMA = {
    "n_rows": 30_000,
    "columns": [
        "ID", "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE",
        "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
        "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
        "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
        TARGET,
    ],
}


def sha256(path: Path) -> str:
    """L'empreinte d'un fichier, lue par blocs pour ne pas charger un gros fichier en mémoire."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(force: bool = False) -> Path:
    """Télécharge l'archive UCI et écrit data/raw/credit.csv. Ne refait rien si le CSV existe déjà."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if RAW_CSV.exists() and not force:
        return RAW_CSV
    print(f"Téléchargement de {URL}")
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        name = next(n for n in z.namelist() if n.endswith(".xls"))
        RAW_XLS.write_bytes(z.read(name))
    # Le fichier Excel a une ligne de titre au-dessus des en-têtes : header=1.
    df = pd.read_excel(RAW_XLS, header=1)
    df = df.rename(columns={"default payment next month": TARGET})
    df.to_csv(RAW_CSV, index=False)
    return RAW_CSV


def load_raw() -> pd.DataFrame:
    """Charge le CSV brut (le télécharge s'il manque) et vérifie le contrat de schéma."""
    path = download()
    df = pd.read_csv(path)
    check_schema(df)
    return df


def check_schema(df: pd.DataFrame) -> None:
    """Le contrat de schéma : colonnes, nombre de lignes, bornes, cible binaire, manquants."""
    missing = [c for c in SCHEMA["columns"] if c not in df.columns]
    if missing:
        raise ValueError(f"colonnes manquantes : {missing}")
    if len(df) != SCHEMA["n_rows"]:
        raise ValueError(f"{len(df)} lignes au lieu de {SCHEMA['n_rows']}")
    if (df["LIMIT_BAL"] <= 0).any():
        raise ValueError("LIMIT_BAL doit être strictement positif")
    if not df[TARGET].isin([0, 1]).all():
        raise ValueError("la cible doit valoir 0 ou 1")
    if df.isna().mean().max() >= 0.05:
        raise ValueError("plus de 5 % de valeurs manquantes dans une colonne")


def check_hash(expected_file: Path) -> None:
    """Compare l'empreinte du CSV à celle attendue ; écrit le fichier d'empreinte s'il n'existe pas."""
    path = download()
    actual = sha256(path)
    if not expected_file.exists():
        expected_file.write_text(actual + "\n", encoding="utf-8")
        print(f"Empreinte écrite dans {expected_file.relative_to(ROOT)} : {actual[:12]}…")
        return
    expected = expected_file.read_text(encoding="utf-8").strip()
    if actual != expected:
        raise SystemExit(
            "Les données ont changé : l'empreinte ne correspond pas à data/sha256.txt.\n"
            f"  attendue : {expected}\n  obtenue  : {actual}\n"
            "Ne modifiez pas l'empreinte sans écrire pourquoi dans DECISIONS.md."
        )
    print(f"Données vérifiées : {path.relative_to(ROOT)}, empreinte {actual[:12]}… conforme.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Télécharge les données UCI et vérifie leur empreinte.")
    p.add_argument("--check", type=Path, default=ROOT / "data" / "sha256.txt", help="fichier d'empreinte attendue")
    p.add_argument("--force", action="store_true", help="retélécharge même si le CSV existe")
    a = p.parse_args()
    if a.force:
        download(force=True)
    check_hash(a.check)
    check_schema(pd.read_csv(RAW_CSV))
