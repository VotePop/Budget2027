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
- **`budget_simulator/ventilation_taille.py`** — module de ventilation par
  taille d'entreprise (microentreprises/MIC, PME, ETI, grandes entreprises/GE),
  même principe que `decile.py` ci-dessus : reprend tel quel le delta Md€ net
  déjà calculé par les handlers pour chaque mesure (`measure_impacts_by_year`),
  sans rien recalculer, et le ventile par catégorie d'entreprise selon deux
  types de clés, toutes deux sourcées ou justifiées, jamais inventées :
  - **`impot_societes`** : clé sourcée INSEE Références, « Les entreprises en
    France », édition décembre 2023 (données DGFiP, IS brut par catégorie
    d'entreprise, 2021) : microentreprises 12,4 Md€ (17,4 %), PME hors
    microentreprises 18,6 Md€ (26,1 %), ETI 16,7 Md€ (23,5 %), grandes
    entreprises 23,5 Md€ (33,0 %), total 71,2 Md€.
  - **`niches_fiscales_tge`, `niches_sociales_tge`, `subventions_tge`,
    `is_exceptionnel_tge`** : ventilées à 100 % sur « GE ». Ce n'est pas une
    hypothèse ajoutée par ce module : ces 4 mesures sont déjà définies, par
    leur propre docstring/logique dans le moteur d'origine
    (`budget_simulator/handlers/competitivite.py`), comme ne concernant QUE
    les très grandes entreprises (« TGE », ~15 000 entreprises) — on reprend
    ici le périmètre déjà fixé par le moteur, sans le modifier.
  - **Mesures explicitement laissées "non ventilées"** : `cotisations_patronales`,
    `impots_production`, `taxe_superprofits`, `exonerations_salaires`. Les seules
    publications trouvées pour ces mesures (DGFiP Statistiques n°35, 2025,
    « Les impôts de production en 2023 ») ne donnent que des ÉVOLUTIONS en
    points de valeur ajoutée par catégorie d'entreprise, pas de montant ou de
    part du total en niveau — insuffisant pour ventiler un delta Md€ sans
    inventer une clé. Idem pour la page INSEE « Vision globale sur la
    fiscalité directe portant sur les entreprises », qui ventile par type
    d'assiette (résultats/capital/masse salariale/CA), pas par taille
    d'entreprise. Ces mesures apparaissent dans `mesures_non_ventilees`
    plutôt que de recevoir une hypothèse inventée — même discipline que
    `decile.py` pour les ménages.
- **`api.py`** (modifié, ajout uniquement — aucune route existante changée) :
  nouvel endpoint `POST /simulate_decile`, qui appelle le moteur exactement
  comme `POST /simulate` puis ajoute le champ `decile` à la réponse. Route
  `GET /ui/` montée en fin de fichier (fichiers statiques `frontend/`), après
  toutes les routes JSON d'origine — ne change leur comportement en rien.
  **2026-09-30** : `/simulate_decile` renvoie désormais aussi le champ
  `measure_impacts` (détail recettes/dépenses par mesure et par année, issu
  de `report['measure_impacts_by_year']`), nécessaire à la maquette
  `frontend/mockup_fiscalite.html` pour afficher l'effet de chaque levier
  directement sur sa carte (et pas seulement sur les indicateurs macro
  globaux). **2026-09-30 (2)** : `/simulate_decile` renvoie aussi le champ
  `ventilation_taille` (sortie de `budget_simulator.ventilation_taille`,
  détaillée ci-dessus), pour le bloc « Compétitivité » de la maquette.
- **`frontend/mockup_fiscalite.html`** — maquette de travail (thématique « Fiscalité »
  uniquement) pour valider un nouveau design avant refonte complète de `frontend/index.html` :
  leviers en entonnoir (principaux visibles, fins repliés dans la carte), chiffrage fusionné
  « aujourd'hui / avec ce réglage », comparaison permanente scénario vs budget de l'État.
  **2026-09-30** : ajout de 3 blocs synthétiques en tête de page (en plus des indicateurs
  déficit/dette/chômage déjà présents) : (1) détail PIB/recettes/dépenses, repliable ; (2)
  indice « Pouvoir d'achat » (champ `Pouvoir d'Achat` déjà calculé par le moteur, canal
  `pouvoir_achat` de chaque handler — jusqu'ici calculé mais jamais affiché) accompagné d'une
  ventilation €/mois/ménage par décile, obtenue en reprenant le delta Md€ déjà ventilé par
  `decile.py` (clés sourcées CPO/Boutchenik 2015, DG Trésor Trésor-Éco n°371 2025, DREES/ACOSS),
  en le divisant par 1/10e du nombre total de ménages en France — **31 274 741 ménages** (INSEE,
  dossier complet France, données 2023) — puis par 12 pour un montant mensuel. Approximation
  assumée et documentée dans le code : les déciles de niveau de vie sont construits sur la
  population (unités de consommation), pas sur un découpage strict de ménages égaux, donc ce
  chiffre €/mois est un ordre de grandeur, pas une identité exacte. **2026-09-30 (v2)** :
  passage de la ventilation décile d'un graphique en barres à une liste (une ligne par décile),
  chaque ligne affichant la tranche de niveau de vie mensuel correspondante pour que chacun
  puisse se situer — seuils D1 à D9 sourcés INSEE, « Niveau de vie et pauvreté en 2024 » (Insee
  Première n°2117) / indicateur « Distribution des niveaux de vie », données 2024, seuils
  annuels convertis en €/mois (÷12, arrondis à la dizaine) ; (3) indice « Compétitivité » (champ
  `Competitivite`, même principe). **2026-09-30 (3)** : la ventilation par taille d'entreprise
  (TPE/PME/ETI/GE) du bloc Compétitivité, jusqu'ici en attente, est maintenant affichée —
  voir `budget_simulator/ventilation_taille.py` ci-dessus pour le détail des sources et des
  mesures volontairement laissées "non ventilées". **2026-09-30 (4)** : affichage en part de
  l'effort net total (%) plutôt qu'en Md€ par catégorie, un montant en Md€ n'étant pas parlant
  pour la plupart des lecteurs ; le Md€ total reste affiché en tête du détail. Avec seulement
  l'IS actif, les pourcentages affichés reproduisent directement la clé sourcée INSEE/DGFiP
  (17,4% / 26,1% / 23,5% / 33,0%). **2026-09-30 (5)** : `.cards` (grille des leviers) passe à
  `align-items:start`, même correctif que `.blocks-grid` plus haut — déplier le détail fin d'un
  levier n'étire plus les cartes voisines de la même ligne à sa hauteur. **2026-09-30 (6)** :
  `align-items:start` réglait l'étirement mais laissait un grand vide sous les cartes plus
  courtes de la même ligne (la hauteur de ligne CSS Grid reste calée sur la carte la plus
  haute). `.cards` passe donc de `display:grid` à des colonnes CSS (`columns:300px 3`) : chaque
  carte qui se déplie ne pousse que celles qui la suivent dans SA colonne, sans réserver de
  hauteur de ligne commune aux 3 colonnes. **2026-09-30 (7)** : aération entre cartes (espacement
  22px au lieu de 14px) et ombre portée plus marquée sur `.card`, pour bien distinguer où une
  carte finit et où la suivante commence — problème signalé une fois les cartes rapprochées par
  le passage aux colonnes CSS ci-dessus. **2026-09-30 (8)** : le bloc résumé du haut reste collé
  en haut de l'écran en scrollant (`position:sticky`, déjà en place) — mais devenait trop haut
  une fois les 2 détails (décile + taille) dépliés en même temps (~40% d'un écran), gênant la
  vue sur les cartes leviers pendant qu'on les ajuste. Réduit : typographies/interlignes
  resserrés partout dans les 3 blocs, note "MIC=..." raccourcie (détail complet au survol), et
  surtout la liste des déciles passe de 10 lignes empilées à 2 colonnes de 5 (D1-D5 / D6-D10,
  libellés raccourcis "1160–1480" au lieu de "entre 1160 et 1480 €/mois", plage complète toujours
  disponible au survol) — la hauteur dépliée passe d'environ 40% à ~30% d'un écran de 900px,
  sans perte d'information. **2026-09-30 (9)** : suppression de la ligne de texte "MIC =
  microentreprises. Part de l'effort net total, pas un montant par entreprise (détail ⓘ)." sous
  le détail Compétitivité — non capitale, elle cassait l'alignement en hauteur avec le bloc
  Pouvoir d'achat voisin ; son contenu est repris dans l'attribut `title` (infobulle) du bloc.
  **2026-10 — réorganisation thématique des leviers (validée en chat)** : la section leviers
  passe d'une structure à 2 niveaux ("Leviers principaux" visibles + "Réglages avancés" repliés
  sous un bouton global, 6+6 mesures) à **3 colonnes thématiques fixes** — Ménages / Entreprises
  / Patrimoine — pour aider à la lecture. Chaque ex-mesure "avancée" est désormais rangée, via un
  "+" ambre en tiret, sous la carte du levier principal auquel elle se rattache le mieux : TVA
  Énergie sous Taux de TVA (Ménages) ; Élargissement de la base IR et Abattement fiscal retraités
  sous Impôt sur le revenu (Ménages) ; Taxe sur les superprofits sous Impôt sur les sociétés
  (Entreprises) ; ISF Climatique sous Fiscalité du patrimoine (Patrimoine). Lutte contre la
  fraude fiscale n'a pas de carte parente naturelle : rangée en carte autonome dans la colonne
  Entreprises (décision prise en chat avec l'utilisateur — le gisement visé est majoritairement
  celui des entreprises/hauts revenus ; aucune règle de rangement stricte ne s'y opposait).
  **Point important, documenté dans le code (`THEMES` en tête du `<script>`) et dans l'UI même**
  (texte sous "Leviers fiscaux") : ce "+" ambre ne fusionne PAS la mesure repliée avec la carte
  parente — contrairement à un "+" teal (subParam), qui partage la même mesure budgétaire que sa
  carte (ex. les 3 autres taux de TVA), chaque mesure repliée en ambre garde son propre id de
  mesure moteur, son propre chiffrage "aujourd'hui/avec ce réglage" et son propre delta —
  c'est un rangement de lecture, pas une fusion budgétaire. Vérifié par test manuel (Playwright) :
  déplacer le curseur de TVA Énergie (repliée sous Taux de TVA) met à jour uniquement son propre
  chiffrage (206,6 Md€ → 6,6 Md€ à taux réduit à 5,5%) sans toucher au chiffrage de la carte
  Taux de TVA (reste 211,7 Md€). Techniquement, chaque colonne thématique est maintenant une
  simple pile verticale de cartes (`display:flex; flex-direction:column`) — l'astuce CSS
  `columns:300px 3` utilisée précédemment pour répartir 12 cartes en 3 colonnes équilibrées
  n'est plus nécessaire : chaque thème a maintenant SA PROPRE colonne dédiée, donc déplier une
  carte ne pousse plus que les cartes suivantes dans le même thème, sans jamais affecter les 2
  autres colonnes. Répartition résultante : Ménages 4 cartes principales (TVA, IR, CSG,
  cotisations salariales) + 3 repliées ; Entreprises 2 cartes principales (IS, fraude fiscale)
  + 1 repliée ; Patrimoine 1 carte principale + 1 repliée — déséquilibre assumé (rangement
  thématique, pas symétrie du nombre de cartes). Ce rangement pourra évoluer (accord explicite
  de l'utilisateur) lors de l'ajout, dans une 2e passe, de nouveaux leviers fiscaux sourcés mais
  pas encore implémentés dans le moteur (taxe sur les transactions financières, taxe GAFA/
  services numériques, CDHR, taxe sur les holdings patrimoniales — voir recherche comparative
  avec monbudgetpourlafrance.fr/IPP menée en amont de cette réorganisation).
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
- **2026-09-30 — `budget_simulator/handlers/fiscalite_menages.py`** (mesure `tva_rate`) :
  ajout de 3 nouveaux paramètres pilotables — `taux_intermediaire` (10 %, restauration/
  travaux/transport...), `taux_reduit` (5,5 %, alimentation/livres/énergie...) et
  `taux_particulier` (2,1 %, presse/médicaments remboursables...). Jusqu'ici seul le taux
  normal (`taux`, 20 %) était un levier ; les 3 autres taux officiels de TVA n'avaient
  aucune prise dans le moteur. Le canal recettes de ces 3 nouveaux paramètres est
  volontairement LINÉAIRE (delta = écart en points × rendement net par point), sans
  courbe d'élasticité propre — contrairement au taux normal, qui garde sa modélisation
  historique inchangée. Source du rendement/point : DG Trésor, Trésor-Éco n°371
  (09/2025), « Analyse de la composition des recettes de TVA », tableau 1 (rendement net
  2025, à partir du compte 2022 Insee semi-définitif) : intermédiaire 1,6 Md€/point,
  réduit 2,0 Md€/point, particulier 0,4 Md€/point. Limite assumée et documentée dans le
  code : les canaux Gini/pouvoir d'achat/compétitivité restent calculés uniquement sur le
  taux normal, faute de source distincte par taux pour ces canaux — aucun chiffre n'est
  inventé pour les 3 nouveaux paramètres sur ces canaux. `policy_measures.json` mis à
  jour en cohérence (3 nouvelles entrées `parametres` sous `tva_rate`, avec tooltips
  sourcés) ; `tests/snapshots/measure_registry.json` mis à jour à la main pour le volet
  `params` (le générateur `scripts/generate_measure_registry.py` ne peut pas tourner
  dans ce fork — il attend un `frontend-react/` absent ici, limitation pré-existante
  déjà tolérée par le skip conditionnel de `tests/test_measure_registry_sync.py`).
  Nouveau test dédié : `tests/test_tva_multitaux.py` (6 tests : statu quo, isolation de
  chacun des 3 nouveaux paramètres, additivité, non-régression du taux normal).
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

## 2026-10 — Nouveaux leviers fiscaux (phase 2 après réorganisation thématique)

Ajout de 4 mesures fiscales identifiées lors de la comparaison avec monbudgetpourlafrance.fr/
IPP (voir plus haut) et jugées suffisamment sourcées pour être implémentées dans le moteur.
CVAE (risque de double-comptage avec `impots_production`), Pilier 2/impôt minimum mondial
(rendement trop incertain, absence d'évaluation officielle à jour après l'accord « side-by-side »
janvier 2026) et la taxation du cannabis (hypothèse non actée, source unique CAE 2019) ont été
écartées à ce stade.

**Fichiers ajoutés (fork uniquement, absents du dépôt original) :**
- `budget_simulator/handlers/nouvelles_taxes_2027.py` — 4 handlers, un par mesure ci-dessous.
  Modélisation volontairement simple (loi linéaire autour du rendement actuel/réel constaté,
  sans élasticité comportementale propre sourcée pour ces 4 mesures précises) ; les impacts
  macro secondaires (compétitivité, Gini) sont une extrapolation par analogie avec l'ordre de
  grandeur déjà utilisé pour `taxe_superprofits` dans `additionnels.py` — limite assumée et
  documentée en tête du fichier et dans chaque docstring de handler.

**Mesures ajoutées :**
- **`ttf`** (taxe sur les transactions financières) : taux actuel 0,4% (relevé de 0,3% en avril
  2025) → 2,5 Md€/an ; le relèvement de 0,1pt a généré ~0,5 Md€/an de plus → modèle linéaire
  (500 Md€ de rendement par 100% de taux plein). Source : moneyvox.fr, « Taxe sur les
  transactions financières : quel bilan 15 ans après ? » (2025). Ventilée 100% GE dans
  `ventilation_taille.py` — pas une hypothèse, le périmètre légal (seuil de capitalisation
  boursière ~1 Md€) exclut par construction MIC/PME/ETI.
- **`taxe_gafa`** (taxe sur les services numériques) : taux actuel 3%, seuil CA mondial 750 M€
  → 0,7 Md€/an (2024). Un amendement PLF 2026 (adopté par l'Assemblée nationale le 28/10/2025)
  propose de doubler le taux à 6% et de relever le seuil à 2 Md€ — seul le levier de taux est
  modélisé ici, le relèvement de seuil (qui réduirait le nombre d'entreprises assujetties) ne
  l'est pas, limite assumée. Source : legifiscal.fr. Ventilée 100% GE, même principe que `ttf`
  (seuil de CA mondial exclut par construction les plus petites entreprises).
- **`cdhr`** (Contribution Différentielle sur les Hauts Revenus) : impôt minimum sur les très
  hauts revenus (PLF 2025). Prévision initiale 2,0 Md€, révisée à 1,5 Md€, mais rendement
  RÉELLEMENT CONSTATÉ (DGFiP) très inférieur — ~0,4 Md€ (2025), ~0,65 Md€ projetés (2026) —,
  écart attribué à l'optimisation comportementale (report de dividendes, arbitrage rémunération/
  dividendes des dirigeants-actionnaires). Le curseur `intensite`=1,0 représente ce rendement
  RÉEL 2026 (pas la prévision initiale). Source : Deloitte Avocats, « La CDHR : un impôt minimum
  sur les revenus du capital... au rendement décevant ». Ventilée 100% D10 dans `decile.py` — le
  périmètre légal (revenu fiscal de référence >250k€ seul / 500k€ couple) vise exclusivement des
  foyers très au-dessus du seuil d'entrée du dernier décile ; approximation assumée : tous les
  foyers CDHR sont en D10, mais tous les foyers de D10 ne sont pas assujettis à la CDHR.
- **`taxe_holdings_patrimoniales`** : taxe sur le patrimoine financier des holdings « patrimoniales »
  familiales (PLF 2026, article 3) — 2% sur la valeur nette des actifs financiers non
  professionnels de holdings familiales détenant ≥5 M€ d'actifs concernés, dont les revenus
  passifs dépassent 50% du total. Rendement estimé ≈1,0 Md€/an dès 2026 ; valeur par défaut du
  curseur = 2% (régime PLF 2026 adopté), même convention que les autres leviers fiscaux de ce
  mockup (défaut = loi en vigueur). Source : legifiscal.fr, « PLF 2026 : instauration d'une taxe
  sur le patrimoine financier des holdings patrimoniales » (10/2025). Ventilée 100% D10 dans
  `decile.py`, même principe que `cdhr` (seuil de patrimoine visé très au-dessus de l'entrée D10).

**`policy_measures.json`** : 4 nouvelles entrées (schéma identique aux mesures existantes,
paramètres/tooltips sourcés) — nécessaire pour que `api.py` accepte ces nouveaux ids (leviers
inconnus du registre → 422).

**`budget_simulator/simulator.py`** (modification du moteur original, AGPL §5) : import du
nouveau mixin `NouvellesTaxes2027Mixin`, ajout à la liste d'héritage de `BudgetSimulatorV45`,
et 4 nouvelles entrées dans le dict `self.measure_handlers`. Aucune ligne de logique métier
existante modifiée — uniquement des ajouts (import, mixin, entrées de dict).

**`frontend/mockup_fiscalite.html`** : les 4 nouvelles mesures sont rangées, comme les mesures
« avancées » existantes, via un « + » ambre en tiret sous la carte du levier principal
thématiquement le plus proche — `ttf` et `taxe_gafa` sous Impôt sur les sociétés (Entreprises),
`cdhr` sous Impôt sur le revenu (Ménages), `taxe_holdings_patrimoniales` sous Fiscalité du
patrimoine (Patrimoine). Nouveau format d'affichage `pct2` (2 décimales) ajouté pour le taux TTF
(0,40% perd en lisibilité avec 1 seule décimale). Vérifié (Playwright) : les 9 « + » ambre
présents, chaque curseur met à jour uniquement son propre chiffrage sans toucher à celui de sa
carte parente.

**Tests manuels effectués** (curl direct sur `/simulate_decile`) : `ttf` à 1% → +3,0 Md€ (formule
`(0.01-0.004)*500`) ; `taxe_gafa` à 6% → +0,7 Md€ (formule `(0.06/0.03-1)*0.7`) ; `cdhr` à
intensité 0 → -0,65 Md€ (suppression) ; `taxe_holdings_patrimoniales` à 4% → +1,0 Md€ (formule
`(0.04/0.02-1)*1.0`) — tous conformes au calcul attendu. `ventilation_taille`/`decile` confirment
le bon routage (ttf/taxe_gafa → 100% GE ; cdhr/taxe_holdings_patrimoniales → 100% D10, non
ventilées par taille).

## 2026-10 — Trois nouveaux leviers sociaux (demande utilisateur, maquette Social)

Lors de la construction de la maquette compacte « Social » (`frontend/mockup_social_compact.html`,
voir entrées précédentes), l'utilisateur a demandé 3 leviers absents du moteur : l'âge du taux
plein automatique (retraites), l'indexation du SMIC sur l'inflation, et une exonération patronale
sur les heures travaillées au-delà de 35h/semaine. Recherche confirmée : AUCUN des trois n'existe
dans `budget_simulator/` (aucun handler, aucun paramètre, aucune constante) avant ce lot.

**AVERTISSEMENT EXPLICITE (à relayer à quiconque reprend ce lot)** : contrairement au reste du
moteur (sourcé précisément, cf `METHODOLOGIE.md`), les 3 coefficients ci-dessous sont des
ESTIMATIONS PAR ANALOGIE ou des ESTIMATIONS COMPOSITES, pas des élasticités dédiées publiées pour
ces mesures précises — même convention de transparence que `handlers/nouvelles_taxes_2027.py`
(2026-10, plus haut). **Non audités.** À valider/recalibrer avant toute mise en production réelle.

**Fichiers ajoutés :**
- `budget_simulator/handlers/nouveaux_leviers_sociaux_2026.py` — handler de la mesure standalone
  `exoneration_heures_sup`.

**Mesures/paramètres ajoutés :**
- **`retraites.age_taux_plein`** (sous-paramètre, PAS une mesure séparée — partage l'id `retraites`
  avec `age_depart`/`indexation`/`duree_cotisation`) : âge d'annulation automatique de la décote
  (67 ans actuellement, Code de la sécurité sociale art. L351-8), référence FIXE (contrairement à
  `age_depart` dont la référence suit le calendrier légal mobile 2026-2032). Coefficient
  budgétaire = 0,15 × `RETRAITES_COEFF_AGE_MD_EUR` (≈0,9 Md€/an par année d'écart) : fraction
  assumée car ce levier ne concerne que les assurés liquidant avec décote/au taux plein par l'âge
  (proxy DREES « Les retraités et les retraites » 2024, ~15% des nouveaux retraités du régime
  général). Effet Gini : même fraction 0,15 appliquée à `RETRAITES_GINI_PAR_ANNEE_ECART`. Implémenté
  dans `handlers/depenses.py::_apply_retraites` (ajout additif, logique existante non modifiée).
- **`smic.indexation`** (sous-paramètre, partage l'id `smic` avec `montant_brut`) : indexation du
  SMIC sur l'inflation (1.0 = trajectoire légale actuelle/statu quo ; <1 = sous-indexation
  cumulative ; >1 = sur-indexation récurrente). Réutilise par analogie les élasticités déjà
  calibrées pour le canal `montant_brut` existant (cotisations 0,45, pouvoir d'achat 0,06,
  compétitivité 0,025, chômage 0,025 — OFCE Plane 2014, IPP Bozio 2018, DG Trésor 2023, Kramarz &
  Philippon 2001), appliquées à un écart cumulé composé (plateau 10 ans, même mécanique que
  `prestations_indexation`) plutôt qu'à un saut de niveau. Anti double-comptage : ne touche pas
  RSA/prime d'activité (périmètre `prestations_indexation`/`asu`). Implémenté dans
  `handlers/additionnels.py::_apply_smic` (canal niveau existant préservé à l'identique, canal
  indexation ajouté en parallèle, additif).
- **`exoneration_heures_sup`** (nouvelle mesure standalone, `cible: recettes`) : exonération de
  cotisations patronales sur les heures travaillées au-delà de 35h/semaine, paramètre `taux`
  (0-100%). Base de cotisations concernée ESTIMÉE ≈9,1 Md€/an (DARES Acemo ~1,4 Md d'heures
  sup/an × salaire horaire brut moyen ~24€ [INSEE DADS 2023] × taux de cotisations patronales de
  référence 27% [même référence que `cotisations_patronales`]) — ESTIMATION COMPOSITE, pas une
  statistique officielle unique. Effet compétitivité one-time par analogie avec le coefficient
  Md€ de `cotisations_patronales` (DG Trésor 2019). AUCUN effet emploi/chômage modélisé : la
  littérature sur les heures sup défiscalisées (loi TEPA 2007-2012) est ambiguë sur l'arbitrage
  heures travaillées/embauches nouvelles, et aucune élasticité consensuelle n'a été identifiée —
  choix assumé de ne rien chiffrer plutôt que d'inventer un coefficient.

**`budget_simulator/config.py`** : nouveaux défauts `retraites.age_taux_plein` (67.0),
`smic.indexation` (1.0), `exoneration_heures_sup` (`{'taux': 0}`).

**`budget_simulator/simulator.py`** (modification du moteur original, AGPL §5) : import du
nouveau mixin `NouveauxLeviersSociaux2026Mixin`, ajout à la liste d'héritage de
`BudgetSimulatorV45`, et 1 nouvelle entrée (`exoneration_heures_sup`) dans le dict
`self.measure_handlers`. Aucune ligne de logique métier existante modifiée pour les mesures déjà
en place — uniquement des ajouts.

**`policy_measures.json`** : `age_taux_plein` ajouté aux `parametres` de `retraites`, `indexation`
ajouté à ceux de `smic`, 1 nouvelle entrée `exoneration_heures_sup`.

**Tests manuels effectués** (appel direct des handlers en Python) : `exoneration_heures_sup`
taux=50%, année 2026 → recettes -4,536 Md€, compétitivité +0,0907 (formule `0.5 * 9.1` Md€ et
`-delta_revenue * 0.020`) ; `retraites` avec `age_taux_plein`=65 (−2 ans) → dépenses +0,72 Md€
(formule `0.9 * 2 * phasing`, Gini -0,00024 ; `phasing`=0,4 au run_year 1, cf
`PHASING_RETRAITES_5ANS`) ; `smic` avec `indexation`=0,8 en 2028 → recettes -0,21 Md€, PA
-0,00048, compétitivité +0,0002, chômage -0,0002 (sous-indexation → moins de cotisations, baisse
de PA pour les smicards, légère amélioration de compétitivité/chômage) — tous les signes
conformes à l'intuition économique attendue. `pytest tests/` : 2 échecs + 7 erreurs liés
exclusivement à des artefacts AUTO-GÉNÉRÉS déjà périmés AVANT ce lot pour les 4 précédents
leviers fiscaux fork (`ttf`/`taxe_gafa`/`cdhr`/`taxe_holdings_patrimoniales` — vérifié : déjà
« absents du registre » avant toute modification de ce lot) : `tests/snapshots/
measure_registry.json` ne peut être régénéré que depuis le dépôt parent complet
(`budgetlab-france`, avec `frontend-react/`), absent de ce fork moteur seul
(`scripts/generate_measure_registry.py`, garde `front_disponible()` déjà skip ce cas en CI).
Rien de cassé côté logique métier existante ; régénération du registre laissée au dépôt parent.
Pas encore exposé dans `frontend/index.html` (production) ni dans `frontend-react/` — seulement
dans le moteur et à ajouter à la maquette `mockup_social_compact.html`.

## 2026-10 — Sourcing des 3 nouveaux leviers sociaux (correction suite à demande utilisateur)

L'entrée précédente qualifiait les paramètres numériques des 3 nouveaux leviers sociaux
d'« ESTIMATION PAR ANALOGIE » / « ESTIMATION COMPOSITE », sans recherche dédiée. L'utilisateur a
demandé de les sourcer correctement. Recherche web ciblée effectuée (2026-10) ; 2 des 3 chiffres
de base ont été CORRIGÉS suite à cette recherche (pas seulement documentés a posteriori) :

- **`retraites.age_taux_plein`** : fraction du coefficient budgétaire corrigée de 0,15
  (valeur à vue de nez) à **0,08 (8 %)**, chiffre officiel DREES : « Les retraités et les
  retraites », édition 2025, fiche 17 « Les conditions de liquidation de la retraite »
  (https://drees.solidarites-sante.gouv.fr/sites/default/files/2025-07/Fiche%2017%20-%20Les%20conditions%20de%20liquidation%20de%20la%20retraite.pdf)
  — génération née en 1953 (départs ~2020) : 8 % liquident au taux plein par l'âge d'annulation
  de la décote (AAD), 11 % avec une décote (population différente, non concernée par CE curseur
  précis : elle liquide avant l'AAD). Nouveau coefficient : `RETRAITES_COEFF_AGE_MD_EUR * 0.08`
  ≈ 0,48 Md€/an (au lieu de ≈0,9 Md€/an). Le MÉCANISME (fraction appliquée au coefficient de
  l'âge légal) reste une construction du moteur, non sourcée en tant que telle — seule la part
  de population l'est désormais.
- **`exoneration_heures_sup`** : base de cotisations corrigée de ≈9,1 Md€/an à **≈4,17 Md€/an**,
  suite à la correction du volume d'heures supplémentaires :
  - Heures sup, secteur privé : 1,4 milliard d'heures/an (estimation initiale à vue de nez) →
    **650 millions d'heures/an**, DARES, enquête Acemo 2016, chiffre repris et cité par l'OFCE,
    « Désocialisation des heures supplémentaires : pouvoir d'achat pour les actifs, perte
    d'emplois pour l'économie »
    (https://www.ofce.sciences-po.fr/blog/lexoneration-partielle-cotisations-sociales-heures-supplementaires-mesure-de-pouvoir-dachat-actifs-perte-demplois-leconomie/).
  - Salaire horaire brut moyen : ~24€ (estimation initiale) → **23,75€** (3 602 €/mois EQTP ÷
    151,67 h/mois), INSEE, Insee Première n° 2079, octobre 2025, « Les salaires dans le secteur
    privé en 2024 » (https://www.insee.fr/fr/statistiques/8657156) — la valeur initiale était en
    fait proche de la bonne, c'est le volume d'heures qui était surestimé d'un facteur ~2.
  - Taux de cotisations patronales de référence : 27 % inchangé (cohérence interne avec
    `cotisations_patronales`, pas une nouvelle source externe).
  - Nouvelle base : 0,65 × 23,75 × 0,27 ≈ 4,17 Md€/an (au lieu de ≈9,1 Md€/an).
- **`smic.indexation`** : recherche dédiée effectuée pour vérifier s'il existe une élasticité
  publiée spécifique à la désindexation du SMIC (plutôt que la réutilisation par analogie des
  élasticités du curseur `montant_brut`). Le rapport officiel France Stratégie, « Groupe
  d'experts SMIC », rapport 2025
  (https://www.strategie-plan.gouv.fr/publications/groupe-dexperts-smic-rapport-2025) a été
  consulté : il recommande explicitement de ne pas dépasser l'indexation automatique par
  précaution, mais NE CHIFFRE AUCUNE élasticité emploi/désindexation — confirmant qu'aucune
  meilleure source dédiée n'existe à ce jour. Les élasticités du canal `montant_brut`
  (elles-mêmes déjà sourcées OFCE/IPP/DG Trésor/Kramarz-Philippon) restent donc la meilleure
  approximation disponible, mais ce choix est désormais justifié par une recherche effective et
  non plus une simple affirmation. AUCUN chiffre modifié pour ce levier.

**Fichiers modifiés** : `budget_simulator/constants.py` (section « Nouveaux leviers sociaux
2026-10 » réécrite avec les 2 corrections et les URLs sources), `budget_simulator/handlers/
nouveaux_leviers_sociaux_2026.py` (docstring mis à jour), `policy_measures.json` (3 tooltips mis
à jour), `frontend/mockup_social_compact.html` (3 tooltips de scope mis à jour). Aucun changement
de logique de calcul (mêmes formules), seulement des constantes numériques et leur
documentation — `exoneration_heures_sup` à 50 % passe donc de -4,536 Md€ de recettes à environ
-2,09 Md€ avec les nouvelles constantes (vérifié par calcul direct).

## 2026-10 — Retours utilisateur sur la réorganisation thématique (lisibilité + bornes)

Suite à un premier test réel de la réorganisation en 3 colonnes, plusieurs problèmes de
lisibilité et de bornes de curseurs ont été signalés et corrigés :

**Bug de lisibilité principal (cause du rendu "illisible" une fois plusieurs `+` ouverts) :**
la règle CSS `.scope-mini` était scopée `.fine-field .scope-mini` — elle ne s'appliquait donc
PAS au texte de description des mesures "folded" (rendues hors d'un `.fine-field`), qui
retombait à la taille de police par défaut du navigateur, nettement plus grosse que partout
ailleurs dans la carte. Règle déscopée (`.scope-mini` tout court) pour s'appliquer partout.
Combiné à un panneau replié auparavant trop verbeux (phrase complète "Mesure indépendante —
rangée ici..." répétée dans chacun des 9 panneaux), le rendu global devenait très lourd. Corrigé
en remplaçant cette phrase par un badge court "indépendant" (même famille visuelle que les
badges "recette"/"ventilé décile" déjà utilisés sur les cartes principales) — l'explication
complète reste dans la légende de section, affichée une seule fois.

**Placement incohérent de la bulle de résultat :** pour les mesures avec `chiffrageMdEur` (ex.
TVA), le chiffrage fusionné "aujourd'hui/avec ce réglage" apparaissait juste sous la
description ; pour les mesures sans `chiffrageMdEur` mais avec un `chiffrage` statique (ex.
Élargissement base IR), il y avait DEUX bulles disjointes : un chiffrage statique en haut ET un
encart "avec ce réglage" tout en bas de la carte, après les sous-paramètres/mesures repliées.
Réorganisé : l'encart "avec ce réglage" est maintenant systématiquement placé juste après le
chiffrage "aujourd'hui", avant le curseur, sur toutes les cartes et tous les panneaux repliés.

**Légende de section en largeur limitée** (`max-width:70ch`, pensée pour du texte de paragraphe)
alors qu'elle explique la règle "+"ambre/teal pour 3 colonnes : passée en pleine largeur.

**Panneaux "Détail par décile"/"Ventilation par taille" repliés par défaut** : ouverts par
défaut maintenant (accès direct à l'info la plus demandée du haut de page).

**Libellé replié qui se compressait en colonne étroite** (ex. "CDHR (impôt minimum hauts
revenus)" affiché sur 5 lignes verticales) : `.folded-head` passé en `flex-wrap`, le libellé
prend toujours 100% de la largeur de sa ligne, les badges passent en dessous.

**Bornes de curseurs élargies** (constat : plusieurs curseurs étaient bloqués sur une plage
artificiellement étroite alors que la formule du moteur est déjà linéaire/valable au-delà) :
- `tva_rate` (taux normal) : 15-25% → 0-50%.
- `tva_rate.taux_intermediaire` : 5,5-20% → 0-30%.
- `tva_rate.taux_reduit` : 2,1-10% → 0-20%, ET **bug corrigé** : le min (0,021) n'était pas un
  multiple du pas (0,005), ce qui faisait "sauter" le curseur vers 2,0%/2,5% dès la première
  interaction (défaut inatteignable ensuite) — signalé comme "incrément bizarre". Min ramené à 0
  (aligné par construction).
- `tva_rate.taux_particulier` : même bug (défaut 0,021, pas 0,005) — corrigé en passant le pas à
  0,001 (0,021 = 21×0,001, aligné) plutôt qu'en arrondissant le défaut. Plage 1-10% → 0-10%.
- `tva_energie` : 5,5-20% → 0-25% ; description clarifiée ("taux simulé librement, pas limité
  aux seuls taux légaux existants") suite à une ambiguïté signalée.
- `elargissement_ir` : 45-70% (figé au statu quo dans les deux sens) → 20-100%.
- `cotisations_salariales` : 0-5 points de BAISSE uniquement → -3 à +5 points (négatif = hausse),
  suite à "on ne peut pas monter du coup ?". **Modification du moteur original (AGPL §5)** :
  `budget_simulator/handlers/fiscalite_menages.py::_apply_cotisations_salariales` clampait
  `baisse_points` à `max(0, min(5, ...))`, empêchant toute hausse même si le paramètre était
  envoyé négatif. Formules déjà linéaires → étendues par symétrie, clamp élargi à `[-3, 5]`,
  aucune nouvelle élasticité inventée.
- `elargissement_ir` (moteur) : même type de modification —
  `_apply_elargissement_ir` clampait `taux_contribuables_cible` à `[0.45, 0.70]` ; élargi à
  `[0.20, 1.00]`, formule déjà linéaire.

**Abattement fiscal retraités — refonte du contrôle** : remplacé l'ancien bouton Oui/Non
(`reforme_active`) par un curseur continu unique 0€-10000€ (`montant`, forfait par personne),
répondant en un seul contrôle aux deux demandes ("curseur 0 à 10000€" ET "suppression oui/non" —
0€ équivaut à la suppression/statu quo). **Modification du moteur original (AGPL §5)** :
`budget_simulator/handlers/depenses.py::_apply_abattement_retraites` acceptait seulement un
booléen `reforme_active` calibré sur UN SEUL forfait (2000€, PLF 2026) ; nouveau paramètre
`montant` ajouté, calibrage étendu en loi LINÉAIRE proportionnelle au forfait choisi
(`montant/2000`) — limite assumée et documentée dans le handler : au-delà de 2000€, c'est une
extrapolation, pas une projection officielle. `reforme_active` reste accepté pour compatibilité
ascendante (équivaut à `montant=2000`).

**Point clarifié (pas un bug)** : le décile D10 affiché dans le détail "Pouvoir d'achat" est une
SOMME de tous les leviers actifs à la fois — `impot_revenu` lui-même n'a PAS de clé de
ventilation par décile sourcée (`decile.py`, `mesures_non_ventilees`), donc bouger son seul
curseur ne devrait rien changer sur ce total ; une variation observée vient forcément d'un AUTRE
levier resté actif (ex. CDHR, qui LUI est ventilé 100% D10). Vérifié par test isolé
(`impot_revenu` seul à 40% vs 60%, toutes choses égales par ailleurs → D10 = 0 dans les deux
cas, conforme). Même remarque pour la décote IR (sous-paramètre d'`impot_revenu` : partage son
chiffrage, pas de ventilation décile indépendante — "aucun lien" est donc le comportement
attendu, pas une anomalie).

Tests effectués : curl direct (`cotisations_salariales` à -2 → +12 Md€ recettes, conforme à
6×2 ; `abattement_retraites` à 5000€ → +10 Md€, conforme à 4×2,5 ; `elargissement_ir` à 90% et
`tva_rate` à 30% calculent sans erreur au-delà des anciennes bornes) + Playwright (page entière,
9 panneaux repliés ouverts simultanément, aucune erreur console, plus de texte disproportionné,
plus de libellé compressé).

## 2026-10 — Bug critique corrigé (TVA) + repère budget de l'État + autres retours

**BUG CRITIQUE trouvé et corrigé par test utilisateur** : `_apply_tva_rate`
(`budget_simulator/handlers/fiscalite_menages.py`) contenait un facteur d'amortissement
comportemental (`1 - 0.2 * (rate - 0.22) / 0.03`) appliqué au-delà de 22%, jamais borné. Ce
facteur était sans danger tant que le curseur restait dans la plage d'origine du moteur
(15-25%) mais, une fois élargi (précédente entrée CHANGES.md), il devenait NUL vers 37% de taux
puis NÉGATIF au-delà — inversant le signe de la recette calculée : le moteur affichait alors
qu'une TVA à 50% rapportait MOINS qu'une TVA à 20%, et par ricochet, dans le mockup (qui inverse
le signe pour afficher un gain/perte ménage), que les ménages gagnaient de l'argent en
augmentant la TVA. Reproduit et confirmé par calcul direct (recette : +64 Md€ à 25%, +76 Md€ à
28% (pic), +31 Md€ à 35%, 0 à 37%, -62 Md€ à 40%, -396 Md€ à 50% AVANT correction). **Correctif** :
le facteur est maintenant plancher à 0 (`max(0.0, damping)`) — au-delà du point où l'effet
comportemental compenserait entièrement l'effet mécanique, le modèle affiche une saturation
(recette additionnelle nulle) plutôt qu'une réversion de signe. Vérifié après correction : 0.0
Md€ à 40% et à 50% (jamais négatif). Borne haute du curseur ramenée de 50% à 40% côté mockup
(zone où l'utilisateur peut voir la hausse ET le début de la saturation, sans aller inutilement
loin dans la zone plate) ; description de la carte mise à jour pour expliquer cette saturation.

**TVA Énergie ne bougeait pas le détail par décile** : signalé par l'utilisateur ("ça ne varie
pas fortement les déciles ?"). Cause : `tva_energie` n'était pas listée dans
`decile.DECILE_SHARES`, donc son impact sur l'indice "Pouvoir d'achat" (calculé) n'était jamais
répercuté sur le détail par décile (toujours 0 pour ce levier). Ajoutée à `DECILE_SHARES` en
réutilisant la clé TVA générale (CPO/Boutchenik), faute de clé dédiée à l'énergie — limite
assumée et documentée explicitement dans le code : cette clé sous-estime probablement la
régressivité réelle d'une taxe sur l'énergie spécifiquement (poids plus élevé chez les ménages
modestes). Egalement : borne haute relevée à nouveau de 25% à 50% (handler purement linéaire,
vérifié sans risque de signe avant élargissement, contrairement à `tva_rate` ci-dessus).

**Repère "budget de l'État" sur les curseurs** (demande explicite : "on bouge un curseur et on
ne sait plus quelle était la valeur de base") : petit trait vertical discret ajouté sur la piste
de CHAQUE curseur, positionné à sa valeur par défaut (= valeur actuelle de la loi). Purement
visuel, ne bouge jamais, avec une infobulle au survol rappelant la valeur de référence.

**Confusion "décote IR rangée dans Impôt >160k€"** : clarifiée sans pouvoir être déplacée (la
décote et le taux marginal >160k€ partagent la MÊME mesure moteur `impot_revenu`, donc le même
id — les séparer visuellement dans des cartes différentes romprait le lien budgétaire réel entre
les deux réglages). La carte est renommée "Impôt sur le revenu (barème)" au lieu de "(tranche
>160k€)", sa description précise qu'elle regroupe 2 curseurs touchant des foyers différents, et
le libellé du "+" décote précise explicitement qu'elle ne dépend pas de la tranche >160k€.

Tests effectués : appel direct du handler `_apply_tva_rate` à 25/30/35/37/40/50% (plus de
recette négative, saturation confirmée à 0 à partir de 37%) ; Playwright (repère visuel présent
sur 21 curseurs, positionné correctement à la valeur par défaut de chacun).

## 2026-10 — Vérification post-sourcing + audit décile/taille des 3 nouveaux leviers sociaux

Suite à la demande explicite de l'utilisateur ("tu as vérifié si tout fonctionnait ? [...] y'a
a mon avis des impacts sur déciles et compet à rajouter [...] faudrait vraiment s'assurer que
tous les leviers impactent"), deux vérifications ont été menées sur les 3 leviers ajoutés le
même mois (`retraites.age_taux_plein`, `smic.indexation`, `exoneration_heures_sup`) :

**1. Re-vérification complète après la correction de sourcing** : suite de tests `pytest`
relancée en intégralité (`2 failed, 1277 passed, 87 skipped, 7 errors` — même résultat,
caractère et nombre identiques, qu'avant la correction : la régression pré-existante et
documentée liée à `tests/snapshots/measure_registry.json` (absence de `frontend-react/` dans ce
fork "moteur seul", cf plus haut dans ce fichier) n'a ni empiré ni changé de nature). Puis un
aller-retour HTTP complet, serveur `uvicorn` lancé localement, avec les 3 leviers actifs
SIMULTANÉMENT :
- `POST /simulate` avec `{"retraites":{"age_taux_plein":70.0},"smic":{"indexation":1.2},
  "exoneration_heures_sup":{"taux":0.5}}` → 200, chaque mesure produit des impacts non-nuls et
  cohérents (`retraites` : -1,44 Md€ de dépenses, gini +1,92e-05 ; `smic` : +0,694 Md€ de
  recettes de cotisations, pouvoir d'achat +0,16%, compétitivité -0,07% ; `exoneration_heures_sup`
  : -2,084 Md€ de recettes, valeur attendue avec les constantes corrigées).
- `POST /simulate_decile` avec les mêmes 3 leviers → 200, `decile.par_mesure` et
  `ventilation_taille.par_mesure` cohérents avec l'audit ci-dessous.

**2. Audit décile (`budget_simulator/decile.py`) et taille d'entreprise
(`budget_simulator/ventilation_taille.py`) des 3 nouveaux leviers**, conformément au principe
déjà en vigueur dans ces deux modules ("pas de clé sourcée -> la mesure reste non ventilée,
plutôt que d'inventer une hypothèse") :

- `retraites.age_taux_plein` : **déjà ventilé par décile sans aucun code supplémentaire.** La
  ventilation opère au niveau de la mesure entière `retraites` (clé DREES déjà présente dans
  `DECILE_SHARES` pour `indexation`/`duree_cotisation`), donc la contribution Md€ de
  `age_taux_plein` au delta net de `retraites` est automatiquement incluse. Vérifié
  empiriquement : `age_taux_plein=70` (vs défaut 67) fait apparaître `retraites` dans
  `decile.par_mesure` avec -1,44 Md€ ventilés par décile (D1 -0,043 Md€ ... D10 -0,245 Md€),
  alors qu'il est absent (aucun impact) à la valeur par défaut.
- `smic.indexation` : recherché (DARES, INSEE, France Stratégie) une clé de répartition des
  smicards par décile de NIVEAU DE VIE DU MÉNAGE (et non juste du salarié) — non trouvée sous
  forme exploitable. `smic` (déjà, y compris pour son paramètre `montant_brut` historique) reste
  donc "non ventilé" par décile — lacune PRÉ-EXISTANTE, pas introduite par ce lot, désormais
  documentée explicitement dans `decile.py` plutôt que silencieuse.
- `exoneration_heures_sup` (nouvelle mesure) : recherché une clé de répartition du volume
  d'heures supplémentaires par catégorie d'entreprise (MIC/PME/ETI/GE), pertinente pour
  `ventilation_taille.py` — non trouvée non plus sous forme exploitable (même lacune, déjà
  documentée pour sa mesure la plus proche, `cotisations_patronales`). Reste "non ventilée" par
  taille et par décile, documenté explicitement dans les deux modules.

**Conclusion** : aucune hypothèse inventée n'a été ajoutée. `age_taux_plein` profite
gratuitement de la ventilation décile déjà sourcée de `retraites`. `smic` et
`exoneration_heures_sup` restent "non ventilés" (décile et/ou taille selon le cas), au même
titre que des mesures pré-existantes du moteur (`fraude_fiscale`, `cotisations_patronales`,
etc.) pour lesquelles aucune source fiable n'a été identifiée — ce choix est maintenant
documenté en commentaire dans le code, pour que ce ne soit plus un angle mort silencieux mais un
choix explicite, traçable, et révisable si une meilleure source est trouvée plus tard.

## 2026-10 — Nouvelle maquette compacte "Dépenses" (suite du plan "un mockup par catégorie")

Après validation de la maquette Social, transposition du même pattern de carte compacte
(`frontend/mockup_fiscalite_compact.html`, `frontend/mockup_social_compact.html`) aux 8 mesures
de la catégorie `depenses` : nouveau fichier `frontend/mockup_depenses_compact.html`. Les 8
mesures (`fonction_publique`, `fonction_publique_reforme`, `optimisation_dette`,
`rabot_uniforme`, `education`, `collectivites`, `defense`, `immigration`) et la totalité de
leurs paramètres ont été vérifiés exhaustivement contre `policy_measures.json` (aucun paramètre
manquant, contrairement au cas "santé" rencontré dans la maquette Social) et regroupés en 2
thèmes : "État & fonction publique" (4 mesures) et "Budgets sectoriels" (4 mesures).

**Limite pré-existante explicitée dans l'UI** : `collectivites`, `defense` et `immigration` sont
des mesures de type "formule" (évaluées par ASTEVAL côté `engine/orchestrator.py`), sans handler
Python dédié — elles n'émettent QUE `depenses`/`recettes`, jamais `gini`, `pouvoir_achat` ni
`competitivite` (vérifié par appel direct au moteur). Ces 3 leviers ne font donc jamais bouger
les indices "Pouvoir d'achat" / "Compétitivité" du bandeau du haut, ni leur détail par
décile/taille (absents de `DECILE_SHARES`/`TAILLE_SHARES`). Un bandeau d'avertissement dédié a
été ajouté dans la maquette pour l'expliciter, plutôt que de laisser l'utilisateur penser à un
bug silencieux en bougeant ces curseurs sans rien voir changer sur ces 2 indices.

**Bug corrigé (découvert en construisant cette maquette)** : `rabot_uniforme` est la première
mesure, dans ce pattern de carte, à avoir des sous-paramètres booléens dont le défaut moteur est
`true` (les 3 exclusions `exclure_dette`/`exclure_defense`/`exclure_ue`, cochées par défaut).
Le code JS partagé `buildMesures()` codait en dur `def = 0` pour TOUT sous-paramètre booléen
(hérité de `mockup_social_compact.html`, où l'unique sous-paramètre booléen,
`chomage_alloc::degressivite`, a justement `default:false` — ce qui masquait le bug). Décocher
une case à défaut `true` (ex. "Exclure la défense") envoyait alors `val=0 === def=0` codé en dur
→ la condition `if (val === def) return;` empêchait silencieusement l'envoi du paramètre à
l'API, qui retombait sur le défaut moteur (exclusion toujours active) au lieu du 0 pourtant
demandé par l'utilisateur. **Corrigé** dans les deux fichiers (`mockup_depenses_compact.html` ET
`mockup_social_compact.html`, par cohérence même si inoffensif dans ce second fichier) en
dérivant `def` du vrai défaut déclaré (`sp.default`) au lieu de le coder en dur à 0. Vérifié par
un test Playwright direct : décocher "Exclure la défense" avec `taux_reduction=8%` envoie bien
`{"taux_reduction":0.08,"exclure_defense":0}` à l'API, et produit un résultat moteur différent
(-140,3 Md€ contre -137,97 Md€ avec l'exclusion active) — confirmant que le paramètre est
désormais pris en compte.

Tests effectués : suite `pytest` complète inchangée (`2 failed, 1277 passed, 87 skipped, 7
errors`, même bucket pré-existant documenté plus haut) ; Playwright (8 cartes, toutes 104px
replié ; tous les curseurs principaux et réglages fins présents et correctement nommés ;
activation de `defense.budget` et `education.budget` vérifiée avec cohérence des deltas affichés
dans le bandeau du haut — PIB, déficit, compétitivité, pouvoir d'achat).

## 2026-10 — Nouvelle maquette compacte "Compétitivité" (suite du plan "un mockup par catégorie")

Troisième maquette compacte du plan, après Social et Dépenses : nouveau fichier
`frontend/mockup_competitivite_compact.html`, transposant les 6 mesures de la catégorie
`competitivite` (`cotisations_patronales`, `impots_production`, `niches_fiscales_tge`,
`niches_sociales_tge`, `subventions_tge`, `is_exceptionnel_tge`). Les 6 mesures et leur
paramètre unique (toutes sont des mesures à un seul réglage, pas de sous-paramètres) ont été
vérifiés exhaustivement contre `policy_measures.json`, et regroupés en 2 thèmes : "Fiscalité
générale des entreprises" (2 mesures touchant toutes les tailles) et "Avantages ciblés grandes
entreprises / TGE" (4 mesures).

À la différence de la catégorie Dépenses, les 6 mesures de Compétitivité ont TOUTES un handler
Python dédié (`budget_simulator/handlers/competitivite.py`, aucune mesure "formule") et
impactent donc toutes directement l'indice Compétitivité du bandeau du haut — pas de bandeau
d'avertissement "sans effet" nécessaire ici. Vérifié par appel direct au moteur et par
Playwright : les 4 leviers "TGE" sont ventilés à 100% sur la catégorie "Grandes entreprises"
dans le détail par taille (périmètre légal de chaque mesure, déjà sourcé dans
`ventilation_taille.py`) ; `cotisations_patronales` et `impots_production` touchent toutes les
entreprises mais restent "non ventilés" par taille (limite pré-existante déjà documentée,
données DGFiP insuffisantes) — signalé explicitement dans un bandeau dédié de la maquette.
Aucune des 6 mesures n'est ventilée par décile de niveau de vie (mesures entreprises, pas
ménages) : comportement normal, pas une lacune.

Tests effectués : suite `pytest` complète inchangée (`2 failed, 1277 passed, 87 skipped, 7
errors`, même bucket pré-existant) ; Playwright (6 cartes, toutes 104px replié, les 6 curseurs
principaux présents et correctement nommés ; activation simultanée de `cotisations_patronales`
(taux 20%, -7 pts) et `niches_fiscales_tge` (montant 5 Md€, suppression de 53 Md€) vérifiée :
effet net sur les finances publiques cohérent, indice Compétitivité +1,26 (cumul des deux
effets de sens opposé), ventilation par taille affichant bien 100% GE pour l'effort de 53 Md€
imputable à `niches_fiscales_tge` uniquement — `cotisations_patronales` correctement absent de
ce détail, confirmant que la non-ventilation documentée est bien respectée en pratique).

## 2026-10 — Nouvelle maquette compacte "Économie" (dernière catégorie du plan)

Cinquième et dernière maquette compacte du plan "un mockup par catégorie" : nouveau fichier
`frontend/mockup_economie_compact.html`, couvrant les 2 seules mesures de la catégorie
`economie` (`transition_ecologique` — 3 paramètres : investissement, taxe carbone, rénovation —
et `recherche_publique`). Avec ce fichier, les 5 catégories du moteur (fiscalite, social,
depenses, competitivite, economie) ont chacune leur maquette compacte validée/vérifiée.

**Point notable découvert en vérifiant `recherche_publique`** : cette mesure est déclarée
`"type": "formule"` dans `policy_measures.json`, comme `collectivites`/`defense`/`immigration`
dans la catégorie Dépenses — mais contrairement à ces 3-là, elle possède bel et bien un handler
Python dédié (`_apply_recherche_publique` dans `handlers/investissements.py`, enregistré dans
`simulator.py::measure_handlers`). Le code de `engine/orchestrator.py` donne toujours priorité
au handler Python sur la formule ASTEVAL quand les deux existent (`if measure_id in
self.measure_handlers: ... elif measure.get('type') == 'formule': ...`), donc `recherche_publique`
impacte bien Gini/Pouvoir d'achat/Compétitivité comme n'importe quelle mesure à handler complet
— le champ `"type"` de `policy_measures.json` ne prédit donc PAS, à lui seul, si une mesure a un
vrai handler ou retombe sur la formule générique : il faut vérifier `measure_handlers` dans
`simulator.py` pour en être sûr. Vérifié par appel direct au moteur.

Les 2 mesures de cette catégorie ont chacune un handler complet et impactent toutes les 2 Gini,
Pouvoir d'achat et Compétitivité (aucun bandeau d'avertissement "sans effet" nécessaire, à la
différence de la maquette Dépenses). Aucune des 2 n'a de clé de ventilation par décile ou par
taille d'entreprise sourcée — `transition_ecologique` est même explicitement citée en exemple
dans la docstring de `decile.py` comme mesure "non ventilée" faute de clé ; recherche effectuée
pour les deux mesures en construisant cette maquette, sans trouver de source exploitable.

Tests effectués : suite `pytest` complète inchangée (`2 failed, 1277 passed, 87 skipped, 7
errors`, même bucket pré-existant) ; Playwright (2 cartes, toutes 104px replié, les 2 curseurs
principaux et les 2 réglages fins de `transition_ecologique` présents et fonctionnels) ;
activation simultanée de `transition_ecologique` (rénovation 10 Md€, taxe carbone 150€/t) et
`recherche_publique` (18 Md€) vérifiée : déficit amélioré (+0,43 pt, recettes carbone + retours
fiscaux dominant la dépense), compétitivité légèrement positive (+0,06), pouvoir d'achat +1,20 —
cohérent avec les formules des handlers.

## 2026-10 — 5 nouveaux leviers ("grille de tri 12 pistes", demande utilisateur)

Comparaison du classeur de référence de l'utilisateur, `Simulateur_Impact_Menages.xlsx` (onglet
"Grille de tri (12 pistes)"), avec les 41 mesures existantes de `policy_measures.json` : 5 pistes
absentes du moteur identifiées et intégrées à sa demande explicite ("oui intégrer ces nouveaux
leviers") — piste 3 "coupe des prestations" (~-13,9 Md€), piste 9 "quotient familial" (~4,75 Md€),
piste 10 "quotient conjugal" (~5,4 Md€), piste 11 "PFU/barème" (~2,2 Md€), piste 12 "taxe Zucman"
(~20 Md€ bruts). Recherche sourcée dédiée effectuée pour chacune (voir détail par mesure
ci-dessous) ; aucun coefficient inventé — quand aucune source exploitable n'a été trouvée pour une
ventilation (décile ou taille d'entreprise), la mesure est explicitement laissée "non ventilée".

**Mesures ajoutées :**

- **`quotient_familial`** (`handlers/fiscalite_menages.py`, catégorie fiscalite) : abaissement du
  plafond de l'avantage du quotient familial par demi-part. Plafond actuel 1791€ (Légifiscal,
  confirmé Sénat rapport PLF 2025 n°144). Rendement calé sur le SEUL point de calibration réel
  disponible : la baisse PLF 2014 (2000€→1500€) avait été chiffrée par le gouvernement à
  +1,03 Md€ (Légifiscal) → coefficient linéaire 1,03 Md€/500€. Coût total du dispositif (hors
  conjugal) : 19,0 Md€/an (Insee Analyses n°53, juin 2020). **Non ventilé par décile** : la seule
  source trouvée (Insee Analyses n°53) ne publie qu'une concentration agrégée conjugal+familial
  par VINGTILE (5% les plus aisés = 20% des gains ; 25% les plus aisés = 50% des gains), pas un
  tableau décile par décile ni une ventilation séparée par dispositif — insuffisant pour
  construire 10 parts sourcées sans inventer les valeurs intermédiaires.
- **`quotient_conjugal`** (`handlers/fiscalite_menages.py`, catégorie fiscalite) : individualisation
  de l'IR des couples mariés/pacsés (fin de l'imposition commune). Slider intensité 0-100%
  interpolant vers le scénario "individualisation complète avec option enfants" de l'Insee
  (+7,2 Md€/an — Économie et Statistique n°526-527, 2021, Allègre et al., qui chiffre aussi 2
  autres scénarios non retenus ici : réduction à 1,5 part 3,8-4,8 Md€, plafonnement 2,9 Md€).
  Coût total du dispositif conjugal seul : 10,8 Md€/an (Insee Analyses n°53 décompose le total
  29,7 Md€ en 10,8 Md€ conjugal / 19,0 Md€ familial — sourcing qui garantit l'ABSENCE de
  double-comptage entre ce levier et `quotient_familial`). **Non ventilé par décile**, même limite
  que `quotient_familial`.
- **`pfu_bareme`** (`handlers/fiscalite_menages.py`, catégorie fiscalite) : retour au barème
  progressif de l'IR pour les revenus du capital (fin du PFU à 30%). Rendement brut 1,55 Md€
  (milieu de la fourchette 1,4-1,7 Md€, coût permanent du PFU estimé par le comité d'évaluation
  France Stratégie — Sénat, rapport n°19-042-1, "Transformation de l'ISF en IFI et création du
  PFU : un premier bilan"), net d'un facteur comportemental 0,85 : ESTIMATION assumant qu'un
  retour au barème réduirait symétriquement le rebond de distribution de dividendes mesuré par
  l'IPP lors du passage au PFU (note n°46, 2019 : dividendes 29,8→37,1 Md€ 2017-2018, ~0,5 Md€ de
  recettes additionnelles non anticipées sur un rendement PFU réel 2018 de 3,5 Md€, d'où
  1-0,5/3,5≈0,85) — pas une élasticité publiée pour le sens inverse de la réforme, symétrie
  assumée et documentée comme telle. **Non ventilé par décile** : l'unique étude distributive
  trouvée sur le PFU (IPP note n°46) ne publie aucune répartition par décile des bénéficiaires.
- **`taxe_zucman`** (`handlers/nouvelles_taxes_2027.py`, catégorie fiscalite) : plancher
  d'imposition de 2% sur le patrimoine net des foyers détenant plus de 100 M€ (~1800 foyers),
  proposition Gabriel Zucman (rapport au G20, 2024). **DEUX estimations délibérément exposées
  toutes les deux**, pas de chiffre tranché arbitrairement par le moteur : estimation du
  proposant 20 Md€/an ±5 Md€ (Public Sénat, "Taxe Zucman : quels sont les arguments pour, et les
  arguments contre ?") vs contre-estimation iFRAP 2-3 Md€/an ("Fiscalité des riches : le mirage
  des milliards € de recettes"), motivée par la non-déduction de l'IS déjà payé par les sociétés
  détenues au niveau des holdings (double imposition du même résultat économique). Risque
  constitutionnel documenté (Conseil constitutionnel, censure 2012 d'un taux marginal 1,8% jugé
  confiscatoire). Un second curseur, `part_critique` (0-1, défaut 0,5), pondère entre les deux
  bornes — curseur ASSUMÉ par ce moteur (pas une pondération publiée), pour que l'utilisateur
  situe lui-même son scénario plutôt que de se voir imposer un choix. DISTINCTE de
  `isf_climatique` (déjà présente dans le moteur) : celle-ci est un ISF progressif classique
  (seuil ~0,8-2M€, barème 0-1%, bonus actifs verts, remplace l'IFI) touchant un bien plus grand
  nombre de foyers ; `taxe_zucman` est un plancher anti-optimisation ultra-ciblé (>100M€, sans
  bonus écologique, sans remplacement d'un impôt existant) — vérifié en lisant le handler
  `_apply_isf_climatique` avant d'écrire celui-ci, aucun chevauchement de mécanisme. **Non
  ventilée ni par décile ni par taille d'entreprise**, par choix de PRUDENCE assumé (et non par
  absence totale d'information de périmètre) : la fraction de D10 réellement concernée est très
  étroite et le rendement lui-même varie d'un facteur 8 entre les deux sources, ce qui rendrait
  une approximation "100% D10" (comme pour `cdhr`/`taxe_holdings_patrimoniales`) trompeuse de
  précision ; et le patrimoine détenu via des holdings familiales privées non cotées échappe au
  périmètre statistique DGFiP/INSEE par taille d'entreprise (MIC/PME/ETI/GE).
- **`coupe_prestations`** (`handlers/depenses.py`, catégorie social) : coupe DIRECTE et IMMÉDIATE
  d'un pourcentage du montant versé des prestations sociales (RSA/APL/allocations
  familiales/prime d'activité). Vérifié au préalable (grep sur `budget_simulator/`) : DISTINCTE de
  `prestations_indexation`, qui ne pilote QUE le taux de compensation de l'inflation (érosion
  composée sur plusieurs années) — `coupe_prestations` retire une fraction du montant chaque année
  dès l'entrée en vigueur, sans dépendre de l'inflation. Réutilise TELLE QUELLE la base de 90 Md€
  déjà sourcée dans ce moteur pour `prestations_indexation` (RSA 12 + APL 15 + allocations
  familiales 50 + autres 13 — PLFSS 2026/DREES/OFCE 2024/IPP 2023) : pas une nouvelle base
  inventée. Les deux leviers sont CUMULABLES (pas d'anti-double-comptage automatique entre eux,
  documenté explicitement comme limite assumée) mais partagent la même garde anti-double-comptage
  ASU (`asu_is_active`) que `prestations_indexation`. **Ventilée par décile** : réutilise la clé
  déjà sourcée de `prestations_indexation` (DSS/DREES REPSS Famille éd. 2025) dans `decile.py`,
  légitime car même base, même population de bénéficiaires — seul le mécanisme budgétaire diffère.

**Fichiers modifiés :**
- `budget_simulator/constants.py` : nouvelle section "Nouveaux leviers fiscaux & sociaux 2026-10"
  (constantes + sources détaillées pour les 5 mesures).
- `budget_simulator/handlers/fiscalite_menages.py` : 3 nouveaux handlers (`_apply_quotient_familial`,
  `_apply_quotient_conjugal`, `_apply_pfu_bareme`), docstring de module mis à jour.
- `budget_simulator/handlers/nouvelles_taxes_2027.py` : 1 nouveau handler (`_apply_taxe_zucman`),
  docstring de module mis à jour (distinction explicite avec `isf_climatique`).
- `budget_simulator/handlers/depenses.py` : 1 nouveau handler (`_apply_coupe_prestations`),
  docstring de module mis à jour (distinction explicite avec `prestations_indexation`).
- `budget_simulator/decile.py` : nouvelle entrée `coupe_prestations` (réutilise la clé
  `prestations_indexation`) ; docstring mis à jour listant `quotient_familial`/`quotient_conjugal`/
  `pfu_bareme`/`taxe_zucman` comme explicitement examinées et laissées non ventilées, avec le
  détail de la recherche effectuée pour chacune.
- `budget_simulator/ventilation_taille.py` : docstring mis à jour (les 5 mesures sont hors
  périmètre ou laissées non ventilées, avec justification pour `taxe_zucman`).
- `budget_simulator/config.py` et `budget_simulator/simulator.py` (modifications du moteur
  original, AGPL §5) : nouveaux défauts (`load_default_values`) et 5 nouvelles entrées dans
  `self.measure_handlers`. Aucune ligne de logique métier existante modifiée.
- `policy_measures.json` : 5 nouvelles entrées (41 → 46 mesures), tooltips citant les sources
  ci-dessus.
- `tests/test_mixin_architecture.py` : `_EXPECTED_HANDLER_COUNT` 38 → 43 (constante maintenue à
  la main, cf. commentaire dans le fichier).

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
EXACTEMENT le même bucket pré-existant qu'avant ce lot (les 2 échecs et 7 erreurs restent dus aux
mêmes causes documentées dans les entrées précédentes — registre `tests/snapshots/
measure_registry.json` périmé, régénérable seulement depuis le dépôt parent complet avec
`frontend-react/` — simplement enrichis des 5 nouvelles entrées dans la liste des paramètres
"morts" déjà signalée pour `ttf`/`taxe_gafa`/`cdhr`/`taxe_holdings_patrimoniales`/
`exoneration_heures_sup`/`smic.indexation`/`retraites.age_taux_plein`, pas une régression
nouvelle). Appels directs du moteur (`BudgetSimulatorV45(...).simulate()`) vérifiés pour les 5
mesures : signes et ordres de grandeur conformes aux formules (ex. `taxe_zucman` intensite=1.0,
part_critique=0 → recettes +20,0 Md€ ; part_critique=1 → +2,5 Md€ ; `coupe_prestations`
taux_coupe=10% → dépenses -9,0 Md€, Gini +0,008, PA -0,003). Serveur `uvicorn api:app` démarré et
testé via `curl` sur `/simulate` (les 5 mesures combinées produisent bien un report cohérent,
`measure_impacts_by_year` peuplé pour chacune) et `/simulate_decile` (`coupe_prestations` ventilée
par décile avec la clé réutilisée de `prestations_indexation`, somme des parts = total ; les 4
mesures fiscales non ventilées apparaissent bien dans `mesures_non_ventilees` de `decile` et dans
celui de `ventilation_taille`).

## 2026-10 — Nouveau levier `accises` (TICPE + tabac + alcool), demande utilisateur "accise ok"

Cette session a comparé le moteur avec un projet tiers (github.com/Vadech/moi-president), qui
porte un levier "Excises/product taxes" (droits d'accise indirects sur carburants/tabac/alcool,
distinct de la TVA) absent de ce moteur — seuls `tva_rate` (TVA générale) et `tva_energie` (TVA
énergie) existaient. Confirmation explicite utilisateur ("accise ok") pour l'ajouter. Le chiffre
du projet tiers lui-même (7,7%, 15,3 Md€/point) n'a PAS été repris (non vérifiable, pas une source
administrative) : assiette et coefficients entièrement reconstruits à partir de sources françaises
vérifiables, suivant le même protocole que les 5 leviers du lot précédent.

**Mesure ajoutée : `accises`** (`handlers/fiscalite_menages.py::_apply_accises`, catégorie
fiscalite) : variation relative (`variation_pct`, -30% à +50%, défaut 0) appliquée identiquement
au niveau des 3 droits d'accise suivants — distincts d'un taux de TVA ad valorem (montant
spécifique par unité physique, hL ou 1000 cigarettes) :
- **TICPE** (carburants routiers) : 30,5 Md€/an (2022, dernière donnée chiffrée par le ministère
  de la Transition écologique, relayée par la presse spécialisée ; ordre de grandeur stable
  30-33 Md€ brut en 2023-2024 selon le Trésor).
- **Droits de consommation sur le tabac** (dont licences débitants) : 13,95 Md€/an (2024,
  prévision), Sénat, rapport d'information n°638 (2023-2024), "La fiscalité comportementale en
  santé : stop ou encore ?" — données DGDDI (13 614 M€ en 2023, 13 952 M€ prévus en 2024).
- **Droits sur les alcools** (droits de consommation alcools + bières/BNA + cotisation de
  solidarité + vins/cidres/poirés/hydromels + produits intermédiaires) : 4,565 Md€/an (2024,
  provisoire), même rapport Sénat n°638, données DGDDI.

Total : 49,0 Md€/an — volontairement EN DEÇÀ de l'estimation informelle "60-70 Md€" parfois citée
(ex. Institut Molinari 2019), qui agrège une assiette plus large incluant la TVA sur ces produits,
ce qui ferait double emploi avec `tva_rate` dans ce moteur ; le périmètre retenu ici est strictement
celui des droits d'accise (TICPE+tabac+alcool), pas la fiscalité totale sur ces produits.

Élasticité-prix -0,4 : reprise du tabac (seule élasticité publiée avec cette précision parmi les 3,
même rapport Sénat n°638, "hypothèse conventionnelle correspondant aux études disponibles"),
appliquée aux 3 composantes par **ESTIMATION PAR ANALOGIE**, faute d'élasticité combinée dédiée
publiée — même démarche déjà utilisée par `tva_rate`/`tva_energie` dans ce fichier pour amortir
l'effet mécanique d'un changement de taux.

**Ventilation par décile : NON ajoutée, mais une vraie source a été trouvée et examinée** — Insee,
Ruiz & Trannoy, "Le caractère régressif des taxes indirectes", Économie et Statistique n°413
(2008), tableau 4, donne un taux d'effort par décile pour EXACTEMENT ces 3 taxes : tabac 0,91%
(D1) à 0,13% (D10) du revenu disponible ; alcools 0,47% (D1) à 0,16% (D10) ; produits
pétroliers/TICPE 2,89% (D1) à 1,00% (D10) ; combinées, 4,3% (D1) contre 1,3% (D10) — confirmant une
régressivité plus marquée que la TVA générale. Cette étude ne publie cependant PAS le revenu
disponible moyen par décile dans le même tableau : convertir un taux d'effort en PART DE CHARGE
par décile (10 parts sommant à 1, le format attendu par `decile.py`) nécessiterait de le croiser
avec une distribution de revenu par décile tirée d'une autre source — une combinaison à deux
sources non publiée telle quelle, que ce moteur évite par principe (même discipline que
`quotient_familial`/`quotient_conjugal`/`pfu_bareme` dans le lot précédent). `accises` reste donc
"non ventilée" dans `decile.py`, mais le coefficient agrégé gini/pouvoir d'achat du handler EST
calibré PAR ANALOGIE sur cette même étude (facteur gini majoré à 0,07 contre 0,05 pour
`tva_energie`, pour refléter la régressivité plus forte mesurée) — documenté comme estimation,
pas comme une clé de décile.

**Fichiers modifiés :**
- `budget_simulator/constants.py` : nouvelle section "Accises" (assiette, élasticité, facteurs
  gini/pouvoir d'achat, sources détaillées avec URLs).
- `budget_simulator/handlers/fiscalite_menages.py` : nouveau handler `_apply_accises`, import des
  nouvelles constantes, docstring de module mis à jour.
- `budget_simulator/simulator.py` : nouvelle entrée `'accises': self._apply_accises` dans
  `self.measure_handlers` (modification du moteur original, AGPL §5).
- `budget_simulator/config.py` : nouveau défaut `'accises': {'variation_pct': 0}` dans
  `load_default_values` (modification du moteur original, AGPL §5).
- `budget_simulator/decile.py` : docstring mis à jour, `accises` listée comme explicitement
  examinée et laissée non ventilée, avec le détail de la source trouvée et la raison de son
  insuffisance pour construire une clé.
- `policy_measures.json` : 1 nouvelle entrée (46 → 47 mesures), tooltip citant les sources.
- `tests/test_mixin_architecture.py` : `_EXPECTED_HANDLER_COUNT` 43 → 44 (constante maintenue à
  la main, cf. commentaire dans le fichier).

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
EXACTEMENT le même bucket pré-existant (les 2 échecs et 7 erreurs restent dus aux mêmes causes déjà
documentées — registre `tests/snapshots/measure_registry.json` périmé — désormais simplement
enrichis de `accises` dans la liste des paramètres "morts" déjà signalée pour les leviers
précédents, pas une régression nouvelle). Serveur `uvicorn api:app --port 8099` démarré et testé
via `curl` : `/simulate` avec `accises.variation_pct=0.10` produit bien, chaque année,
`recettes +4,71 Md€` (= 0,10 × 49,0 Md€ × (1 - 0,4×0,10), cohérent avec la formule), et en
première année seulement (effet NIVEAU one-time) `gini +0,007` et `pouvoir_achat -0,0028` ; comparé
à un run sans mesure sur la même période, le Gini agrégé passe de 0,290 à 0,291 et le Pouvoir
d'Achat agrégé 2026 recule de 100,5 à 100,2 (cohérent avec une taxe régressive) ; `Recettes/PIB %`
passe de 52,2% à 52,4%. `/simulate_decile` confirmé : `accises` apparaît bien dans
`mesures_non_ventilees`, aucun crash.

## 2026-10 — Deux nouveaux leviers ("audit comparatif" vs autres simulateurs citoyens, dont
l'Institut Montaigne "Atelier des finances publiques" 2015-2017)

Cette session a comparé le moteur avec plusieurs autres simulateurs budgétaires citoyens
(dont l'outil 2015-2017 de l'Institut Montaigne) et identifié 2 leviers sourcés absents de ce
moteur, confirmés par l'utilisateur ("oui ok") : le Crédit d'impôt recherche (CIR, aide fiscale
à la R&D PRIVÉE) et la subvention d'équilibre de l'État aux régimes spéciaux de retraite. Les
deux ont été vérifiés comme NE recoupant PAS une mesure existante avant ajout :
- `credit_impot_recherche` est DISTINCT de `recherche_publique`
  (`handlers/investissements.py`), dont le docstring précisait déjà explicitement
  "Actuel ~10 Md€ (hors CIR 7 Md€)" — assiettes disjointes (R&D publique vs crédit d'impôt aux
  entreprises privées).
- `regimes_speciaux_retraite` est DISTINCTE de `retraites` (`handlers/depenses.py`), qui ne
  pilote que les paramètres du régime général (âge légal, durée de cotisation, indexation) —
  aucun recoupement avec la subvention budgétaire directe aux régimes fermés/déséquilibrés.

**Mesure ajoutée : `credit_impot_recherche`** (`handlers/investissements.py::
_apply_credit_impot_recherche`, catégorie compétitivité) : paramètre `montant` (Md€, défaut 6,6,
0 à 12). Coût budgétaire actuel 6,6 Md€ (DGFiP "Voies et moyens" tome II, créance 2025
anticipée, cité par Sénat, rapport PLF 2025 "Remboursements et dégrèvements", l24-144-327 ;
2024 : 6,5 Md€). Une baisse du montant = rabot/suppression partielle (+recettes immédiates).
Effet compétitivité calibré sur l'effet de levier publié par France Stratégie/CNEPI (rapport
SEURECO, juin 2021, strategie-plan.gouv.fr) : 1€ de CIR génère entre 1,2 et 1,5€ de R&D privée
supplémentaire (1,35 retenu) ; phasing progressif sur 5 ans et coefficient par Md€ de R&D
identiques à `recherche_publique` (0,0015, élasticité OCDE Guellec & Van Pottelsberghe 2004 =
0,17), appliqués ici au delta de R&D PRIVÉE induit. LIMITE ASSUMÉE documentée : l'OCDE (2017,
citée par la CNEPI) montre que le CIR génère un effet de levier plus faible que la R&D publique
directe (1,2-1,5€ CIR vs 1,70$ OCDE pour la R&D publique) — ce différentiel est capturé par le
ratio de levier lui-même, pas recorrigé une seconde fois. Gini laissé à 0 (même argumentation
que `recherche_publique` : aucune étude n'estime l'incidence MÉNAGE d'un crédit d'impôt versé à
des entreprises). Pouvoir d'achat laissé à 0 (pas de canal emploi chiffré comparable au
recrutement public de chercheurs modélisé côté `recherche_publique`).

**Ventilation : non par décile (mesure concernant des entreprises, pas des foyers fiscaux —
hors périmètre par nature, documenté dans `decile.py`), MAIS par taille d'entreprise AJOUTÉE**
dans `ventilation_taille.py` avec une clé réelle sourcée : MESR-DGRI, données 2023 (relayées par
financeinnovation.fr, "Le crédit impôt recherche (CIR) en 2023") : PME 31% de la créance (81%
des déclarants), ETI 28% (15% des déclarants), grandes entreprises 41% (3,5% des déclarants) —
ces 3 parts somment à 100%. Microentreprises non isolées dans cette statistique officielle (seuil
communautaire "PME" <250 salariés les englobe) : MIC mis à 0, limite documentée explicitement
dans `ventilation_taille.py` (part réelle non nulle mais non chiffrée séparément par la source).

**Mesure ajoutée : `regimes_speciaux_retraite`** (`handlers/depenses.py::
_apply_regimes_speciaux_retraite`, catégorie social) : paramètre `montant` (Md€, défaut 6,0, 0
à 8). Subvention d'équilibre totale 6,0 Md€ en 2026 (Sénat, rapport PLF 2026 "Régimes sociaux et
de retraite", l25-139-324, quasi stable vs 2025, -0,13%), dont ~69% (4,1 Md€) pour les seuls
régimes fermés SNCF/RATP ; source corroborante : Cour des comptes, note d'exécution budgétaire
2023, mission "Régimes sociaux et de retraite" (avril 2024). Une baisse du montant = économie
budgétaire directe.

**Ventilation : non ajoutée, ni par décile ni par taille d'entreprise**, EXAMINÉE et
documentée explicitement comme hors de portée des sources disponibles : aucune publication
(DREES, Cour des comptes) ne ventile les bénéficiaires de CES régimes spécifiquement par décile
de niveau de vie du ménage (la DREES ventile les pensions de retraite EN GÉNÉRAL, `retraites`
dans `decile.py`, pas ce sous-ensemble). Le signe même de l'effet distributif n'est d'ailleurs
pas établi : la Cour des comptes documente des pensions moyennes de certains régimes spéciaux
(ex. SNCF) supérieures à la moyenne du régime général, ce qui rend non fondée l'hypothèse par
défaut "régressif". Gini ET pouvoir d'achat laissés à 0 (même argumentation que
`recherche_publique`) plutôt qu'un coefficient inventé, doublement arbitraire ici (ampleur ET
signe). Hors périmètre de `ventilation_taille.py` par nature (subvention à des caisses de
retraite de ménages pensionnés, pas une mesure touchant des entreprises par taille).

**Fichiers modifiés :**
- `budget_simulator/constants.py` : nouvelles sections "Crédit d'impôt recherche (CIR)" et
  "Régimes spéciaux de retraite" (montants, effet de levier, coefficients, clé de taille
  d'entreprise, sources détaillées).
- `budget_simulator/handlers/investissements.py` : nouveau handler
  `_apply_credit_impot_recherche`, import des nouvelles constantes, docstring de module.
- `budget_simulator/handlers/depenses.py` : nouveau handler
  `_apply_regimes_speciaux_retraite`, import de la nouvelle constante.
- `budget_simulator/simulator.py` : 2 nouvelles entrées dans `self.measure_handlers`
  (modification du moteur original, AGPL §5).
- `budget_simulator/config.py` : 2 nouveaux défauts (`credit_impot_recherche`,
  `regimes_speciaux_retraite`) dans `load_default_values` (modification du moteur original,
  AGPL §5).
- `budget_simulator/decile.py` : docstring mis à jour, les 2 mesures listées comme
  examinées et laissées non ventilées, avec la raison précise pour chacune.
- `budget_simulator/ventilation_taille.py` : nouvelle clé sourcée `credit_impot_recherche`
  (PME/ETI/GE) ; `regimes_speciaux_retraite` documentée comme hors périmètre par nature.
- `policy_measures.json` : 2 nouvelles entrées (47 → 49 mesures), tooltips citant les sources.
- `tests/test_mixin_architecture.py` : `_EXPECTED_HANDLER_COUNT` 44 → 46 (constante maintenue
  à la main, cf. commentaire dans le fichier).

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
EXACTEMENT le même bucket pré-existant (registre `tests/snapshots/measure_registry.json`
périmé — désormais enrichi de `credit_impot_recherche`/`regimes_speciaux_retraite` dans la
liste des paramètres "morts" déjà signalée pour tous les leviers des lots précédents, pas une
régression nouvelle). Serveur `uvicorn api:app --port 8099` démarré (appel séparé de `curl`,
comme demandé) et testé via `curl` : `/simulate` avec `credit_impot_recherche.montant=2.0`
(rabot de 4,6 Md€ vs le défaut 6,6) produit bien `recettes +4.6 Md€` et `competitivite -0.0093`
sans crash ; `/simulate` avec `regimes_speciaux_retraite.montant=2.0` (économie de 4,0 Md€ vs le
défaut 6,0) produit bien un Déficit réduit de l'ordre de grandeur attendu, Gini et pouvoir
d'achat inchangés (0, comme documenté), sans crash.

## 2026-10 — 4 nouvelles clés de ventilation (décile/taille) identifiées par une passe d'audit

Suite à une passe de recherche dédiée, 4 mesures déjà présentes dans le moteur ont pu recevoir
une clé de ventilation décile ou taille d'entreprise SANS inventer aucune hypothèse : soit en
réutilisant une clé déjà sourcée pour un périmètre proche (`asu`, `fraude_sociale`), soit parce
que le périmètre même de la mesure (seuil légal) la place intégralement dans une seule catégorie
(`isf_climatique`, `taxe_superprofits`) — même principe que `cdhr`/`taxe_holdings_patrimoniales`
(décile) et `niches_fiscales_tge`/`ttf`/`taxe_gafa` (taille) déjà présents.

- **`asu`** (`handlers/depenses.py::_apply_asu`) — décile. Périmètre confirmé par le handler :
  RSA + prime d'activité + APL (PAS les allocations familiales). RÉUTILISE la clé déjà sourcée
  de `prestations_indexation`/`coupe_prestations` (DSS/DREES, REPSS Famille éd. 2025), avec un
  `note_rapprochement` explicite signalant que la base de l'ASU est plus étroite (hors
  allocations familiales, moins concentrées sur les bas déciles que RSA/PA/APL) — contrairement
  à `coupe_prestations`, qui partage EXACTEMENT la même base de 90 Md€ que
  `prestations_indexation` et n'a donc pas besoin de cette réserve.
- **`fraude_sociale`** (`handlers/efficience.py::_apply_fraude_sociale`) — décile. Périmètre
  confirmé encore plus étroit : RSA + APL uniquement (ni prime d'activité, ni allocations
  familiales). Même réutilisation de la clé `prestations_indexation`, avec son propre
  `note_rapprochement` signalant un sous-ensemble plus étroit encore que celui de l'ASU.
- **`isf_climatique`** (`handlers/fiscalite_menages.py::_apply_isf_climatique`) — décile, 100%
  D10. Le handler lui-même borne la population concernée à 130k-500k foyers (top 0,5% à 3% des
  patrimoines, IPP 2024), seuil de patrimoine 0,8 à 2,0 M€ : entièrement au-dessus du seuil
  d'entrée de D10 (~48,6k€/an de niveau de vie). Même construction que `cdhr`/
  `taxe_holdings_patrimoniales` ; même disclaimer déjà utilisé pour `fiscalite_patrimoine`/
  `impot_societes` sur la convention proxy niveau-de-vie (revenu) vs assiette patrimoniale.
- **`taxe_superprofits`** (`handlers/additionnels.py::_apply_taxe_superprofits`) —
  `ventilation_taille.py`, 100% GE. Le handler cible des entreprises à seuil de chiffre
  d'affaires 1 à 1,5 Md€ (~400 entreprises, secteurs énergie/banques/luxe/tech) : catégorie
  "grande entreprise" sans ambiguïté au sens de la taxonomie INSEE par taille. Même construction
  que `niches_fiscales_tge`/`ttf`/`taxe_gafa`.

**Fichiers modifiés :**
- `budget_simulator/decile.py` : 3 nouvelles entrées `DECILE_SHARES` (`asu`, `fraude_sociale`,
  `isf_climatique`).
- `budget_simulator/ventilation_taille.py` : 1 nouvelle entrée `TAILLE_SHARES`
  (`taxe_superprofits`) ; docstring de module mis à jour (retrait de `taxe_superprofits` de la
  liste des mesures "sans clé sourcée à ce stade").

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
EXACTEMENT le même bucket pré-existant (inchangé par rapport à la vérification précédente dans
ce fichier). Serveur `uvicorn api:app --port 8099` démarré (appel séparé de `curl`, comme
demandé) et testé via `curl` : `POST /simulate_decile` avec `fraude_sociale`+`isf_climatique`
actifs ensemble → `decile.par_mesure` contient bien les deux, `fraude_sociale` ventilé selon la
clé `prestations_indexation` (concentration D1 > D10) et `isf_climatique` à 100% sur D10
(7,68 Md€) ; `asu` testé séparément (`asu_activation=1`) → apparaît ventilé selon la même clé
(D1 0,92 Md€ ... D10 0,08 Md€) ; `taxe_superprofits` (`intensite=1.0`) → apparaît dans
`ventilation_taille.par_mesure` à 100% GE (15,0 Md€), absent de `mesures_non_ventilees` des deux
modules.

## 2026-10-02 — Ventilation taille : nouvelle clé `exoneration_heures_sup`, progrès partiel documenté pour `cotisations_patronales` (source PLFSS 2026, Annexe 4)

Lecture précise (pdfplumber) du PDF fourni `PLFSS2026-Annexe4.pdf` ("Présentation des mesures
de réduction et d'exonération de cotisations et contributions"), pour vérifier si une clé
sourcée par taille d'entreprise existait désormais pour deux mesures jusqu'ici non ventilées
dans `budget_simulator/ventilation_taille.py`.

- **`cotisations_patronales`** — **progrès partiel documenté, PAS d'entrée `TAILLE_SHARES`
  ajoutée** (reste dans `mesures_non_ventilees`). Source : Tableau 5 "Masse salariale (secteur
  privé) et exonérations par taille d'entreprise en 2024" (PLFSS 2026, Annexe 4, p. 24), source
  URSSAF Caisse Nationale — DSN 2024, colonne "Structure des exonérations générales (%)" : 0 à
  9 = 25,2% ; 10 à 19 = 12,1% ; 20 à 49 = 15,3% ; 50 à 99 = 9,3% ; 100 à 249 = 10,6% ; 250 à
  499 = 6,1% ; 500 et plus = 21,4%. Ceci donne désormais une part MIC propre (25,2%) et une
  part PME propre (10-249 salariés = 12,1+15,3+9,3+10,6 = 47,3%), les deux exactement alignées
  sur les seuils INSEE. En revanche, la table s'arrête à "500 et plus" (21,4%), qui mélange
  ETI (500-4999 salariés) et GE (5000+) sans les distinguer — combiné aux 6,1% de la tranche
  "250-499" (ETI pure), le solde ETI+GE (27,5%) reste non séparable avec cette seule source.
  Recherche dédiée effectuée (URSSAF open data "exos-secteur-prive-tranche-ent", INSEE "Les
  entreprises en France", Bpifrance Le Lab) sans trouver de publication comparable qui
  subdivise le segment "500 et plus salariés" en tranches plus fines (ex. 500-999/1000-4999/
  5000+) à un niveau d'exonérations ou de masse salariale exploitable — seules des données de
  comptage/effectifs existent à ce niveau de détail, ce qui ne donne qu'une clé de POPULATION,
  pas de MONTANT d'exonération (même lacune que le précédent déjà écarté pour
  `quotient_conjugal` : une pondération de population seule, sans montant correspondant, est
  jugée insuffisante). Plutôt que d'inventer une répartition ETI/GE du solde de 27,5%, la
  mesure reste "non ventilée" ; le docstring de `ventilation_taille.py` documente ce point en
  détail pour qu'un futur mainteneur sache exactement ce qui est désormais sourcé (MIC/PME) et
  ce qui manque encore (ETI/GE).
- **`exoneration_heures_sup`** — **nouvelle entrée `TAILLE_SHARES` ajoutée**, MIC 57,798%
  / PME 42,202% / ETI 0% / GE 0%. Source : PLFSS 2026, Annexe 4, Tableau 13 (p. 45-46) et
  Tableau 22 (p. 53), ligne "Déductions sur les heures supplémentaires (entreprises de moins
  250 salariés)", colonne 2026 (P), données CCSS d'octobre 2025 : total 872 M€, dont
  entreprises de moins de 20 salariés 504 M€ (57,8%), dont entreprises d'au moins 20 et de
  moins de 250 salariés 368 M€ (42,2%). Contradiction apparente levée en lisant intégralement
  la section 1.3.2 (p. 25) : la 2e LFR 2012 (article 3) a bien restreint la déduction
  forfaitaire PATRONALE aux entreprises de moins de 20 salariés, mais l'article 2 de la loi
  n° 2022-1158 du 16 août 2022 a ensuite créé un SECOND dispositif de déduction forfaitaire
  (0,50 €/heure), à compter du 1er octobre 2022, pour les entreprises d'au moins 20 et de moins
  de 250 salariés — les deux dispositifs coexistent aujourd'hui et couvrent ensemble tout le
  périmètre "moins de 250 salariés" documenté par les Tableaux 13/16/22 ; il n'y a donc pas de
  contradiction mais une extension législative postérieure au texte historique de la page 25.
  ETI=0%/GE=0% justifiés par ce plafond légal strict à 250 salariés. `note_rapprochement`
  signale explicitement que la source utilise un seuil légal de 20 salariés et non le seuil
  INSEE de la catégorie MIC (0-9) : la tranche 10-19 (PME au sens INSEE) est donc incluse dans
  la part "MIC" faute de source isolant le seuil 0-9 pour ce dispositif précis.

**Fichiers modifiés :**
- `budget_simulator/ventilation_taille.py` : 1 nouvelle entrée `TAILLE_SHARES`
  (`exoneration_heures_sup`) ; docstring de module mis à jour (retrait d'`exoneration_heures_sup`
  de la liste des mesures sans clé, et remplacement du paragraphe générique sur
  `cotisations_patronales` par une explication détaillée et chiffrée de ce qui est désormais
  résolu — MIC/PME — et de ce qui reste non résolu — ETI/GE).

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
EXACTEMENT le même bucket pré-existant (vérifié par comparaison directe : en restaurant
temporairement l'ancienne version de `ventilation_taille.py`, la suite donne le même résultat
exact `2 failed, 1277 passed, 87 skipped, 7 errors` — confirmant qu'aucune régression n'a été
introduite). Un premier essai de part MIC à 3 décimales (0,578) avait fait apparaître une
collision purement fortuite avec un test-propriété non lié
(`tests/test_emploi_seniors_v061.py::test_p8_aucun_litteral_de_calibration_seniors_hors_constants`,
qui interdit la réutilisation littérale, n'importe où dans le package, de constantes de
calibration du canal "emploi seniors" — `0,578` apparaît par coïncidence dans
`ABSORPTION_OFFRE_SENIORS`/`PHASING_OFFRE_SENIORS` de `constants.py`, sans aucun rapport avec
la taille d'entreprise) ; corrigé en utilisant 5 décimales (0,57798/0,42202, dont la somme
reste exactement 1,0) pour lever la collision sans changer la valeur réelle. Serveur `uvicorn
api:app --port 8099` démarré (appel séparé de `curl`, comme demandé) et testé via `curl` :
`POST /simulate_decile` avec `cotisations_patronales`+`exoneration_heures_sup` actifs ensemble
→ `exoneration_heures_sup` apparaît bien ventilé dans `ventilation_taille.par_mesure` (MIC/PME
seulement, ETI/GE à 0), et `cotisations_patronales` reste bien dans `mesures_non_ventilees`,
comme attendu.

## 2026-10-02 — Ventilation décile `sante` résolue (source DREES/Ines-Omar) ; `abattement_retraites` examinée, laissée non ventilée (OFCE/Ines, données insuffisantes)

**`sante` (handlers/depenses.py::_apply_sante) — RÉSOLU.** Nouvelle entrée `DECILE_SHARES['sante']`
dans `budget_simulator/decile.py`, construite à partir du **remboursement AMO (assurance
maladie obligatoire) moyen par ménage et par décile** publié par DREES, *La complémentaire
santé*, édition 2024, Fiche 15 « Le poids de la santé dans le revenu des ménages », Graphique 1
« Partage de la dépense de santé entre financeurs selon le niveau de vie du ménage, en 2019 »
(modèle de microsimulation Ines-Omar 2019) : D1 4266€, D2 7331€, D3 5864€, D4 6896€, D5 4877€,
D6 5844€, D7 5592€, D8 4048€, D9 4993€, D10 4415€. Un montant MOYEN PAR MÉNAGE et par décile se
convertit directement en part de la masse totale (les déciles ayant, par construction, la même
population) sans nécessiter de source de pondération séparée — à la différence du cas
`quotient_conjugal` (Insee Analyses n°53, rejeté dans le docstring du module), où les montants
publiés ne couvraient qu'une SOUS-population de taille inégale par décile. Parts calculées :
`[0.07882, 0.13544, 0.10834, 0.12741, 0.0901, 0.10797, 0.10331, 0.07479, 0.09225, 0.08157]`
(somme = 1.0 exactement). `DD135` (DREES, *Les Dossiers de la DREES* n°135, « Dérembourser des
soins », février 2026) a été vérifié pour une clé plus spécifique au déremboursement visé par
le handler : il ne publie qu'une ventilation par QUINTILE (pas décile) du coût moyen par ménage
de scénarios de déremboursement simulés — moins précis et non convertible en 10 valeurs sans
interpoler, donc non retenu au profit de la table Fiche 15. `note_rapprochement` ajoutée : le
handler `_apply_sante` agrège 3 réformes d'efficience sur la dépense remboursée par l'AMO
(hôpital/ambulatoire/prévention-organisation — périmètre couvert par cette clé) AVEC une
franchise/participation forfaitaire (reste à charge payé directement par les patients, hors
AMO) et un budget de prévention institutionnelle (dépense publique sans remboursement
individualisé) — deux composantes dont le périmètre réel diffère de celui de la clé AMO,
documentées comme approximation. Docstring du module vérifié : `sante` n'apparaissait dans
aucune liste "examinée, non ventilée" existante, donc rien à en retirer.

**`abattement_retraites` (nouvelle mesure, lot 2026-10) — NON RÉSOLU, documenté précisément.**
Source trouvée : OFCE, blog, 18 juillet 2025, « "Stop à la dette" : les retraités largement mis
à contribution » (modèle de microsimulation Ines, Insee/Drees/Cnaf), qui décrit exactement cette
mesure et donne des agrégats nationaux (1,5M ménages gagnants dont 2/3 dans la moitié la plus
aisée des retraités ; 5,2M ménages perdants, surtout parmi les 30% les plus aisés ; solde
budgétaire -300M€ côté gagnants / +1,1Md€ côté perdants). Son « Graphique 1 » ventile bien par
DÉCILE de niveau de vie des retraités, mais croisé avec la composition familiale (retraité·e
seul·e / couple de retraités / autres), et l'onglet capturé dans le PDF fourni (« Gagnants et
perdants par décile ») ne montre que des EFFECTIFS par décile×famille, pas des montants ; le
texte ne donne de montants € que de façon qualitative et agrégée par type de ménage ("pertes
allant de 100€ environ pour les retraités seuls du 10% le plus modeste à près de 1000€ pour les
couples de retraités du 10% le plus aisé" — deux points isolés, pas un tableau à 10 valeurs), et
semble en outre porter sur les 4 mesures du plan "année blanche" combinées (pas l'abattement
seul). Construire un array sourcé nécessiterait soit les poids de population retraité·e-seul·e
vs couple PAR DÉCILE (non publiés — seuls les totaux 1,5M/5,2M et proportions "2/3"/"30%" le
sont, pas de table croisée décile×famille en valeur), soit le CSV sous-jacent au graphique
interactif (bouton "données" visible dans l'article, pointant vers une ressource externe non
accessible depuis ce bac à sable réseau-restreint). Même défaut que `quotient_conjugal` :
des montants réels existent, mais pas la clé de pondération par décile permettant de les
agréger sans inventer une hypothèse. Documentation ajoutée dans le docstring de
`budget_simulator/decile.py` (nouveau paragraphe `abattement_retraites`) ; la mesure reste dans
`mesures_non_ventilees`. Une prochaine passe pourrait reprendre le CSV lié par l'article OFCE si
l'accès réseau le permet.

**Fichiers modifiés :**
- `budget_simulator/decile.py` : nouvelle entrée `DECILE_SHARES['sante']` (source DREES Fiche
  15 / Ines-Omar 2019, avec `note_rapprochement`) ; docstring de module complété d'un nouveau
  paragraphe documentant précisément la limite trouvée pour `abattement_retraites` (non résolue).
- `CHANGES.md` : cette entrée.

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
IDENTIQUE au bucket pré-existant documenté en tête de cette tâche (aucune régression). Serveur
`uvicorn api:app --port 8099` démarré en arrière-plan (appel dédié) puis testé via un appel
`curl` séparé : `POST /simulate_decile` avec `sante` actif (`effort_hopital`/`effort_ambu`/
`effort_prev_org` à 80) → `decile.par_mesure.sante.par_decile` non vide, 10 clés D1..D10 avec
des valeurs Md€ cohérentes avec le total de la mesure et les parts sourcées ci-dessus (ex. D2,
le décile avec la part la plus élevée, porte la valeur absolue la plus élevée). Les 3 PDF de
référence fournis pour cette tâche (`DREES_Fiche15.pdf`, `DD135.pdf`, `OFCE_retraites.pdf`) ont
été supprimés du dépôt après usage (matériel de travail, pas des fichiers du projet).

## 2026-10-02 — Ventilation taille round 4 : `impots_production` résolue, `smic` partiellement documentée, `exonerations_salaires` bloquée

Poursuite de la recherche exhaustive décile/taille ("chercher jusqu'à trouver") sur les mesures
restées non ventilées. Round 4 portait sur 7 mesures (`impot_revenu`, `elargissement_ir`,
`impots_production`, `exonerations_salaires`, `transition_ecologique`, `smic`,
`cotisations_patronales` ETI/GE).

**`impots_production` (taille) — RÉSOLUE**, en combinant deux sources officielles
indépendantes sans inventer de pondération : (1) DGFiP Statistiques n°35 (2025), « Les impôts
de production en 2023 », Tableau 4 (poids moyen en % de la valeur ajoutée par catégorie : GE
3,4%, ETI 2,9%, PME 1,9%, microentreprises exclues du tableau — taux qualifié d'explicitement
« négligeable » par la DGFiP) ; (2) Insee Focus n°372 (décembre 2025), « Le tissu productif
français par catégorie d'entreprises en 2023 » (valeur ajoutée par catégorie : MIC 219,2 Md€,
PME 312,2 Md€, ETI 354,7 Md€, GE 459,1 Md€, total 1 345,2 Md€). En multipliant taux × VA par
catégorie, on obtient un montant réel d'impôts de production (GE 15,61 Md€, ETI 10,29 Md€, PME
5,93 Md€, MIC ≈ 0, total 31,83 Md€), d'où les parts : MIC 0%, PME 18,63%, ETI 32,33%, GE 49,04%.
Deux limites documentées : le taux DGFiP est une moyenne de taux individuels (pas un ratio
agrégat total/total, possible léger écart) ; les microentreprises sont mises à 0% faute de taux
publié séparément.

**`smic` (taille) — PARTIELLEMENT résolue, reste NON ventilée.** Source : Assemblée nationale,
rapport commission des affaires sociales n° l16b0489, tableau « Salariés bénéficiant de la
revalorisation du Smic au 1ᵉʳ janvier 2021, par taille d'entreprise » (Dares, enquêtes Acemo) :
effectifs bénéficiaires par tranche de 1-9 à 500+ salariés, donnant une part MIC propre (24,1%)
et une part PME propre (47,8%, somme 10-249). La tranche « 250 à 499 » (8,7%, ETI pure) est
exploitable, mais « 500 et plus » (5,6%) mélange ETI (500-4999) et GE (5000+) sans les
distinguer — même obstacle déjà rencontré pour `cotisations_patronales`, sans source
complémentaire trouvée pour le lever. De plus, c'est un comptage de salariés (clé de
population), utilisé comme proxy du coût Md€ en supposant un coût par salarié à peu près
uniforme entre tranches — hypothèse raisonnable mais non garantie par la source. Reste dans
`mesures_non_ventilees`, comme `cotisations_patronales`, mais la progression réelle (MIC/PME
résolus) est documentée pour un futur mainteneur.

**`exonerations_salaires` (taille) — NON résolue, piste BLOQUÉE côté réseau.** Jeu de données
open.urssaf.fr « Exonérations de cotisations sociales de l'ensemble des employeurs du secteur
privé, par tranche de taille d'entreprise » (`exos-secteur-prive-tranche-ent`), qui couvre
2004-2025 par tranche d'effectifs et catégorie d'exonération dont la « réduction générale »
(la mesure visée). Domaine open.urssaf.fr inaccessible depuis ce bac à sable (connexion
rejetée par le proxy réseau) — signalé à l'utilisateur pour téléchargement manuel de l'export
CSV si possible.

**`impot_revenu` (décile), `elargissement_ir` (décile), `transition_ecologique` (taille),
`cotisations_patronales` ETI/GE (taille) :** toujours non résolues après ce round. Une piste
`transition_ecologique` (CSIA, « Première évaluation in itinere France 2030 », juin 2023,
Tableau 3) a été examinée et explicitement ÉCARTÉE : elle couvre tous les axes France 2030
(pas seulement la transition écologique), sur une photo partielle à fin avril 2023, sans
catégorie MIC distincte — extrapolation hors-périmètre jugée trop fragile, contrairement à
`impots_production` ci-dessus où les deux sources couvrent exactement le périmètre voulu. Une
piste `impot_revenu` (traitement 100% D10 par construction pour la seule composante
`taux_superieur`, RFR > 160 950€) a été identifiée mais non implémentée : la mesure est gérée
comme un bloc unique dans le moteur, et la découper en sous-mesure pour ventiler seulement une
partie nécessiterait une décision d'architecture non prise sans validation explicite. Un
nouveau document potentiellement utile pour `cotisations_patronales` (Insee,
statistiques/8266010, tranches d'effectifs détaillées fin 2024) a été repéré mais le fichier
Excel/dictionnaire de données lié est inaccessible depuis ce bac à sable (domaine insee.fr
accessible pour les pages mais pas pour ce fichier précis) — signalé à l'utilisateur.

**Fichiers modifiés :**
- `budget_simulator/ventilation_taille.py` : nouvelle entrée `TAILLE_SHARES['impots_production']`
  ; docstring de module complété de paragraphes documentant précisément `smic` (partiel, non
  ventilé) et `exonerations_salaires` (bloqué, piste identifiée).
- `CHANGES.md` : cette entrée.

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
identique au bucket pré-existant documenté en tête de cette tâche (aucune régression — seules
des données/commentaires ont été modifiés, aucun handler). Vérification indépendante des
parts `impots_production` via import Python direct (`sum(shares.values()) == 1.0`).

## 2026-10-02 — `abattement_retraites` résolue (décile) grâce au CSV OFCE fourni par l'utilisateur ; FLORES Insee vérifié, ne résout pas le solde ETI/GE

**`abattement_retraites` (décile) — RÉSOLUE.** L'utilisateur a récupéré manuellement le CSV
sous-jacent au « Graphique 1 » de l'article OFCE (bouton « données », export du modèle de
microsimulation Ines, Insee/Drees/Cnaf), inaccessible directement depuis ce bac à sable réseau-
restreint. Le fichier donne, pour chacune des 30 cellules décile × composition (couples/seuls/
autres), le nombre de ménages (`nb_men`, pondération réelle) et le montant Md€ agrégé de l'effet
« abattement » (`total_abat`, en M€). En sommant `total_abat` sur les 3 compositions pour chaque
décile, on obtient directement un montant net par décile sans inventer de clé : D1 à D3 = 0,
D4 -10M€, D5 -10M€, D6 -90M€, D7 -220M€, D8 -340M€, D9 -500M€, D10 -660M€ (total -1830M€), d'où
les parts : D1-D3 0%, D4 0,55%, D5 0,55%, D6 4,92%, D7 12,02%, D8 18,58%, D9 27,32%, D10 36,07%.
Vérification de cohérence : somme des effectifs gagnants (`g_abat`) = 1 582 000 ≈ « 1,5 million »
du texte de l'article, et perdants (`p_abat`) = 5 218 000 ≈ « 5,2 millions » — confirme qu'il
s'agit bien des données sous-jacentes au même article (pas un export sans rapport). Ceci clôt le
dernier cas « montants réels sans pondération » de la liste des mesures ménages recherchées ce
mois-ci.

**FLORES Insee (`DS_FLORES_A5_TRANCHES_EFFECTIFS` et fichiers associés, transmis par
l'utilisateur) — VÉRIFIÉ, NE RÉSOUT PAS le solde ETI/GE de `cotisations_patronales`/`smic`.**
Ces fichiers (source Insee, Fichier localisé des rémunérations et de l'emploi salarié) donnent le
nombre d'établissements et les effectifs salariés par commune, avec des tranches d'effectifs
allant jusqu'à « 500 salariés et plus » — EXACTEMENT le même plafond que la table PLFSS 2026
Annexe 4 déjà utilisée pour `cotisations_patronales`, donc aucune granularité supplémentaire pour
distinguer ETI (500-4999) de GE (5000+). Par ailleurs ces données sont au niveau ÉTABLISSEMENT
(lieu de travail physique), pas ENTREPRISE (unité légale) : une entreprise de 6000 salariés
répartis sur 20 établissements de 300 apparaîtrait dans la tranche « 20-49 » ou « 50-99 » par
établissement, pas dans « 500 et plus » — ce qui rendrait de toute façon ce fichier inadapté à
une ventilation par catégorie d'ENTREPRISE même s'il allait au-delà de 500. Les autres fichiers
du même lot (A17/A38/A88 = nomenclatures sectorielles plus ou moins fines, ECONOMIC_SPHERE =
secteur public/privé/ménages-employeurs, PE = particuliers employeurs) sont tous des croisements
différents de la même base établissement, avec les mêmes tranches d'effectifs plafonnées à
« 500 et plus » — aucun n'apporte d'information nouvelle pour ce blocage précis. Le solde ETI+GE
(27,5% des exonérations générales pour `cotisations_patronales`, 5,6% des bénéficiaires de la
revalorisation pour `smic`) reste donc non ventilable entre ces deux catégories à ce stade.

**Fichiers modifiés :**
- `budget_simulator/decile.py` : nouvelle entrée `DECILE_SHARES['abattement_retraites']` ;
  paragraphe du docstring remplacé (était "EXAMINÉE, non ventilée", devient "RÉSOLUE").
- `CHANGES.md` : cette entrée.

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
identique au bucket pré-existant (aucune régression). Vérification indépendante des parts via
import Python direct (`sum(shares) == 1.0`). Serveur `uvicorn api:app --port 8099` démarré en
arrière-plan puis testé via un appel `curl` séparé : `POST /simulate_decile` avec
`abattement_retraites.reforme_active=1` → `decile.par_mesure.abattement_retraites.par_decile`
non vide, total 4,0 Md€ réparti D1-D3 à 0 puis croissant jusqu'à D10 = 1,4426 Md€, cohérent avec
« surtout les 30% de retraités les plus aisés ». Le CSV OFCE fourni par l'utilisateur a été
supprimé du dépôt après usage (matériel de travail, pas un fichier du projet) ; les fichiers
FLORES (plusieurs dizaines de Mo, format Insee non lié à ce dépôt) n'ont pas été copiés dans le
dépôt du tout, seulement lus depuis leur emplacement temporaire.

## 2026-10-02 — Premier examen des 11 mesures "dépenses publiques" jamais ventilées côté décile

Jusqu'ici, la recherche décile/taille portait sur les mesures fiscales et sociales. À la
demande de l'utilisateur ("et sur les autres leviers sans ventilation ?"), un audit complet
du moteur a identifié 11 mesures côté dépenses qui n'avaient JAMAIS été examinées pour une
ventilation décile (ni documentées comme hors périmètre, ni comme recherchées sans succès) :
`fraude_fiscale`, `chomage_alloc`, `fonction_publique`, `fonction_publique_reforme`,
`education`, `collectivites`, `defense`, `recherche_publique`, `immigration`,
`optimisation_dette`, `rabot_uniforme`.

**`education` — PISTE SÉRIEUSE, bloquée côté accès réseau.** Insee Analyses n°88 (2023),
« La redistribution élargie... », donne des transferts en nature (éducation, santé,
logement) par groupe de niveau de vie, avec un renvoi explicite (notes des Figures 1/6/7) à
des « données complémentaires » par VINGTIÈME (20 groupes, regroupables 2 par 2 en déciles
sans invention de pondération, même logique que `sante`). Fichier identifié :
`https://www.insee.fr/fr/statistiques/fichier/7669723/donnees_ia88.xlsx` — inaccessible
depuis ce bac à sable (téléchargement direct ET WebFetch bloqués). Signalé à l'utilisateur
pour récupération manuelle.

**Trouvées mais insuffisantes (pas une impasse de recherche, juste la mauvaise granularité) :**
`fraude_fiscale` (Cour des comptes déc. 2025, montants globaux sans ventilation par
contribuable), `chomage_alloc` (l'Insee exclut explicitement l'assurance chômage de ses
tableaux de redistribution, traitée comme revenu de remplacement contributif),
`fonction_publique`/`fonction_publique_reforme` (niveaux de vie MOYENS par catégorie
socioprofessionnelle chez l'Insee, mais sans poids de population par décile — même défaut
que `quotient_conjugal`).

**Hors périmètre de fond, pas une lacune de recherche :** `collectivites` (transfert
inter-administrations), `defense`/`recherche_publique` (biens publics purs, non
individualisables), `immigration` (l'AME cible une population hors du champ des enquêtes
Insee sur les ménages fiscaux français, qui fondent le découpage en déciles),
`optimisation_dette` (opération macro-financière pure), `rabot_uniforme` (coupe composite
sur des lignes déjà non ventilées individuellement — assembler une clé inventerait une
pondération).

**Fichiers modifiés :**
- `budget_simulator/decile.py` : docstring de module complété de 9 nouveaux paragraphes
  documentant précisément le statut de ces 11 mesures (aucune entrée DECILE_SHARES ajoutée
  à ce stade — en attente du fichier Insee pour `education`).
- `CHANGES.md` : cette entrée.

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
identique au bucket pré-existant (modification de commentaires uniquement, aucun code
exécutable touché).

## 2026-10-02 — `education` résolue (décile) grâce au fichier Insee Analyses n°88 fourni par l'utilisateur

L'utilisateur a récupéré et transmis `IA88.xlsx`, le fichier de données associé à l'Insee
Analyses n°88 (2023), « La redistribution élargie... » — bloqué en téléchargement direct et
en WebFetch depuis ce bac à sable. Ce fichier contient en réalité TOUTES les données
(principales ET complémentaires) dans un seul classeur à onglets, dont le **Tableau
complémentaire 4** « Transferts moyens reçus en 2019 par les ménages, selon le niveau de vie » :
la ligne « Éducation » donne le montant moyen de transfert éducatif par VINGTIÈME (V1-V20) de
niveau de vie, en euros par unité de consommation (V1 3700€ ... V20 1950€, profil décroissant
avec le niveau de vie, cohérent avec un service public universel consommé proportionnellement
plus par les ménages modestes avec enfants).

Les vingtièmes étant de taille de population égale par construction (comme les déciles), on les
regroupe directement 2 par 2 (D1=V1+V2, ..., D10=V19+V20) pour obtenir un montant par décile,
sans inventer de pondération — même principe déjà appliqué pour `sante` (DREES Fiche 15). Parts
obtenues : D1 15,56%, D2 12,31%, D3 10,74%, D4 10,13%, D5 9,65%, D6 9,01%, D7 8,53%, D8 8,21%,
D9 7,77%, D10 8,10% (profil globalement décroissant mais avec un léger rebond en D10, fidèle aux
données sources).

**Fichiers modifiés :**
- `budget_simulator/decile.py` : nouvelle entrée `DECILE_SHARES['education']` ; paragraphe du
  docstring remplacé (était "PISTE SÉRIEUSE, NON RÉSOLUE", devient "RÉSOLUE").
- `CHANGES.md` : cette entrée.

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
identique au bucket pré-existant (aucune régression). Vérification indépendante des parts via
import Python direct (`sum(shares) == 1.0`). Serveur `uvicorn api:app --port 8099` démarré en
arrière-plan puis testé via un appel `curl` séparé : `POST /simulate_decile` avec
`education.budget=80` (+15 Md€) → `decile.par_mesure.education.par_decile` non vide, répartition
cohérente avec le profil décroissant de la source (D1 2,33 Md€ → D9 1,17 Md€, léger rebond D10 à
1,21 Md€). Le fichier Insee fourni par l'utilisateur n'a pas été copié dans le dépôt (matériel de
travail externe), seulement lu depuis son emplacement temporaire.

## 2026-10-02 — `chomage_alloc` résolue (décile, même fichier Insee n°88) ; `fraude_fiscale` et `fonction_publique`/`fonction_publique_reforme` réexaminées en profondeur (pistes de combinaison testées et écartées)

**`chomage_alloc` — RÉSOLUE.** Le même fichier Insee n°88 fourni par l'utilisateur pour
`education` contient aussi, dans son Tableau complémentaire 4, une ligne « Chômage et revenus
de remplacement » par vingtième de niveau de vie. Point important : une recherche antérieure
(round 5) avait jugé cette mesure non ventilable car la fiche Insee « Redistribution
monétaire » EXCLUT explicitement l'assurance chômage de son périmètre — mais le document des
comptes nationaux distribués (Insee Analyses n°88) utilise une définition plus large et
l'INCLUT explicitement (le Tableau complémentaire 3 le précise noir sur blanc). Regroupement
2 par 2 en déciles (même méthode qu'`education`) : parts D1 7,79% → D10 13,08%, profil
CROISSANT avec le niveau de vie (contre-intuitif pour une prestation sociale, mais cohérent
avec le caractère proportionnel au salaire antérieur de l'allocation chômage française,
documenté dans la note_rapprochement).

**`fraude_fiscale` — piste de combinaison testée, explicitement ÉCARTÉE.** La Cour des
comptes (déc. 2025) donne les droits rappelés 2024 PAR TYPE D'IMPÔT (IS 4,14 Md€, TVA 2,41 Md€,
IR 1,95 Md€, droits d'enregistrement 3,57 Md€, IFI 0,31 Md€, etc.). L'idée de combiner ce
montant par impôt avec la clé de répartition des PAYEURS normaux de chaque impôt par décile
(même principe que la combinaison réussie pour `impots_production`) a été explorée puis
abandonnée : la Cour des comptes précise elle-même que cette répartition reflète l'INTENSITÉ
DU CONTRÔLE (dossiers à fort enjeu → IS), pas la structure réelle de la fraude par type de
contribuable — combiner reviendrait à inventer une hypothèse que la source elle-même
contredit. Documenté en détail dans le docstring pour qu'un futur mainteneur ne retente pas
la même piste sans relire cette mise en garde.

**`fonction_publique`/`fonction_publique_reforme` — recherche dédiée round 6, rien trouvé.**
Vérifié sans succès : DGAFP (rapports annuels 2023-2025), Insee "Emploi, chômage, revenus du
travail", Insee "Niveaux de vie"/France portrait social — aucune table ne croise secteur
employeur (public/privé) avec décile de niveau de vie du ménage, et aucune combinaison à deux
sources n'est possible faute d'un taux publié à multiplier par un poids de population.

**Fichiers modifiés :**
- `budget_simulator/decile.py` : nouvelle entrée `DECILE_SHARES['chomage_alloc']` ; les trois
  paragraphes du docstring (`chomage_alloc`, `fraude_fiscale`, `fonction_publique`/
  `fonction_publique_reforme`) réécrits pour documenter précisément l'état de la recherche.
- `CHANGES.md` : cette entrée.

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
identique au bucket pré-existant (aucune régression). Vérification indépendante des parts via
import Python direct (`sum(shares) == 1.0`). Serveur `uvicorn api:app --port 8099` testé via
`POST /simulate_decile` avec `chomage_alloc.taux_remplacement=0.7` → ventilation non vide,
cohérente avec le profil croissant documenté (D1 0,4752 Md€ → D10 0,7979 Md€ pour un total de
6,1 Md€).

Il ne reste plus, à ce stade, que 2 vraies lacunes actives côté décile : `impot_revenu`
(décote) et `elargissement_ir`, toutes deux recherchées de façon approfondie sans résultat
(voir entrées précédentes de ce fichier).

## 2026-10-02 — Changement de politique utilisateur : extrapoler avec sources fiables plutôt que laisser non ventilé ; 10 clés décile/taille ajoutées avec flag `"estimation": True`

**Nouvelle directive utilisateur (verbatim)** : « Car si on ne trouve pas : va falloir
extrapoler mais autant le faire en se basant sur des sources fiables tout de même ! Même si
elles sont incomplètes ! dans tous les cas faudra que la ventilation existe (ménages et
entreprise) pour TOUS les leviers concernés. MAIS faut vraiment essayer de se rapprocher de la
vérité le plus possible ! » Ceci **remplace** la règle précédente (« jamais inventer, laisser
non ventilé ») par : chercher une vraie source en priorité ; si aucune n'existe, construire une
extrapolation documentée, ancrée sur la meilleure donnée réelle disponible (même incomplète) ;
toute mesure concernée doit finir avec UNE ventilation ; mais toujours privilégier
l'approximation la moins mauvaise et la plus proche de la vérité réelle.

**Convention technique adoptée pour appliquer cette directive** : chaque entrée extrapolée
reçoit désormais un champ explicite `"estimation": True` (absent = valeur par défaut `False`
pour les clés pleinement sourcées), distinct des clés pleinement sourcées, avec sa méthode
exacte et ses limites documentées en toutes lettres dans `note_rapprochement`. Ce flag est
remonté dans la sortie API (`decile_breakdown()` et `ventilation_taille()`, via
`cfg.get("estimation", False)`) pour que le front puisse, à terme, l'afficher différemment
d'une clé sourcée.

**Ventilation TAILLE (`budget_simulator/ventilation_taille.py`), 4 clés résolues avec
estimation :**
- `cotisations_patronales` : MIC 25,2% / PME 47,3% / ETI 16,342% / GE 11,158% — PLFSS 2026
  Annexe 4 Tableau 5 donne la répartition par taille jusqu'à « 500 salariés et plus » fusionné ;
  seul le partage ETI/GE à l'intérieur de ce dernier bloc est une estimation (voir ratio
  national ci-dessous).
- `smic` : MIC 27,958% / PME 55,452% / ETI 13,202% / GE 3,387% — rapport Assemblée nationale
  (l16b0489), même limite de bloc fusionné « 500+ » à répartir.
- `exonerations_salaires` : MIC 12% / PME 34,8% / ETI 29,481% / GE 23,719% — **correction de
  périmètre importante** : cette mesure modélise l'exonération NFP 2027 sur les
  AUGMENTATIONS de salaire appliquée à toute la masse salariale privée (800 Md€), pas les
  allègements généraux niveau SMIC comme supposé initialement (round 4) — relecture du handler
  `handlers/additionnels.py::_apply_exonerations_salaires` ayant révélé l'erreur. Poids
  recalculé sur la colonne « masse salariale » du PLFSS 2026 Annexe 4 (et non « exonérations »).
  Seul le solde ETI/GE reste une estimation.
- `transition_ecologique` (nouvelle clé, absente jusqu'ici) : MIC 0% / PME 54,433% / ETI
  13,054% / GE 32,512% — ancrée sur les données CSIA/France 2030 par taille de bénéficiaire ;
  limites plus importantes et non résolues, documentées dans `note_rapprochement`.

**Outil commun aux 3 premières clés ci-dessus — ratio ETI/GE national** : le champ
« 500 salariés et plus » recoupe TOUTES les tables françaises de taille trouvées à ce jour
(PLFSS Annexe 4, DARES/Assemblée nationale, FLORES Insee). Pour le scinder sans l'inventer, on
utilise le ratio réel d'effectifs ETI/GE 2023 (Insee Focus n°372, vérifié par WebFetch direct :
ETI 3 826,0 milliers d'ETP = 25,8% de l'emploi salarié marchand, GE 4 167,9 milliers d'ETP =
28,1%, soit, UNIQUEMENT à l'intérieur du total ETI+GE : ETI 47,861% / GE 52,139%) appliqué au
bloc fusionné de chaque mesure. Limite documentée : ce ratio national peut ne pas correspondre
au ratio réel de la sous-population spécifique à chaque mesure (ex. la dynamique salariale ou
d'exonération peut différer entre ETI et GE).

**Ventilation DÉCILE (`budget_simulator/decile.py`), 6 clés résolues avec estimation :**
- `taxe_zucman` : 100% D10 — par construction légale, ne concerne que ~1 800 foyers détenant
  plus de 100 M€ de patrimoine net, très au-dessus du seuil d'entrée de D10.
- `regimes_speciaux_retraite` : réutilisation PAR PROXY de la clé `retraites` existante
  (pensions en général) faute de table spécifique aux régimes spéciaux SNCF/RATP/ENIM/CANSSM ;
  biais documenté et non corrigé (la Cour des comptes signale des pensions moyennes
  supérieures pour certains régimes spéciaux, donc cette clé proxy sous-estime probablement
  D8-D10).
- `impot_revenu` (décote) : `[5%, 30%, 40%, 20%, 5%, 0%, 0%, 0%, 0%, 0%]` — clé STRUCTURELLE
  construite à partir des seuils réels de décile Insee Première n°2117 (D1=13 970€,
  D2=17 700€, D3=20 980€, D4=23 880€/UC) pour placer la fenêtre de revenu concernée par la
  décote. **Limite architecturale importante** : le handler `_apply_impot_revenu` combine dans
  un seul delta la décote ET le taux de la tranche supérieure (`taux_superieur`, 100% D10) —
  cette clé unique n'est fiable que lorsque `taux_superieur` reste proche de son défaut ; une
  correction propre nécessiterait de scinder la mesure en deux dans le moteur (hors périmètre
  de cette tâche).
- `elargissement_ir` : `[0%, 0%, 0%, 50%, 35%, 15%, 0%, 0%, 0%, 0%]` — reprend la fourchette
  D4-D6 déjà présente (non sourcée) dans un commentaire du handler `_apply_elargissement_ir`
  lui-même, pondérée vers D4 (plus proche du revenu moyen de 18 000€ annoncé par ce
  commentaire). Estimation à deux niveaux : la fourchette D4-D6 vient du code, pas d'une étude ;
  la pondération interne est notre choix.
- `fonction_publique` / `fonction_publique_reforme` : forme qualitative en cloche centrée
  D5-D7 (`[6%,8%,10%,12%,13%,13%,13%,11%,8%,6%]`), construite à partir du rapport DGAFP
  « Rémunérations dans la fonction publique » 2025, qui montre les salaires publics supérieurs
  aux salaires privés jusqu'au 7e décile de SALAIRE puis inférieurs à partir du 9e. Limite
  documentée : ce sont des déciles de SALAIRE individuel, pas de niveau de vie du MÉNAGE (pas
  de table croisant les deux).

**Décision explicite de NE PAS extrapoler `fraude_fiscale`** malgré la nouvelle politique
permissive : la seule source disponible (Cour des comptes, déc. 2025) prévient ELLE-MÊME que
sa répartition du recouvrement par type d'impôt reflète l'intensité du contrôle fiscal, pas la
structure réelle de la fraude par profil de contribuable. Forcer une clé décile ici irait donc
à l'encontre de l'objectif premier de la directive utilisateur (« se rapprocher de la vérité »)
— c'est le seul cas où le choix a été de maintenir la mesure non ventilée malgré la nouvelle
politique, documenté en détail dans le docstring pour qu'un futur mainteneur comprenne que ce
n'est pas un oubli.

**Fichiers modifiés :**
- `budget_simulator/decile.py` : 6 nouvelles entrées `DECILE_SHARES` (`taxe_zucman`,
  `regimes_speciaux_retraite`, `impot_revenu`, `elargissement_ir`, `fonction_publique`,
  `fonction_publique_reforme`) ; ajout du champ `"estimation"` à la sortie de
  `decile_breakdown()` ; docstring complété avec les paragraphes de statut correspondants.
- `budget_simulator/ventilation_taille.py` : 4 entrées `TAILLE_SHARES` résolues/ajoutées
  (`cotisations_patronales`, `smic`, `exonerations_salaires`, `transition_ecologique`) ; ajout
  du champ `"estimation"` à la sortie de `ventilation_taille()` ; nouveau paragraphe de
  docstring expliquant la convention `"estimation"`.
- `CHANGES.md` : cette entrée.

**Tests effectués :** suite `pytest` complète → `2 failed, 1277 passed, 87 skipped, 7 errors`,
identique au bucket pré-existant (aucune régression introduite par ces changements, tous
limités aux données/docstrings de `decile.py` et `ventilation_taille.py`, pas à la logique des
handlers). Vérification indépendante de chaque nouvelle entrée via import Python direct
(`sum(shares) == 1.0` pour les 6 clés décile, `sum(shares.values()) == 1.0` pour les 4 clés
taille). Tests API live via `uvicorn api:app --port 8099` + `POST /simulate_decile` pour
`impot_revenu` et `elargissement_ir` (ventilation non vide, cohérente avec les profils
documentés, champ `"estimation": true` bien présent dans la réponse JSON) et via
`POST /simulate_taille` (round précédent) pour les 4 clés taille.

**Bilan de couverture à ce stade** : sur les 49 mesures du moteur, une seule reste
délibérément non ventilée côté décile pour une raison de fond documentée (`fraude_fiscale`) ;
toutes les autres mesures concernées par une ventilation ménage et/ou entreprise disposent
désormais d'une clé, sourcée ou explicitement marquée `"estimation": True` avec sa méthode et
ses limites en toutes lettres.

## 2026-10-02 — Fusion des 5 maquettes compactes validées en une seule page de production (`frontend/index.html`) + ajout des 8 mesures manquantes + nouvel onglet « Analyse (taille) »

**Demande utilisateur** : « basculer sur le vrai moteur fusionné ». Les 5 maquettes compactes
par catégorie (`mockup_fiscalite_compact.html`, `mockup_social_compact.html`,
`mockup_depenses_compact.html`, `mockup_competitivite_compact.html`,
`mockup_economie_compact.html`) avaient chacune été construite et validée séparément, déjà
rebranchées sur le vrai moteur (`/simulate_decile`) mais jamais réunies. `frontend/index.html`
(page de production réelle, déployée) était resté sur l'ancien design de carte (liste plate,
pas de repli/dépli) et, découverte faite en préparant cette fusion, **ne couvrait plus que 36
mesures sur 49** (`policy_measures.json`) : 13 mesures ajoutées à l'moteur dans des lots
ultérieurs n'avaient jamais été répercutées dans la page de production.

**Ce qui a été fait** : `frontend/index.html` entièrement reconstruit (1720 lignes, fichier
HTML autonome unique, aucune dépendance externe nouvelle) :
- Panneau de leviers : remplacement du rendu "carte plate" par le design "carte compacte"
  validé dans les 5 maquettes (repliée par défaut à 104px, interrupteur propre, dépli au clic,
  chiffrage "avec ce réglage" calculé en direct, réglages fins rangés dans la carte parente),
  pour les 5 catégories (fiscalite/social/depenses/competitivite/economie).
- Bandeau "compare-bar" (Finances publiques / Pouvoir d'achat / Compétitivité, avec détail
  décile et détail taille d'entreprise dépliables en direct) repris des maquettes, remplaçant
  l'ancienne rangée de KPI simple.
- Conservé de l'ancienne page de production : onglets "Graphiques" (séries multi-années vs
  statu quo vs scénario comparé), "Tableau" (impact par mesure, dernière année), "Analyse
  (décile)", et le sélecteur de comparaison à un scénario prédéfini (`/scenarios`).
- **Nouvel onglet "Analyse (taille)"**, miroir exact d'"Analyse (décile)" mais pour la
  ventilation par taille d'entreprise (`data.ventilation_taille`, même structure que
  `data.decile` : `par_mesure`/`total_par_categorie`/`mesures_non_ventilees`) : 4 barres
  MIC/PME/ETI/GE, tableau par mesure, liste des mesures non ventilées par taille.
- **8 mesures ajoutées** (absentes des 5 maquettes ET de l'ancienne page de production, car
  introduites dans des lots postérieurs à leur construction) : `quotient_familial`,
  `quotient_conjugal`, `pfu_bareme`, `taxe_zucman`, `accises` (fiscalité), `coupe_prestations`,
  `regimes_speciaux_retraite` (social), `credit_impot_recherche` (compétitivité, ajoutée au
  thème "Fiscalité générale des entreprises" aux côtés de `cotisations_patronales`/
  `impots_production`). Cartes construites dans le même style visuel, bornes/défauts/tooltips
  repris tels quels de `policy_measures.json`, drapeaux décile/taille vérifiés contre
  `decile.py`/`ventilation_taille.py` (ex. `taxe_zucman` et `regimes_speciaux_retraite` ventilés
  décile avec `estimation: True`, `credit_impot_recherche` ventilé taille uniquement).
- Badge "⚠ estimation" ajouté dans les tableaux Analyse (décile) et (taille) pour toute mesure
  dont la clé est marquée `"estimation": True` côté moteur (aucune maquette n'avait encore ce
  cas de figure visuellement traité).

**Bug trouvé et corrigé pendant les tests** : `refreshCounts()` (repris tel quel des maquettes,
qui n'avaient toujours qu'une seule catégorie dans le DOM) plantait (`Cannot set properties of
null`) en activant un levier, car la page fusionnée n'injecte dans le DOM que la catégorie
active. Corrigé par une garde nulle.

**Tests effectués** : suite `pytest` complète inchangée (`2 failed, 1277 passed, 87 skipped, 7
errors`, aucun fichier Python modifié). Vérification indépendante que les 49 identifiants de
`policy_measures.json` sont tous présents exactement une fois dans la page (0 manquant, 0
inventé). Syntaxe JS validée (`node --check`). Aucun id DOM dupliqué. Test Playwright headless
(Chromium préinstallé) : les 5 onglets de catégorie affichent des cartes, dépli/réglage de
`taxe_zucman` et `credit_impot_recherche` (nouvelles mesures) confirmés en direct contre l'API,
onglet "Analyse (taille)" vérifié (barres + tableau + non-ventilées), aucune erreur console/page
hormis un 404 `favicon.ico` sans conséquence. Vérification manuelle complémentaire (`curl` sur
`/simulate_decile` avec `taxe_zucman`/`credit_impot_recherche` actifs) : `estimation: true` bien
présent côté décile, `credit_impot_recherche` bien présent côté `ventilation_taille`.

**Fichiers modifiés :** `frontend/index.html` (reconstruit intégralement). `CHANGES.md` : cette
entrée. Les 5 fichiers `mockup_*_compact.html` sont conservés tels quels (matériel de travail
historique, non supprimés).

**Limite connue, non bloquante** : sur le graphique à barres décile/taille, l'étiquette de
valeur et l'étiquette de catégorie peuvent légèrement se chevaucher pour une barre proche du
maximum de l'échelle — défaut cosmétique hérité du graphique décile original de la page de
production (pas introduit par cette fusion), non corrigé faute de périmètre.

## 2026-10-04 — Banc d'essai de documents programmatiques : curseurs élargis, libellés alignés

Un banc d'essai a traduit en réglages de nos leviers les chiffrages de plusieurs livrets
(chômage, effectifs publics, enseignants, cotisations, impôts de production, fraude). Résultats
et écarts : `Banc_essai_programmes.xlsx`. Conséquences, sans changer aucun coefficient de calcul :

- **Curseurs élargis** (`policy_measures.json`, `frontend/index.html`) :
  `chomage_alloc.montant` min 27,5 → 21,4 Md€ (le domaine `_CHOMAGE_TAUX_DOMAINE` de
  `constants.py` passe de 0,45–0,80 à 0,35–0,80, dont le montant dérive) ;
  `fonction_publique.effectifs` min −100 000 → −150 000 (toujours plafonné par le vivier de départs) ;
  `education.enseignants` min −20 000 → −120 000.
- **Libellé fraude fiscale** : la « cible 0-30 Md€ » est un montant BRUT détecté ; le net est ≈ 53 %
  (68 % recouvrés − 15 % de coûts de contrôle) avec montée en charge sur 5 ans. Texte précisé ; calcul inchangé.
- **Cotisations patronales : base recalée** (`constants.MASSE_SALARIALE_BRUTE_PCT_PIB` = 0,38, avant 0,48 en dur dans le handler).
  Le 0,48 était proche de la rémunération totale (≈ 51 % du PIB, qui inclut déjà les cotisations) : 27 % dessus donnait ≈ 390 Md€
  (1 point ≈ 14,4 Md€). Sources : Insee comptes nationaux base 2020, tables 6.204 (1 502,9 Md€) et 6.205 (salaires bruts 1 108,5 Md€
  en 2024, ≈ 38 % du PIB) ; FIPECO « Les cotisations sociales » (20/06/2026 : patronales ≈ 10 % du PIB ≈ 300 Md€). Contrôle : 27 % × 1 108,5 ≈ 299 Md€.
  Effet : 1 point ≈ 11,5 Md€ (2026) ; tous les résultats de ce levier perdent ≈ 21 % d'ampleur. Libellé UI aligné.
- **ASU** : le coût (et non l'économie) est voulu et documenté dans le handler (source : mission flash AN, juillet 2025). Aucun changement.
- Tests : baseline inchangée (3 échecs et 7 erreurs préexistants dus au registre périmé).

## 2026-10-04 — Lecture triple État / Sécurité sociale / Collectivités dans le bandeau « Finances publiques »

- Le moteur reste consolidé (administrations publiques). Le bandeau affiche en plus, sous les tuiles Finances publiques,
  trois tuiles : solde 2025 de chaque budget (Insee, Informations rapides n°78 : État −128,1 + ODAC −2,1 ; ASSO −6,7 ; APUL −15,6 ; total −152,5 Md€)
  et contribution des réformes activées (effet direct, Md€/an, avant effets macro).
- Répartition par levier : table `BUDGET_SHARES` dans `frontend/index.html` ([État+ODAC, Sécu, Collectivités], somme = 1, 50 leviers).
  **Clés indicatives, à valider levier par levier** (voir `Table_affectation_budgets.xlsx`). La somme des trois tuiles égale le total « Amélioration nette du solde public ».
- Libellés : titre « Budget de l'État 2030 » → « Finances publiques de la France 2030 » ; légende « Budget de l'État (référence, non modifié) » → « Finances publiques (référence, sans réforme) ».
- Aucun changement de calcul côté moteur.

- Correction (2026-10-04, suite) : clé `csg` passée de [0,05 ; 0,95 ; 0] à [0 ; 1 ; 0]. Source : PLFSS 2026, annexe 3, tableau de répartition des
  impositions affectées à la sécurité sociale (CSG activité, remplacement, patrimoine, placements, jeux : tous les points de CSG sont affectés à
  Cnam, Cnaf, Cnav/FSV, CNSA, CADES ou Unédic, aucun à l'État) ; FIPECO, « L'impôt sur le revenu et la CSG » : la CSG est « affectée à la sécurité sociale ».

## 2026-10-04 — Refonte du bandeau du haut (maquette v13 validée)
- Nouvelle bande pleine largeur : Déficit/PIB (+ Md€), Dette/PIB (+ Md€), PIB, Recettes/PIB, Dépenses/PIB, **Solde primaire/PIB**, **Intérêts de la dette**, avec la ligne « État » de référence sous chaque repère (année 2030).
- Bloc « Emploi, prix & budgets » : Chômage, Inflation, **Croissance moyenne 2026-2030**, lecture État / Sécu / Collectivités, coût net et lien « Détail du coût » sur une ligne.
- Trois blocs de même hauteur ; titre « Répartition de l'effort net… » supprimé (fusionné dans la ligne de total).
- `api.py` : `/simulate_decile` renvoie `interets` (Année, Intérêts_Dette) issu du second DataFrame du moteur ; moteur inchangé. Solde primaire = Déficit + intérêts (en % du PIB).
- Correctif bandeau (aligné sur la maquette v13) : blocs Pouvoir d'achat / Compétitivité compactés (mention « indice national » dans l'en-tête, libellé redondant et liens « Détail » supprimés, détails toujours affichés) → trois blocs de même hauteur (176 px), « Amélioration nette » alignée sur D5.
