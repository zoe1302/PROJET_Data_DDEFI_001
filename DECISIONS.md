# Journal des décisions

Une entrée par décision, datée, avec l'alternative rejetée et la raison. L'équipe qui vous audite lit ce fichier avant le code.
Une décision sans alternative n'est pas une décision, c'est un constat.

## 2026-10-14 · Cible : le défaut d'octobre, tel quel

- Décision : la colonne `default payment next month` du jeu UCI est la cible, renommée `default`, sans retraitement.
- Alternative rejetée : construire une cible « défaut dans les trois mois » à partir des statuts de retard. Impossible : on n'a qu'un mois après la fenêtre d'observation.
- Preuve : `src/credit/data.py`, contrat de schéma ; `tests/test_data.py`.

## 2026-10-14 · Coupe 60 / 20 / 20, stratifiée, graine 20261015

- Décision : deux coupes stratifiées successives ; le test ne se lit qu'une fois, au jalon 2.
- Alternative rejetée : validation croisée seule, sans test figé. Rejetée parce qu'on veut un chiffre final que personne n'a vu pendant le développement.
- Preuve : `make split` écrit `data/processed/hashes.txt` ; `tests/test_split.py` fige les empreintes.

## 2026-10-14 · SEX exclue, MARRIAGE gardée avec audit

- Décision : `SEX` n'entre dans aucun modèle. `MARRIAGE` entre, et son effet sera audité au jalon 2 (parité des taux de refus, égalité des chances).
- Alternative rejetée : garder `SEX` « parce que le modèle est meilleur ». Rejetée : garde-fou juridique, pas un choix de performance.
- Preuve : `config.yaml`, `excluded_features` ; `split_xy` refuse les colonnes interdites.

## 2026-10-14 · Coûts : 600 € le refus à tort, 4 500 € le défaut accepté

- Décision : deux hypothèses métier, écrites dans `config.yaml`, pas sorties du modèle.
- Alternative rejetée : pondérer les classes dans la logistique (`class_weight`). Rejetée : cela rend les probabilités fausses ; on garde des probabilités calibrées et on déplace le seuil.
- À faire : confirmer les deux montants avec le commanditaire avant le jalon 1.

## 2026-10-14 · Seuil 0,1176, le seuil d'indifférence, pas 0,5

- Décision : avec des probabilités calibrées, le seuil qui minimise le coût attendu vaut c_fp / (c_fp + c_fn) = 600 / 5 100 = 0,1176. On l'écrit dans `config.yaml`.
- Constat à garder en tête : sur la validation, l'argmin empirique de C(t) tombe à 0,045, et la courbe est plate entre 0,04 et 0,15 : le modèle de référence trie mal les bas risques, et refuser presque tout le monde coûte autant que suivre le modèle (467 € contre 469 € par dossier). C'est la preuve chiffrée qu'il faut un meilleur modèle, pas un meilleur seuil.
- Alternative rejetée : prendre l'argmin empirique. Rejetée tant que le modèle n'est pas meilleur : le seuil théorique est celui qu'on sait défendre.
- Preuve : `make metrics` imprime les deux valeurs ; `metrics.json`, clé `seuil_optimal_validation`.

## 2026-10-14 · Calibration de Platt sur la validation

- Décision : la logistique est calibrée par une sigmoïde ajustée sur le pli de validation.
- Conséquence assumée : la validation sert à calibrer et à choisir le seuil, donc les métriques de validation sont légèrement optimistes. Le test tranchera une fois.
- Alternative rejetée : calibration isotonique. Rejetée pour l'instant : plus souple, mais elle demande plus de données et casse la monotonie lisible d'une logistique.

## À écrire avant `make compare` (jalon 2)

- **Règle du champion** : [quel modèle gagne, sur quelle métrique, avec quel intervalle, et ce qu'on fait en cas d'égalité]. Tant que ce titre n'est pas écrit ici, `make compare` refuse de tourner.
