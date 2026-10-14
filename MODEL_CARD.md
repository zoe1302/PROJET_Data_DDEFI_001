# Fiche de modèle (model card)

D'après Mitchell et al. (2019), « Model Cards for Model Reporting ». Version 1 : le modèle de référence. Version 2 au jalon 2, avec l'audit d'équité.

| | |
|---|---|
| Modèle | Régression logistique sur un Pipeline (standardisation, indicatrices), calibration de Platt sur la validation |
| Usage prévu | Trier les demandes de renouvellement d'une ligne de crédit ; motiver une revue manuelle |
| Usage exclu | Décision automatique sans revue ; tout autre pays, toute autre année ; fixer un montant |
| Données d'entraînement | 18 000 clients (pli `train`), coupe figée, graine 20261015 |
| Variables | 21 colonnes, `SEX` exclue, `ID` exclue |
| Métriques sur la validation (6 000 clients) | voir `metrics.json` : AUC, log-loss, Brier, coût attendu au seuil 0,1176 |
| Seuil | 0,1176, seuil d'indifférence pour c_fp = 600 €, c_fn = 4 500 € |
| Limites connues | Trie mal les bas risques (courbe de coût plate) ; calibrée sur la validation, donc métriques de validation optimistes |
| Équité | À faire au jalon 2 : taux de refus, taux de faux positifs et taux de vrais positifs par `MARRIAGE` et par tranche d'`AGE` |
| Surveillance | À faire au jalon 3 : `MONITORING.md` (PSI par variable, dérive de la cible, alarme) |
