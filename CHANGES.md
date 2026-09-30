# Modifications apportées à ce fork (AGPL-3.0)

Ce dépôt est un fork de [cturkieh/france-budget-simulateur](https://github.com/cturkieh/france-budget-simulateur)
(licence AGPL-3.0, auteur Cyril Turkieh). Conformément à l'article 5 de l'AGPL-3.0,
les modifications apportées par rapport au dépôt d'origine sont documentées ici,
avec la date de fork.

**Date du fork : 30 septembre 2026.**
**Commit amont forké : `6c804e040cfb7426d9f4ca1dee17a549153c76f0` (2026-08-31).**

Jusqu'au 2026-09-30, aucun fichier du moteur original (`budget_simulator/handlers/`,
`budget_simulator/engine/`, `budget_simulator/simulator.py`, `budget_simulator/constants.py`,
`policy_measures.json`, `docs/`, `tests/` d'origine) n'avait été modifié — tous les ajouts
étaient dans des fichiers NOUVEAUX, listés ci-dessous, pour que le diff avec l'amont reste
trivial à auditer et qu'un `git pull` depuis l'amont reste possible sans conflit. Une
modification d'un fichier original a depuis eu lieu (voir "Modifications du moteur original"
ci-dessous) ; le reste de cette section décrit les ajouts.

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

## Modifications du moteur original

Conformément à l'article 5 de l'AGPL-3.0 (obligation de signaler les fichiers modifiés
et la date), les modifications suivantes ont été apportées à des fichiers du dépôt
original (par opposition aux ajouts listés ci-dessus, dans des fichiers nouveaux) :

- **2026-09-30 — `budget_simulator/handlers/investissements.py`** (mesure
  `transition_ecologique`, sous-paramètre `taxe_carbone`) : recalibrage du rendement de la
  composante carbone. L'ancienne formule (`(carbon_tax - référence) * 0.06`, soit ~6 Md€ pour
  +100 €/tCO2) ne portait aucune source identifiable dans l'historique du fichier et
  sous-évaluait l'assiette réelle d'un facteur ~3,3. Nouveau calcul, entièrement sourcé
  FIPECO ("Les taxes sur les carburants", fiche IV.18, 06.07.2026) + OCDE/Wikipédia (rendement
  2018 de la composante carbone) : assiette physique ≈ 195,7 MtCO2 (dérivée du rendement 2018
  et de l'évolution 2019→2025 du rendement total de l'accise en comptabilité nationale, le
  taux étant gelé depuis 2018), avec un effet-volume comportemental (élasticité-prix long
  terme 0,6-0,7, FIPECO citant Économie et Statistique 2011) qui atténue le rendement marginal
  net à mesure que le curseur s'écarte du statu quo. Voir les commentaires en tête du bloc
  "RECETTES TAXE CARBONE" dans le fichier pour le détail de la chaîne de calcul et les sources
  précises. Seule la formule de recettes a changé ; les canaux Gini/pouvoir d'achat/
  compétitivité de cette mesure (déjà sourcés Douenne 2020, IPP note 34, CAE 2023/CBAM)
  n'ont pas été touchés.
- **2026-09-30 — `tests/test_carbon_tax_abrogation.py`** : la sonde de test lisait un delta
  de recettes via une colonne d'affichage arrondie à 1 décimale (`Recettes/PIB % × PIB`), ce
  qui produisait un faux positif de "discontinuité" avec le nouveau coefficient (plus grand)
  ci-dessus. Remplacée par une lecture directe et non arrondie du delta calculé par le handler
  (`measure_impacts_by_year`), conformément à l'intention déjà documentée dans ce fichier de
  test ("sonde directe").

## Obligation AGPL §13 (network use)

1. **Fait** — dépôt public créé : https://github.com/VotePop/Budget2027
   (conserve la licence AGPL-3.0).
2. **Fait** — le lien "Code source" dans l'interface (`frontend/index.html`)
   pointe vers ce dépôt public, pour que tout visiteur du site puisse
   récupérer le code exact qui tourne (obligation légale de l'AGPL §13, pas
   une simple bonne pratique).

Reste à faire avant toute mise en ligne publique : pousser réellement l'état
courant du code (avec ces deux ajustements) sur ce dépôt, et vérifier qu'il y
reste synchronisé à chaque mise à jour du service déployé — un lien qui pointe
vers un dépôt qui ne reflète plus le code en production ne satisfait pas
l'obligation.
