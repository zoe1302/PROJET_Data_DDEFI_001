# Les branches, les pull requests, les tags : comment on travaille à plusieurs

Ce fichier est arrivé dans le dépôt par une pull request, depuis la branche `structure-du-projet`.
Regardez l'onglet **Pull requests** (fermées) et **Insights → Network** : vous verrez la branche
partir de `main`, recevoir ses commits, et y revenir. C'est le cycle que vous répéterez cent fois.

## L'idée en une phrase

`main` est la version qui marche. On ne travaille jamais dessus directement : on part d'une
branche, on y fait une tâche, on la fait relire, on la fusionne. Si la tâche échoue, on jette la
branche et `main` n'a rien vu.

```
main      ●────────●───────────────●──────────●──────→   (toujours vert : make reproduce, make test)
           \                      /            \
docs/branches ●──●──●──(pull request)           \
                                                  \
tests/robustesse                                   ●──●──(pull request)──→ main
```

## Le cycle, commande par commande

```bash
git switch main && git pull                 # 1. partir de la dernière version de main
git switch -c features/ablation-pay         # 2. une branche par tâche, nommée par ce qu'elle fait
# ... vous modifiez des fichiers ...
git status                                  # 3. voir ce qui a changé
git add src/credit/features.py tests/       # 4. choisir ce qui entre dans le commit
git commit -m "Ablation : retirer les statuts de retard, mesurer l'AUC"   # 5. un message qui dit quoi et pourquoi
git push -u origin features/ablation-pay    # 6. envoyer la branche sur GitHub
```

Puis, sur GitHub : **Compare & pull request** → un titre, trois lignes (ce que ça change, comment
vérifier, ce qui reste), et un relecteur de l'équipe dans **Reviewers**. Le relecteur lit le diff,
lance `make test` chez lui, commente, puis **Approve** et **Merge pull request** (merge commit, pas
squash : on garde l'histoire). Ensuite **Delete branch**, et chacun fait `git switch main && git pull`.

## Les règles de l'équipe

| Règle | Pourquoi |
|---|---|
| Une branche = une tâche, courte (un à trois jours) | une branche qui vit deux semaines ne se fusionne plus sans conflit |
| Personne ne pousse sur `main` | la CI tourne sur chaque pull request : `main` reste vert |
| Une pull request est relue par quelqu'un d'autre | c'est la revue croisée du barème, et c'est ce qui attrape les fuites |
| Un commit par idée, un message au présent qui dit quoi et pourquoi | `git log` devient le journal du projet |
| Jamais de données, de modèles entraînés ni de secrets dans un commit | `.gitignore` les refuse ; un jeton poussé est volé en minutes |
| Les notebooks sont commités sans leurs sorties | sinon chaque commit pèse des mégaoctets et le diff est illisible |

## Les conflits

Deux personnes modifient la même ligne sur deux branches : à la fusion, Git s'arrête et marque le
fichier.

```
<<<<<<< HEAD
threshold: 0.1176
=======
threshold: 0.12
>>>>>>> features/seuil
```

On ouvre le fichier, on garde la bonne version (ou une troisième), on enlève les marqueurs, puis
`git add` et `git commit`. Un conflit n'est pas une panne : c'est deux décisions à réconcilier, et
la bonne réponse est souvent dans `DECISIONS.md`.

## Les tags : marquer un rendu

Le rendu d'un jalon, c'est l'état du dépôt à l'heure limite : le dernier commit poussé sur `main`
fait foi. Le tag est conseillé parce qu'il donne un nom à ce moment :

```bash
git switch main && git pull
git tag jalon-1 && git push origin jalon-1
```

Ou sur GitHub : **Releases → Draft a new release → Create new tag** `jalon-1` → **Publish**.
Ensuite, n'importe qui retrouve exactement cette version : `git switch --detach jalon-1`.

## Le cycle quotidien, en trente secondes

Matin : `git switch main && git pull`, puis sa branche. Journée : des commits petits et fréquents.
Soir : `git push`, même si ce n'est pas fini (un travail qui n'est que sur votre portable n'existe
pas). Avant la pull request : `make test` et `make reproduce` chez vous.

## Ce qu'on ne fait pas

- `git add .` sans regarder `git status` : c'est comme ça qu'un `kaggle.json` finit sur GitHub.
- `git push --force` sur une branche partagée : vous effacez le travail des autres.
- Résoudre un conflit en recopiant « sa » version sans lire l'autre.
- Attendre la veille du jalon pour fusionner trois semaines de travail.

## Pour aller plus loin

Le deck « Outils » du cours (Git au quotidien), et le cours ecofinlearning.com, leçon
« Git et GitHub : push », pour refaire le cycle sur un dépôt d'essai.
