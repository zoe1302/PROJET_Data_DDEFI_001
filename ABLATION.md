# Étude d'ablation (jalon 1)

Pré-enregistrement d'abord, calcul ensuite. Vous écrivez vos prédictions dans une issue du dépôt (horodatée), puis seulement vous lancez le calcul et vous remplissez ce tableau.

Lien de l'issue de pré-enregistrement : [à coller]

| Groupe retiré | AUC prédite | AUC mesurée (validation) | Écart | Commentaire |
|---|---|---|---|---|
| Statuts de retard (`PAY_0` à `PAY_6`) | | | | |
| Montants facturés (`BILL_AMT1` à `6`) | | | | |
| Montants payés (`PAY_AMT1` à `6`) | | | | |
| Plafond (`LIMIT_BAL`) | | | | |
| Profil (`AGE`, `EDUCATION`, `MARRIAGE`) | | | | |

Règle : une ablation se fait en réentraînant le Pipeline sans le groupe, sur le même pli d'entraînement, et en mesurant sur la même validation. Pas en mettant les colonnes à zéro.
