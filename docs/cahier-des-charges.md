# Cahier des charges : le score de défaut (fil rouge)

Six lignes, écrites après la séance 1, modifiées par pull request à chaque fois que le projet change d'avis.
L'historique de ce fichier raconte comment le cadrage a évolué.

| Ligne | Réponse |
|---|---|
| **La décision servie** | Un analyste crédit décide, pour chaque client, d'accorder, de refuser ou de revoir à la main le renouvellement de sa ligne de crédit le mois prochain. |
| **La cible** | `default` : 1 si le client n'a pas payé l'échéance d'octobre 2005. Une trace datée, pas « le client est risqué ». |
| **La métrique** | Pour le comité : le coût attendu par dossier en euros au seuil choisi. Pour l'ingénieur : AUC, log-loss, Brier, courbe de calibration. |
| **Les données** | UCI « Default of Credit Card Clients », 30 000 clients, 23 variables d'avril à septembre 2005, CC BY 4.0. Pas de variable postérieure à la cible : carte des fuites vide. |
| **Les garde-fous** | `SEX` exclue (directive 2004/113/CE). `MARRIAGE` autorisée, audit d'équité au jalon 2. Score de crédit de personnes physiques : système à haut risque au sens de l'AI Act, annexe III, point 5 b. Le seuil est une décision métier écrite, pas une sortie du modèle. |
| **Les livrables** | Ce dépôt : `make reproduce` et `make compare`, cinq tests, CI, `metrics.json`, `compare.json`, `DECISIONS.md`, fiche de modèle, fiche de données, plan de surveillance, mémo client, interface. |

## Ce que le projet ne fait pas

- Il ne fixe pas le montant de la ligne de crédit, seulement la décision de renouvellement.
- Il ne remplace pas l'analyste : il trie les dossiers et motive une revue manuelle.
- Il ne s'applique pas à d'autres pays ni à d'autres années sans réentraînement : les données ont vingt ans.

## Les questions posées au commanditaire (réponses supposées, à confirmer)

1. Que coûte un bon client refusé ? Réponse retenue : 600 € de marge perdue (`config.yaml`).
2. Que coûte un défaut accepté ? Réponse retenue : 4 500 € de perte attendue.
3. Combien de dossiers peut-on revoir à la main par mois ? Pas encore répondu : conditionne la zone « revoir ».
