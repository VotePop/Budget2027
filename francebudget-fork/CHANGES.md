# Modifications apportées à ce fork (AGPL-3.0)

Ce dépôt est un fork de [cturkieh/france-budget-simulateur](https://github.com/cturkieh/france-budget-simulateur)
(licence AGPL-3.0, auteur Cyril Turkieh). Conformément à l'article 5 de l'AGPL-3.0,
les modifications apportées par rapport au dépôt d'origine sont documentées ici,
avec la date de fork.

**Date du fork : 30 septembre 2026.**
**Commit amont forké : `6c804e040cfb7426d9f4ca1dee17a549153c76f0` (2026-08-31).**

Aucun fichier du moteur original (`budget_simulator/handlers/`, `budget_simulator/engine/`,
`budget_simulator/simulator.py`, `budget_simulator/constants.py`, `policy_measures.json`,
`docs/`, `tests/` d'origine) n'a été modifié. Tous les ajouts sont dans des
fichiers NOUVEAUX, listés ci-dessous, pour que le diff avec l'amont reste trivial
à auditer et qu'un `git pull` depuis l'amont reste possible sans conflit.

## Fichiers ajoutés

- **`budget_simulator/decile.py`** — module de ventilation par décile de niveau
  de vie. Réutilise tel quel le delta Md€ net que chaque handler du moteur
  original calcule déjà (exposé par `report['measure_impacts_by_year']`), et le
  répartit selon des clés de décile sourcées séparément (CPO/Boutchenik 2015,
  DG Trésor Trésor-Éco n°371 2025, DREES, Insee — mêmes sources que le classeur
  `Simulateur_Impact_Menages.xlsx` d'un projet compagnon). Aucune mesure sans
  clé sourcée de notre côté n'est ventilée par une hypothèse inventée — elle
  apparaît dans `mesures_non_ventilees`.
- **`tests/test_decile_ajout.py`** — 6 tests couvrant `decile.py` (sommes à
  100%, ventilation correcte, non-invention pour les mesures non couvertes,
  agrégation multi-mesures, cas vide).
- **`api.py`** (modifié, ajout uniquement — aucune route existante changée) :
  nouvel endpoint `POST /simulate_decile`, qui appelle le moteur exactement
  comme `POST /simulate` puis ajoute le champ `decile` à la réponse. Route
  `GET /ui/` montée en fin de fichier (fichiers statiques `frontend/`), après
  toutes les routes JSON d'origine — ne change leur comportement en rien.
- **`frontend/index.html`** — interface web à page unique (HTML/CSS/JS vanilla,
  aucune dépendance externe) : sliders pour 9 leviers, indicateurs macro
  (déficit/PIB, dette/PIB, croissance, chômage) et graphique en barres de la
  ventilation par décile, avec tableau des sources par mesure.
- **`Dockerfile`, `DEPLOY.md`** — packaging de déploiement (voir `DEPLOY.md`).
- **Ce fichier, `CHANGES.md`.**

## Obligation AGPL §13 (network use) — À FAIRE avant toute mise en ligne publique

Ce fork n'est PAS encore publié sur un dépôt public. **Avant de déployer cette
version sur un site accessible à des tiers**, l'opérateur du service DOIT :

1. Publier ce dépôt (avec ses modifications) sur une plateforme accessible
   publiquement (GitHub, GitLab...), en conservant la licence AGPL-3.0.
2. Faire pointer un lien "Code source" visible dans l'interface (`frontend/index.html`)
   vers ce dépôt public, pour que tout visiteur du site puisse récupérer le
   code exact qui tourne (obligation légale de l'AGPL §13, pas une simple
   bonne pratique).

Tant que ces deux étapes ne sont pas faites, le service ne doit être exposé
qu'en usage privé/local (pas de mise en ligne publique).
