# PROJET_Data_DDEFI_001
Groupe 

---

# Le gabarit du cours : score de défaut (fil rouge)

Prédit, pour chaque client d'une banque, la probabilité qu'il fasse défaut le mois prochain,
pour aider un analyste crédit à décider : accorder, refuser, ou revoir à la main.

Données : « Default of Credit Card Clients » (UCI, 30 000 clients taïwanais, 2005, licence CC BY 4.0).
Elles ne sont pas dans le dépôt : un script les télécharge et vérifie leur empreinte.

## Lancer

```bash
python -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.lock
make reproduce        # télécharge, coupe, entraîne, mesure : metrics.json
make test             # les cinq tests, moins d'une minute
```

`make reproduce` doit donner deux fois les mêmes chiffres, chez vous et chez l'équipe qui vous audite.
Si ce n'est pas le cas, l'un des quatre a bougé : données, code, graine, environnement.

## Où est quoi

| Dossier | Contenu |
|---|---|
| `docs/cahier-des-charges.md` | la décision servie, en six lignes ; modifié par pull request |
| `docs/git-branches.md` | comment on travaille à plusieurs : branches, pull requests, revue, conflits, tags |
| `DECISIONS.md` | le journal : une entrée datée par décision, avec l'alternative rejetée |
| `data/README.md` | l'origine des données, la licence, l'empreinte SHA-256 |
| `src/credit/` | le code qui compte : `data`, `split`, `features`, `model`, `evaluate`, `compare` |
| `batch/` | les scripts de traitement par lots : préparer, entraîner, prédire, évaluer |
| `notebooks/` | `00_guide.ipynb` (ce qui est à faire et ce qu'il ne faut pas faire), `01_exploration.ipynb`, `02_pourquoi-et-robustesse.ipynb` |
| `tests/` | treize tests : contrat de schéma, coupe figée, propriétés du modèle, robustesse |
| `app/` | une interface minimale : on entre un client, le modèle répond |
| `config.yaml` | la graine, les coûts d'erreur, le seuil |
| `metrics.json`, `compare.json` | ce que `make reproduce` et `make compare` produisent |

## Les trois modèles

| Niveau | Modèle | Où | Quand |
|---|---|---|---|
| naïf | le taux de base, 22,1 % pour tout le monde | `credit.model.naive` | fourni |
| meilleur | régression logistique calibrée, seuillée par les coûts | `credit.model.train` | fourni, à défendre au jalon 1 |
| lourd | gradient boosting (XGBoost) comparé honnêtement | `credit.model.heavy` | **à vous**, jalon 2 |

Le modèle lourd n'est pas écrit : la fonction existe et vous dit quoi faire. C'est le travail du jalon 2.

## Pourquoi un modèle, et comment on sait qu'il tient

Avant tout machine learning, une banque refuse déjà les clients en retard. Le modèle doit faire mieux que cette règle, en euros, et le prouver. Sur la validation, avec un refus à tort à 600 € :

| Coût d'un défaut accepté | Meilleure règle métier (PAY_0 ≥ 1) | Logistique au meilleur seuil |
|---|---|---|
| 600 € | 133 € par dossier | 112 € |
| 1 500 € | 227 € | 226 € |
| 4 500 € (config.yaml) | 541 €, mais « refuser tout le monde » fait 467 € | 460 € |

Le modèle bat la règle à chaque niveau de coût, de peu ; à 4 500 €, il fait à peine mieux que refuser tout le monde. **L'intérêt d'un modèle dépend des coûts d'erreur** : c'est au comité de les donner, et c'est au jalon 2 de faire mieux. Le détail, avec l'intervalle de confiance de l'AUC et six tests de robustesse (bruit, monotonie, valeurs absurdes, rééchantillonnage, tranches, dérive), est dans `notebooks/02_pourquoi-et-robustesse.ipynb` et `tests/test_robustness.py`.

## Règles du dépôt

- Les notebooks importent `src/credit`, ils ne le recopient pas.
- Tout ce qui est appris (moyennes, coefficients, seuil) l'est sur le pli d'entraînement, jamais sur le jeu entier.
- Le jeu de test ne se lit qu'une fois, à `make compare`, quand la règle du champion est écrite dans `DECISIONS.md`.
- La variable `SEX` n'entre pas dans le modèle (garde-fou, directive 2004/113/CE) ; `MARRIAGE` est autorisée avec audit d'équité.
- L'IA peut écrire du code ici ; à l'oral, vous devez pouvoir expliquer chaque ligne.

## Licence

Code : MIT. Données : CC BY 4.0, Yeh et Lien (2009), UCI Machine Learning Repository.
