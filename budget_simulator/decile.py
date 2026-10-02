"""Module décile — ventilation par décile de niveau de vie des impacts Md€
calculés par le moteur macro-budgétaire (mixins ``handlers/``).

CONTEXTE : ce module N'EST PAS dans le dépôt original cturkieh/france-budget-
simulateur (AGPL-3.0). Il est ajouté par nous pour combler un angle absent de
leur moteur (macro pur : dette/PIB, déficit/PIB, croissance, chômage) : QUI
supporte réellement chaque mesure, ménage par ménage, décile par décile.

MÉTHODE : le moteur original expose déjà, par ``/simulate``, un champ
``report['measure_impacts_by_year']`` donnant le delta Md€ NET (recettes -
dépenses) de chaque mesure, année par année — calculé par leurs handlers
sourcés (IMF/OFCE/IPP/Banque de France/Cour des comptes). On NE RECALCULE
PAS ce delta : on le reprend tel quel et on le multiplie par nos propres clés
de répartition par décile (sourcées séparément, voir DECILE_SHARES
ci-dessous — mêmes sources et mêmes valeurs que le classeur Excel
"Simulateur_Impact_Menages.xlsx" de ce projet, onglet "Chiffrage national").

LIMITES ASSUMÉES (à afficher côté client) :
- Seules les mesures listées dans DECILE_SHARES sont ventilables. Les autres
  n'ont pas de clé de répartition par décile sourcée de notre côté — elles
  restent "non ventilées" plutôt que de se voir attribuer une hypothèse
  inventée. Voir ci-dessous pour les mesures explicitement examinées.
- Mesures « dépenses publiques » jamais examinées avant 2026-10 (round
  dédié "incidence des dépenses par décile de bénéficiaires") :
  - ``education`` : RÉSOLUE (2026-10-02, fichier Insee transmis par
    l'utilisateur). Voir l'entrée ``DECILE_SHARES["education"]`` ci-dessous
    pour le détail de la source (Insee Analyses n°88, Tableau complémentaire
    4, transferts moyens d'éducation par vingtième, regroupés 2 par 2 en
    déciles).
  - ``fraude_fiscale`` : EXAMINÉE EN PROFONDEUR (round 6, piste de
    combinaison testée et explicitement ÉCARTÉE), non ventilée. Cour des
    comptes (déc. 2025), « La lutte contre la fraude fiscale », Tableau n°2
    p.26, donne les droits rappelés 2024 PAR TYPE D'IMPÔT : IS 4,14 Md€, TVA
    2,41 Md€, IR 1,95 Md€, droits d'enregistrement 3,57 Md€, IFI 0,31 Md€,
    taxes locales 0,49 Md€, autres 1,19 Md€ (total 14,04 Md€ brut, distinct
    des 11,4 Md€ nets encaissés). Piste envisagée : combiner ce montant par
    impôt avec la clé de répartition des PAYEURS de chaque impôt par décile
    (ex. celle d'``impot_revenu``/``csg`` pour l'IR) pour approximer une
    ventilation du recouvrement — MÊME PRINCIPE que la combinaison réussie
    pour ``impots_production`` (taux × VA). ÉCARTÉE après lecture : la Cour
    des comptes précise ELLE-MÊME (p.26) que cette répartition par impôt
    reflète l'INTENSITÉ DU CONTRÔLE (l'IS est davantage contrôlé car les
    dossiers à fort enjeu y sont concentrés), PAS la structure réelle de la
    fraude par type de contribuable — appliquer la clé des payeurs normaux
    de chaque impôt à ce montant redresserait une fraude en réalité
    concentrée sur des profils que ces clés de paiement normal ne
    représentent pas (la source elle-même met en garde contre cet usage).
    Combiner les deux reviendrait donc à inventer une hypothèse contredite
    par la source — exactement le type d'erreur que ce module s'interdit.
    Par ailleurs l'IS (impôt sur les sociétés) et les droits d'enregistrement
    n'ont de toute façon pas de clé décile directe dans ce module (l'IS a une
    clé TAILLE d'entreprise, pas décile ménage), et la fraude aux
    cotisations sociales (~1,6 Md€ redressé en 2024 pour travail dissimulé,
    source Urssaf/ACOSS) est suivie séparément, sans détail par type de
    cotisation. La mesure reste non ventilée.
  - ``chomage_alloc`` : RÉSOLUE (2026-10-02, même fichier Insee n°88 que
    pour `education`). Voir l'entrée ``DECILE_SHARES["chomage_alloc"]``
    ci-dessous — la fiche « Redistribution monétaire » de l'Insee exclut
    l'assurance chômage de son périmètre (constat initial, round 5), mais le
    document des comptes nationaux distribués (Insee Analyses n°88) l'inclut
    explicitement dans sa définition élargie et publie un montant par
    vingtième exploitable.
  - ``fonction_publique``, ``fonction_publique_reforme`` : RÉSOLUES avec
    ``"estimation": True`` (directive utilisateur du 2026-10-02). Aucune
    table ne croise secteur public/privé et décile de niveau de vie du
    ménage (recherché sans succès sur 2 rounds : DGAFP, Insee emploi, Insee
    niveaux de vie). Une forme qualitative (cloche centrée D5-D7) est
    construite à partir d'un fait réel mais partiel — le rapport DGAFP
    « Rémunérations dans la fonction publique » 2025 montre une distribution
    salariale compressée côté fonction publique, supérieure au privé jusqu'à
    D7 puis inférieure à partir de D9. Voir
    `DECILE_SHARES["fonction_publique"]` pour le détail et les limites
    (déciles de SALAIRE, pas de niveau de vie du ménage).
  - ``collectivites`` : HORS PÉRIMÈTRE DE FOND, pas une lacune de recherche.
    Les dotations aux collectivités locales (DGF etc.) sont un transfert
    inter-administrations ; aucune statistique française ne les décompose
    par ménage bénéficiaire.
  - ``defense``, ``recherche_publique`` : HORS PÉRIMÈTRE DE FOND. Biens
    publics purs (non rivaux, non exclusifs) — aucune publication française
    (Insee/DREES/Cour des comptes/France Stratégie) ne tente de leur
    attribuer une incidence individualisée par ménage ou décile.
  - ``immigration`` : HORS PÉRIMÈTRE DE FOND. L'AME cible des personnes sans
    statut régulier, hors du champ des enquêtes Insee sur les ménages
    fiscaux français (ERFS/Enquête Revenus Fiscaux) qui fondent le découpage
    en déciles de ce module — aucun pont statistique possible vers D1-D10.
  - ``optimisation_dette`` : HORS PÉRIMÈTRE DE FOND. Opération de
    refinancement macro-financier pur (gestion de taux/maturité), sans aucun
    point de contact avec un ménage.
  - ``rabot_uniforme`` : HORS PÉRIMÈTRE DE FOND à ce stade. Coupe composite
    sur des dizaines de lignes budgétaires elles-mêmes non ventilées
    individuellement (voir ci-dessus) : assembler une clé reviendrait à
    inventer une pondération entre des postes déjà non sourcés.
- ``smic`` (montant_brut ET le sous-paramètre indexation, lot 2026-10) : EXAMINÉ
  et volontairement laissé "non ventilé" à ce stade (2026-10). Aucune publication
  trouvée ne donne la répartition des salariés au SMIC (ou de la masse salariale
  concernée par une revalorisation du SMIC) par décile de NIVEAU DE VIE du
  ménage (la DARES publie des caractéristiques des salariés au SMIC — âge,
  temps partiel, secteur — mais pas de ventilation par décile de niveau de vie
  du ménage, et beaucoup de smicards vivent dans des ménages avec d'autres
  revenus, rendant la conversion salarié -> décile ménage non triviale sans
  microsimulation dédiée). Inventer une clé serait contraire au principe
  ci-dessus ; la mesure reste dans `mesures_non_ventilees` jusqu'à ce qu'une
  source solide soit identifiée.
- ``exoneration_heures_sup`` (nouvelle mesure, lot 2026-10) : même limite —
  aucune clé de répartition par décile sourcée identifiée pour les heures
  supplémentaires (la répartition des heures sup par catégorie d'entreprise,
  pertinente pour `ventilation_taille.py`, a été cherchée mais pas trouvée non
  plus sous forme exploitable, voir ce module).
- ``quotient_familial``, ``quotient_conjugal``, ``pfu_bareme`` (nouvelles
  mesures, lot 2026-10 "grille de tri 12 pistes") : EXAMINÉES et
  volontairement laissées "non ventilées". Pour les deux premières, la
  source trouvée (Insee Analyses n°53, juin 2020, "Les dispositifs conjugaux
  et familiaux réduisent l'impôt sur le revenu de 29,7 milliards d'euros")
  ne publie qu'une concentration AGRÉGÉE conjugal+familial par VINGTILE
  (5% des ménages les plus aisés = 20% des gains ; 25% les plus aisés = 50%
  des gains), ni un tableau décile par décile, ni une ventilation séparée
  par dispositif — insuffisant pour construire 10 parts sourcées sommant à 1
  sans inventer les valeurs intermédiaires. Pour `pfu_bareme`, la seule
  étude distributive trouvée sur le PFU (IPP, note n°46, octobre 2019) ne
  publie aucune répartition par décile des bénéficiaires. Les 3 mesures
  restent dans `mesures_non_ventilees`.
- ``taxe_zucman`` : RÉSOLUE avec ``"estimation": True`` (directive
  utilisateur du 2026-10-02 : extrapoler plutôt que laisser non ventilé, en
  documentant les limites). Par construction, ne concerne que ~1800 foyers
  détenant plus de 100 M€ de patrimoine — très au-dessus du seuil d'entrée
  de D10. Précédemment laissée "non ventilée" par choix de prudence (la
  fraction de D10 concernée est extrêmement étroite, et le rendement varie
  d'un facteur 8 entre l'estimation du proposant et celle de la critique) ;
  voir `DECILE_SHARES["taxe_zucman"]` pour le détail de cette estimation,
  marquée comme moins fiable que `cdhr`/`taxe_holdings_patrimoniales`.
- ``accises`` (nouvelle mesure, lot 2026-10, "accise ok") : EXAMINÉE et
  volontairement laissée "non ventilée". Une étude RÉELLE donnant un taux
  d'effort par décile pour EXACTEMENT ces 3 taxes (TICPE/tabac/alcool) a été
  trouvée — Insee, Ruiz & Trannoy, "Le caractère régressif des taxes
  indirectes", Économie et Statistique n°413 (2008), tableau 4 : tabac 0,91%
  (D1) à 0,13% (D10) du revenu disponible ; alcools 0,47% (D1) à 0,16%
  (D10) ; produits pétroliers/TICPE 2,89% (D1) à 1,00% (D10) ; combinées,
  4,3% (D1) contre 1,3% (D10) — confirmant une régressivité marquée. MAIS
  cette étude ne publie le revenu disponible moyen par décile NULLE PART
  dans le même tableau : convertir un taux d'effort (taxe payée / revenu) en
  PART DE CHARGE par décile (le format attendu ici, 10 parts sommant à 1)
  nécessite de multiplier par le revenu moyen du décile, une donnée qu'il
  faudrait aller chercher dans une AUTRE source Insee et combiner nous-mêmes
  — une reconstruction à deux sources non publiée telle quelle, que ce
  module évite par principe (même limite que `quotient_familial` ci-dessus).
  Le facteur gini/pouvoir d'achat utilisé dans le handler
  (`handlers/fiscalite_menages.py::_apply_accises`) EST calibré par analogie
  sur cette étude (régressivité plus forte que `tva_energie`), mais ce n'est
  pas une clé de décile : `accises` reste dans `mesures_non_ventilees`.
- ``credit_impot_recherche`` (nouvelle mesure, lot 2026-10 "audit comparatif") :
  EXAMINÉE et volontairement laissée "non ventilée" PAR NATURE, pas faute de
  recherche : le CIR est un crédit d'impôt versé à des ENTREPRISES (personnes
  morales), pas à des foyers fiscaux — aucune étude ne peut en principe en
  ventiler l'incidence par décile de niveau de vie du MÉNAGE, de la même
  façon qu'aucune mesure purement "entreprise" de ce moteur (`impots_production`,
  `cotisations_patronales`...) n'a de clé ici. Cette mesure a en revanche une
  clé RÉELLE et sourcée par TAILLE D'ENTREPRISE (voir `ventilation_taille.py`,
  MESR-DGRI 2023), le périmètre pertinent pour un crédit d'impôt aux entreprises.
- ``regimes_speciaux_retraite`` : RÉSOLUE avec ``"estimation": True``
  (directive utilisateur du 2026-10-02). Aucune publication (DREES, Cour des
  comptes) ne ventile spécifiquement les bénéficiaires des régimes SPÉCIAUX
  (SNCF/RATP/ENIM/CANSSM...) par décile de niveau de vie du ménage — la clé
  `retraites` (pensions EN GÉNÉRAL) est réutilisée comme proxy, PAR DÉFAUT
  DE MIEUX, avec un biais documenté et non corrigé : la Cour des comptes
  signale des pensions moyennes de certains régimes spéciaux (ex. SNCF)
  supérieures à la moyenne du régime général, ce qui suggère que cette clé
  proxy sous-estime probablement D8-D10. Voir
  `DECILE_SHARES["regimes_speciaux_retraite"]` pour le détail.
- ``impot_revenu`` (décote) : RÉSOLUE avec ``"estimation": True`` (directive
  utilisateur du 2026-10-02, round 7). Aucune table RÉELLE ne donne la
  répartition des bénéficiaires de la décote par décile. Clé STRUCTURELLE
  construite à partir des seuils réels de décile de niveau de vie (Insee
  Première n°2117, "Niveau de vie et pauvreté en 2024" : D1=13 970€,
  D2=17 700€, D3=20 980€, D4=23 880€ par UC) pour placer la zone de
  plausibilité des foyers concernés par la décote (bas de la distribution,
  concentrée D1-D4). LIMITE ARCHITECTURALE IMPORTANTE, documentée dans
  `DECILE_SHARES["impot_revenu"]["note_rapprochement"]` : le handler
  `_apply_impot_revenu` combine dans UN SEUL `delta_revenue` deux
  sous-mécanismes aux profils très différents (la décote, concentrée bas de
  distribution, ET le taux de la tranche supérieure, 100% D10) — cette clé
  décile unique n'est donc fiable que lorsque `taux_superieur` reste proche
  de son défaut ; une correction propre nécessiterait de scinder la mesure
  en deux dans le moteur, hors périmètre de cette tâche.
- ``elargissement_ir`` : RÉSOLUE avec ``"estimation": True`` (directive
  utilisateur du 2026-10-02, round 7). Le handler `_apply_elargissement_ir`
  suppose lui-même, dans un commentaire interne NON sourcé, que les nouveaux
  contribuables concernés par l'abaissement du seuil d'entrée dans l'IR sont
  des "revenus D4-D6 (classes moyennes basses)" avec un revenu imposable
  moyen de ~18 000€ — cohérent avec la zone D3-D4 des seuils Insee réels
  cités ci-dessus pour `impot_revenu`. La clé reprend cette fourchette D4-D6
  du handler lui-même (on ne l'invente pas) mais la pondère vers D4, plus
  proche du revenu moyen annoncé. ESTIMATION À DEUX NIVEAUX : (1) la
  fourchette D4-D6 elle-même vient d'un commentaire de code non sourcé, pas
  d'une étude ; (2) la pondération interne D4>D5>D6 est notre choix. Voir
  `DECILE_SHARES["elargissement_ir"]` pour le détail complet.
- ``abattement_retraites`` (réexaminée 2026-10, round 4 "chercher jusqu'à
  trouver") : RÉSOLUE. L'utilisateur a récupéré manuellement le CSV sous-jacent
  au "Graphique 1" de l'article OFCE (bouton "données", inaccessible
  directement depuis ce bac à sable réseau-restreint) : OFCE, export du
  modèle de microsimulation Ines (Insee/Drees/Cnaf), colonnes
  ``deciles;compo;nb_men;...;gain_abbat;perte_abbat;total_abat;...`` — 30
  lignes = 10 déciles × 3 compositions (couples/seuls/autres), avec pour
  chaque cellule le NOMBRE DE MÉNAGES (``nb_men``, pondération réelle) et le
  montant Md€ agrégé de l'effet "abattement" (``gain_abbat``/``perte_abbat``/
  ``total_abat``, en M€). En sommant ``total_abat`` sur les 3 compositions
  pour chaque décile (poids réel par ``nb_men``, pas une hypothèse), on
  obtient directement un montant NET par décile sans inventer de clé — même
  logique que ``sante`` ci-dessous (donnée déjà agrégée sur la population
  complète du décile, pas une moyenne sur une sous-population de taille
  inconnue comme c'était le cas pour `quotient_conjugal`). Valeurs obtenues
  (perte nette ménages, M€, signe négatif = coût pour les ménages du décile
  = gain budgétaire, cohérent avec le signe "recettes positif" du moteur) :
  D1 0, D2 0, D3 0, D4 -10, D5 -10, D6 -90, D7 -220, D8 -340, D9 -500,
  D10 -660 (total -1 830 M€). On en tire les parts du total (valeur absolue)
  utilisées comme ``shares`` : D1-D3 à 0%, puis une progression de 0,55% (D4)
  à 36,07% (D10), cohérente avec le texte de l'article ("surtout les 30% de
  retraités les plus aisés" = D8+D9+D10 = 79,2% du total ici). Vérification
  de cohérence : somme de ``g_abat`` (effectifs gagnants, toutes lignes) =
  1 582 000 ≈ "1,5 million" du texte ; somme de ``p_abat`` (perdants) =
  5 218 000 ≈ "5,2 millions" du texte — la correspondance confirme qu'il
  s'agit bien des mêmes données que celles citées dans l'article, pas d'un
  autre export sans rapport.
- Les clés `tva_rate` et `fiscalite_patrimoine` de LEUR moteur ne coïncident
  pas exactement avec nos propres pistes (voir docstring de chaque entrée
  ci-dessous) : rapprochement fait au mieux, à traiter comme un ordre de
  grandeur, pas une identité parfaite.
- Le delta ventilé est celui du PREMIER TOUR (recettes - dépenses, sans
  boucler sur les effets démographiques/croissance de leur moteur macro) —
  cohérent avec la convention "statique" déjà utilisée dans notre classeur
  Excel.
"""
from __future__ import annotations

from typing import Any

DECILES = [f"D{i}" for i in range(1, 11)]

# Chaque entrée : mesure du moteur francebudget.fr -> (shares par décile
# (somme = 1.0), note de méthode/source, note de rapprochement si le
# périmètre des deux mesures n'est pas rigoureusement identique).
DECILE_SHARES: dict[str, dict[str, Any]] = {
    "tva_rate": {
        "shares": [0.02926, 0.04703, 0.06747, 0.07673, 0.09016, 0.09762, 0.10719, 0.11416, 0.13333, 0.23706],
        "source": "CPO/Boutchenik (2015), Tableau 4, décomposition du taux normal de TVA par décile ; DG Trésor Trésor-Éco n°371 (2025) pour la part ménages.",
        "note_rapprochement": "La mesure `tva_rate` de ce moteur modélise un taux de TVA GÉNÉRAL appliqué à toute la consommation (assiette forfaitaire 53% du PIB), alors que nos clés reconstruisent spécifiquement le TAUX NORMAL SEUL. Rapprochement fait par défaut (le taux normal domine la recette TVA), à traiter comme un ordre de grandeur.",
    },
    # Ajoutée 2026-10 (budget_simulator/handlers/nouvelles_taxes_2027.py n'est pas concerné ici,
    # tva_energie existe depuis avant dans fiscalite_menages.py) suite à un signalement
    # utilisateur : ce levier ne bougeait PAS le détail par décile alors qu'il affecte bien
    # l'indice "Pouvoir d'achat" global (impact_pa calculé mais non ventilé). Faute de clé
    # dédiée à la consommation d'énergie par décile, on réutilise la clé TVA générale
    # (CPO/Boutchenik) — LIMITE ASSUMÉE, documentée explicitement : cette clé sous-estime
    # probablement la régressivité réelle d'une taxe sur l'énergie spécifiquement (l'énergie pèse
    # plus lourd, en part du revenu, chez les ménages modestes que la consommation moyenne — voir
    # note_rapprochement). Mieux vaut cette approximation, explicitée, que zéro ventilation.
    "tva_energie": {
        "shares": [0.02926, 0.04703, 0.06747, 0.07673, 0.09016, 0.09762, 0.10719, 0.11416, 0.13333, 0.23706],
        "source": "Réutilisation de la clé TVA générale (CPO/Boutchenik 2015, Tableau 4), faute de clé dédiée à la consommation d'énergie par décile.",
        "note_rapprochement": "Approximation basse : l'énergie représente une part du budget plus élevée chez les ménages modestes que la consommation moyenne (INSEE), donc cette clé sous-estime probablement la régressivité réelle de ce levier — traiter le détail par décile de cette mesure comme un plancher, pas une mesure précise.",
    },
    "csg": {
        "shares": [0.01598, 0.02861, 0.04694, 0.05944, 0.07449, 0.08482, 0.10123, 0.12195, 0.15148, 0.31506],
        "source": "Reconstruction masse des revenus bruts par décile (proxy CSG), voir classeur Excel Simulateur_Impact_Menages.xlsx.",
        "note_rapprochement": None,
    },
    "cotisations_salariales": {
        "shares": [0.01598, 0.02861, 0.04694, 0.05944, 0.07449, 0.08482, 0.10123, 0.12195, 0.15148, 0.31506],
        "source": "Proxy masse salariale brute par décile (même reconstruction que CSG) — voir classeur Excel.",
        "note_rapprochement": None,
    },
    "impot_societes": {
        "shares": [0.0144, 0.0144, 0.0144, 0.0144, 0.0144, 0.065, 0.087, 0.12, 0.177, 0.479],
        "source": "Convention TAXIPP d'incidence de l'IS (répercussion partielle sur les actionnaires/détenteurs de patrimoine) — SPÉCULATIF, voir classeur Excel.",
        "note_rapprochement": None,
    },
    "fiscalite_patrimoine": {
        "shares": [0.0144, 0.0144, 0.0144, 0.0144, 0.0144, 0.065, 0.087, 0.12, 0.177, 0.479],
        "source": "Masse de patrimoine par décile, proxy succession/donation — voir classeur Excel.",
        "note_rapprochement": "Le levier `fiscalite_patrimoine` de ce moteur regroupe IFI + succession + taxe foncière en un seul curseur d'intensité. Nos clés portent spécifiquement sur la masse de patrimoine (succession/IFI) — la composante \"foncière\" n'a pas sa propre clé de décile sourcée ici.",
    },
    "prestations_indexation": {
        "shares": [0.25452, 0.22001, 0.1438, 0.09922, 0.07334, 0.06471, 0.05464, 0.03739, 0.0302, 0.02217],
        "source": "Part de la masse des prestations versées (AF+PAJE+minima/PPA+logement) par décile — DSS/DREES REPSS Famille éd. 2025, voir classeur Excel.",
        "note_rapprochement": None,
    },
    # Ajoutée 2026-10 (handlers/depenses.py::_apply_coupe_prestations, lot "grille de tri
    # 12 pistes") : RÉUTILISE LA MÊME clé que `prestations_indexation` ci-dessus — PAS une
    # nouvelle hypothèse. Les deux mesures portent sur la même base de 90 Md€ (RSA/APL/
    # allocations familiales/autres) et la même population de bénéficiaires ; seul le
    # mécanisme budgétaire diffère (coupe de niveau immédiate vs écart d'indexation
    # cumulatif), ce qui ne change rien à QUI perçoit la prestation coupée.
    "coupe_prestations": {
        "shares": [0.25452, 0.22001, 0.1438, 0.09922, 0.07334, 0.06471, 0.05464, 0.03739, 0.0302, 0.02217],
        "source": "Réutilisation de la clé `prestations_indexation` (DSS/DREES REPSS Famille éd. 2025) : même base de prestations (90 Md€), même population de bénéficiaires, seul le mécanisme budgétaire diffère.",
        "note_rapprochement": None,
    },
    # Ajoutée 2026-10 (handlers/depenses.py::_apply_asu, sourcing v0.6.1) : RÉUTILISE
    # la même clé que `prestations_indexation`/`coupe_prestations` ci-dessus (DSS/DREES),
    # mais le périmètre de l'ASU est plus ÉTROIT que ces deux mesures : RSA + prime
    # d'activité + APL uniquement (PAS les allocations familiales), d'après l'évaluation
    # administrative sourcée dans le handler (mission flash Assemblée nationale, commission
    # des affaires sociales, juillet 2025, restituant les chiffrages DREES/Igas modèle Ines).
    # Pas de clé publiée spécifique à ce sous-périmètre exact : on réutilise la clé la plus
    # proche disponible (même famille de source DSS/DREES), avec un rapprochement explicite.
    "asu": {
        "shares": [0.25452, 0.22001, 0.1438, 0.09922, 0.07334, 0.06471, 0.05464, 0.03739, 0.0302, 0.02217],
        "source": "Réutilisation de la clé `prestations_indexation` (DSS/DREES REPSS Famille éd. 2025), faute de clé publiée spécifique au périmètre RSA + prime d'activité + APL de l'ASU.",
        "note_rapprochement": "Le périmètre réel de l'ASU (RSA + prime d'activité + APL, cf. docstring `_apply_asu`) est PLUS ÉTROIT que la base `prestations_indexation` (qui inclut aussi les allocations familiales). Les allocations familiales sont moins concentrées sur les déciles bas que le RSA/la PA/l'APL (elles ne sont pas, ou peu, sous conditions de ressources) : cette clé sous-estime donc probablement, dans une mesure limitée, la concentration réelle de l'ASU sur les déciles les plus modestes — à traiter comme un ordre de grandeur, pas une identité parfaite.",
    },
    # Ajoutée 2026-10 (handlers/efficience.py::_apply_fraude_sociale) : RÉUTILISE la même
    # clé que `prestations_indexation`/`asu` ci-dessus. Périmètre RSA + APL spécifiquement
    # (cf. docstring `_apply_fraude_sociale`, Cour des comptes, certification des comptes du
    # régime général 2024) : sous-ensemble ENCORE PLUS ÉTROIT que celui de l'ASU (pas de
    # prime d'activité ici).
    "fraude_sociale": {
        "shares": [0.25452, 0.22001, 0.1438, 0.09922, 0.07334, 0.06471, 0.05464, 0.03739, 0.0302, 0.02217],
        "source": "Réutilisation de la clé `prestations_indexation` (DSS/DREES REPSS Famille éd. 2025), faute de clé publiée spécifique au périmètre RSA + APL de la fraude sociale visée.",
        "note_rapprochement": "Le périmètre réel de ce levier (RSA + APL, cf. docstring `_apply_fraude_sociale`) est PLUS ÉTROIT encore que celui de l'ASU (ni prime d'activité, ni allocations familiales) : sous-ensemble parmi les plus concentrés sur les bas déciles de toute la base `prestations_indexation`. Cette clé sous-estime donc probablement la concentration réelle sur les déciles bas — à traiter comme un ordre de grandeur, pas une identité parfaite.",
    },
    "retraites": {
        "shares": [0.03, 0.059, 0.07, 0.08, 0.089, 0.1, 0.112, 0.129, 0.162, 0.17],
        "source": "Part de la masse des pensions de retraite par décile — DREES, Les retraités et les retraites, éd. 2025, voir classeur Excel.",
        "note_rapprochement": None,
    },
    # Ajoutées 2026-10 (budget_simulator/handlers/nouvelles_taxes_2027.py) : 100% D10 non par
    # hypothèse mais parce que le PÉRIMÈTRE LÉGAL de chaque mesure cible explicitement les très
    # hauts revenus/patrimoines (seuils bien au-dessus du seuil d'entrée du décile supérieur) —
    # même principe que le 100% GE des mesures « TGE »/ttf/taxe_gafa de ventilation_taille.py.
    # Ajoutée 2026-10 (handlers/depenses.py::_apply_sante) : clé construite à partir du
    # remboursement AMO moyen par ménage et par décile (Graphique 1, Ines-Omar 2019) — un
    # montant MOYEN PAR MÉNAGE par décile se convertit directement en part de la masse
    # totale, les déciles ayant par construction la même taille de population (pas besoin
    # d'une source de pondération séparée, à la différence de `quotient_conjugal` plus haut).
    "sante": {
        "shares": [0.07882, 0.13544, 0.10834, 0.12741, 0.0901, 0.10797, 0.10331, 0.07479, 0.09225, 0.08157],
        "source": (
            "DREES, La complémentaire santé, édition 2024, Fiche 15 « Le poids de la santé "
            "dans le revenu des ménages », Graphique 1 « Partage de la dépense de santé entre "
            "financeurs selon le niveau de vie du ménage, en 2019 », colonne AMO, modèle de "
            "microsimulation Ines-Omar 2019 (montant moyen de remboursement AMO par ménage et "
            "par décile : D1 4266€, D2 7331€, D3 5864€, D4 6896€, D5 4877€, D6 5844€, D7 5592€, "
            "D8 4048€, D9 4993€, D10 4415€ — part = montant du décile / somme des 10 déciles)."
        ),
        "note_rapprochement": (
            "Le levier `sante` (_apply_sante) agrège 3 réformes structurelles d'efficience "
            "(hôpital/ambulatoire/prévention-organisation, qui réduisent la dépense remboursée "
            "par l'AMO — périmètre couvert par cette clé) AVEC deux composantes de périmètre "
            "différent : la franchise/participation forfaitaire (reste à charge payé "
            "DIRECTEMENT par les patients, pas remboursé par l'AMO — incidence probablement "
            "plus concentrée sur les gros consommants de soins/personnes âgées que la moyenne "
            "AMO par décile) et le budget de prévention institutionnelle (dépense publique dont "
            "l'incidence par ménage n'est pas captée par un remboursement individualisé). "
            "DD135 (DREES, Les Dossiers de la DREES n°135, « Dérembourser des soins », février "
            "2026) a été vérifié pour une clé plus spécifique au déremboursement : il ne publie "
            "qu'une ventilation par QUINTILE (pas décile) du coût moyen par ménage de scénarios "
            "de déremboursement simulés, non convertible en 10 valeurs sans interpoler — moins "
            "précis que la table Fiche 15, donc non retenu. Cette clé AMO reste la meilleure "
            "approximation disponible pour l'ensemble du levier, à traiter comme un ordre de "
            "grandeur pour sa partie franchise/prévention."
        ),
    },
    "chomage_alloc": {
        "shares": [0.077905, 0.096144, 0.104482, 0.093017, 0.096404, 0.100313, 0.094841, 0.099531, 0.106566, 0.130797],
        "source": (
            "Insee Analyses n°88 (2023), « La redistribution élargie... », Tableau "
            "complémentaire 4 « Transferts moyens reçus en 2019 par les ménages, selon le "
            "niveau de vie » (même fichier donnees_ia88.xlsx que pour `education`), ligne "
            "« Chômage et revenus de remplacement », par vingtième (V1-V20) de niveau de "
            "vie, en euros par unité de consommation : V1 1260€, V2 1730€, V3 1810€, "
            "V4 1880€, V5 2090€, V6 1920€, V7 1940€, V8 1630€, V9 1860€, V10 1840€, "
            "V11 1870€, V12 1980€, V13 1880€, V14 1760€, V15 1910€, V16 1910€, V17 2000€, "
            "V18 2090€, V19 2340€, V20 2680€. Regroupement 2 par 2 en déciles (comme "
            "`education`), sans invention de pondération."
        ),
        "note_rapprochement": (
            "Cette source (comptes nationaux distribués Insee, 2019) est différente et plus "
            "englobante que la fiche « Redistribution monétaire » de l'Insee qui EXCLUT "
            "explicitement l'assurance chômage de son périmètre — recherche antérieure "
            "(round 5, chomage_alloc) l'avait donc jugée insuffisante. Le Tableau "
            "complémentaire 3 du même document n°88 précise explicitement : « Les pensions "
            "de retraite et les allocations chômage sont incluses dans la redistribution "
            "élargie ». Profil atypique à signaler : la part est CROISSANTE avec le niveau "
            "de vie (D10 à 13,1%, le plus haut), contre-intuitif pour une prestation sociale "
            "— cohérent cependant avec le fait que l'allocation chômage française est "
            "proportionnelle à l'ancien salaire (donc plus élevée en euros pour d'anciens "
            "hauts revenus), à la différence d'un minimum social forfaitaire comme le RSA. "
            "Données 2019, mêmes réserves de stabilité temporelle que pour `education`."
        ),
    },
    "education": {
        "shares": [0.155609, 0.12309, 0.107377, 0.101266, 0.096464, 0.090135, 0.085334, 0.08206, 0.077695, 0.08097],
        "source": (
            "Insee Analyses n°88 (2023), « La redistribution élargie... », Tableau "
            "complémentaire 4 « Transferts moyens reçus en 2019 par les ménages, selon le "
            "niveau de vie » (fichier donnees_ia88.xlsx, transmis par l'utilisateur le "
            "2026-10-02), ligne « Éducation », par vingtième (V1-V20) de niveau de vie, en "
            "euros par unité de consommation : V1 3700€, V2 3430€, V3 3090€, V4 2550€, "
            "V5 2580€, V6 2340€, V7 2450€, V8 2190€, V9 2210€, V10 2210€, V11 2150€, "
            "V12 1980€, V13 1990€, V14 1920€, V15 1850€, V16 1910€, V17 1790€, V18 1770€, "
            "V19 1760€, V20 1950€. Les vingtièmes étant de taille de population égale par "
            "construction (comme les déciles), on les regroupe directement 2 par 2 "
            "(D1=V1+V2, D2=V3+V4, ..., D10=V19+V20) pour obtenir un montant par décile, "
            "puis la part de chaque décile dans le total des 10 déciles — sans inventer de "
            "pondération, même principe que la clé `sante` (montant moyen déjà disponible "
            "sur une population complète et égale)."
        ),
        "note_rapprochement": (
            "Données 2019 (comptes nationaux distribués Insee), pas actualisées à l'année "
            "courante de simulation — utilisées comme la meilleure clé de répartition "
            "disponible (une part relative, pas un montant absolu), hypothèse implicite que "
            "la structure par décile de la dépense d'éducation est restée stable depuis "
            "2019. Le montant est \"par unité de consommation\" (UC, échelle d'équivalence "
            "Insee), pas par ménage brut — cohérent avec le concept de \"niveau de vie\" "
            "utilisé partout ailleurs dans ce module."
        ),
    },
    "abattement_retraites": {
        "shares": [0.0, 0.0, 0.0, 0.005464, 0.005464, 0.04918, 0.120219, 0.185792, 0.273224, 0.360657],
        "source": (
            "OFCE, export CSV du Graphique 1 (modèle de microsimulation Ines, Insee/Drees/"
            "Cnaf), transmis par l'utilisateur le 2026-10-02 — 10 déciles x 3 compositions "
            "(couples/seuls/autres), chaque cellule donnant le nombre de ménages (nb_men) et "
            "le montant Md€ agrégé de l'effet abattement (total_abat, en M€). Montant net "
            "ménages par décile (somme des 3 compositions) : D1 0, D2 0, D3 0, D4 -10M€, "
            "D5 -10M€, D6 -90M€, D7 -220M€, D8 -340M€, D9 -500M€, D10 -660M€ (total "
            "-1830M€) ; part = |montant du décile| / somme des valeurs absolues des 10 "
            "déciles. Vérification : somme des effectifs gagnants (g_abat) = 1 582 000 et "
            "perdants (p_abat) = 5 218 000, cohérent avec les \"1,5 million\"/\"5,2 millions\" "
            "cités dans l'article OFCE du 18 juillet 2025, confirmant qu'il s'agit bien des "
            "données sous-jacentes au même article."
        ),
        "note_rapprochement": (
            "Les montants sont en signe \"impact ménage\" (négatif = perte pour les ménages du "
            "décile, cohérent avec le signe \"recettes positif = gain budgétaire\" du moteur "
            "puisqu'une perte nette ménages correspond à un gain net pour l'État). D1 à D3 "
            "sont à 0% car le CSV source donne des montants nuls pour ces déciles (pas un "
            "artefact d'arrondi) — l'abattement ne touche quasiment pas les retraités des 30% "
            "les plus modestes."
        ),
    },
    "taxe_zucman": {
        "shares": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0],
        "estimation": True,
        "source": (
            "Périmètre légal (patrimoine net > 100 M€, ~1800 foyers) : très au-dessus du "
            "seuil d'entrée de D10 — même construction que `cdhr`/`taxe_holdings_patrimoniales`."
        ),
        "note_rapprochement": (
            "ESTIMATION, pas une clé aussi fiable que `cdhr` : la fraction de D10 réellement "
            "concernée est extrêmement étroite (~1800 foyers sur plusieurs millions dans D10), "
            "et le rendement lui-même varie d'un facteur 8 entre l'estimation du proposant et "
            "celle de la critique (cf. `handlers/nouvelles_taxes_2027.py`). 100% D10 reste "
            "néanmoins la seule affirmation vraie disponible (la mesure ne touche JAMAIS un "
            "foyer hors D10) — présentée comme une estimation par construction plutôt que "
            "comme une clé aussi précise que `cdhr`, pour ne pas suggérer que l'effet est "
            "réparti sur l'ensemble du décile."
        ),
    },
    "impot_revenu": {
        "shares": [0.05, 0.30, 0.40, 0.20, 0.05, 0.0, 0.0, 0.0, 0.0, 0.0],
        "estimation": True,
        "source": (
            "Pas de table RÉELLE de foyers bénéficiaires de la décote par décile (round 7, "
            "\"chercher jusqu'à trouver\" : IPP, AN/Sénat, DGFiP — rien trouvé). Clé "
            "structurelle construite à partir des seuils de décile de niveau de vie Insee "
            "(Insee Première n°2117, « Niveau de vie et pauvreté en 2024 ») : D1=13970€, "
            "D2=17700€, D3=20980€, D4=23880€/an/UC. La décote s'applique sur une fenêtre de "
            "revenu net imposable juste AU-DESSUS du seuil d'entrée dans l'impôt (~15900 à "
            "17440€ pour une personne seule en 2024/2025), zone qui se situe structurellement "
            "entre les seuils D1 et D2, débordant sur D3 pour les ménages plus grands (seuil "
            "par UC plus bas que le revenu individuel). D'où une concentration D2-D3, un "
            "palier D1 (beaucoup de foyers D1 ne sont de toute façon pas imposables, décote "
            "sans objet) et D4 (haut de la fenêtre), zéro au-delà."
        ),
        "note_rapprochement": (
            "DOUBLE LIMITE IMPORTANTE à signaler : (1) ceci est une zone de PLAUSIBILITÉ "
            "ancrée sur des seuils réels, PAS une distribution mesurée de bénéficiaires — "
            "aucune publication ne confirme les parts exactes (5/30/40/20/5) choisies ici, "
            "seule leur CONCENTRATION en D2-D4 repose sur un fait réel (position du seuil "
            "d'entrée dans l'impôt). (2) le handler `_apply_impot_revenu` combine dans UNE "
            "SEULE mesure deux mécanismes à l'incidence décile très différente : la décote "
            "(ci-dessus, classes moyennes basses) ET le taux de la tranche supérieure "
            "(`taux_superieur`, structurellement 100% D10, cf. seuil RFR > 160 950€, même "
            "logique que `cdhr`). Cette clé décile UNIQUE n'est donc fiable QUE lorsque "
            "`taux_superieur` reste proche de son défaut (45%) et que seule `decote` varie — "
            "si `taux_superieur` est aussi modifié, cette clé SOUS-ESTIME la part réelle de "
            "D10 (l'effet taux_superieur y est entièrement concentré mais n'est pas isolé "
            "ici). Correction propre : scinder `impot_revenu` en deux mesures distinctes dans "
            "le moteur (décote / taux supérieur), non fait à ce stade (changement "
            "d'architecture hors périmètre de cette tâche)."
        ),
    },
    "elargissement_ir": {
        "shares": [0.0, 0.0, 0.0, 0.50, 0.35, 0.15, 0.0, 0.0, 0.0, 0.0],
        "estimation": True,
        "source": (
            "Le handler `_apply_elargissement_ir` suppose lui-même (commentaire du code "
            "d'origine, non sourcé) que les nouveaux contribuables créés par l'abaissement du "
            "seuil d'entrée sont des « revenus D4-D6 (classes moyennes basses) », avec un "
            "revenu imposable moyen de 18 000€/an. Les seuils de décile Insee (Insee Première "
            "n°2117, 2024 : D2=17700€, D3=20980€, D4=23880€/UC/an) situent 18 000€ juste "
            "au-dessus du seuil D2, donc plutôt en bas de la bande D3/D4 une fois ajusté de "
            "l'individuel au niveau de vie par UC (le revenu individuel d'un célibataire se "
            "classe structurellement un peu plus bas une fois rapporté à un ménage). On reste "
            "dans la fourchette D4-D6 fixée par le handler d'origine (pour ne pas réviser une "
            "hypothèse de périmètre qui n'est pas de notre ressort), mais on pondère vers D4 "
            "plutôt qu'une répartition égale 1/3-1/3-1/3 : D4 50%, D5 35%, D6 15%."
        ),
        "note_rapprochement": (
            "ESTIMATION à deux niveaux : (1) le périmètre D4-D6 lui-même vient d'un "
            "commentaire NON SOURCÉ du code d'origine (repris tel quel, pas vérifié "
            "indépendamment) ; (2) la pondération 50/35/15 à l'intérieur de cette fourchette "
            "est une extrapolation de proximité de seuil, pas une distribution mesurée. "
            "Combinaison de deux approximations, à traiter comme une illustration qualitative "
            "(\"plutôt concentré en bas de la fourchette\") plutôt qu'un chiffre précis."
        ),
    },
    "fonction_publique": {
        "shares": [0.06, 0.08, 0.10, 0.12, 0.13, 0.13, 0.13, 0.11, 0.08, 0.06],
        "estimation": True,
        "source": (
            "Aucune table ne croise secteur employeur (public/privé) et décile de niveau de "
            "vie du ménage (round 6 et 7, recherche dédiée : DGAFP, Insee emploi, rien "
            "trouvé). Clé construite à partir d'un fait réel mais partiel : le rapport DGAFP "
            "« Rémunérations dans la fonction publique » (édition 2025) déclare explicitement "
            "« Jusqu'au septième décile de l'échelle salariale, les salaires dans le secteur "
            "privé sont inférieurs à ceux observés dans la fonction publique » et que les 6 "
            "premiers déciles de la fonction publique sont supérieurs de 6 à 12% à ceux du "
            "privé, l'écart s'inversant à partir de D9 (secteur privé +12% à D9, +26% au "
            "centile supérieur). Ceci documente une distribution SALARIALE compressée côté "
            "fonction publique, concentrée en milieu de distribution et sous-représentée en "
            "haut — traduit ici en une forme qualitative en cloche centrée D5-D7, décroissant "
            "vers D1 et D10."
        ),
        "note_rapprochement": (
            "ESTIMATION DE FORME, pas de valeurs mesurées : (1) la source DGAFP compare des "
            "déciles de SALAIRE individuel, pas des déciles de NIVEAU DE VIE du ménage (un "
            "fonctionnaire bien payé dans un ménage à un seul revenu peut se classer "
            "différemment en niveau de vie par UC) ; (2) les valeurs numériques exactes "
            "(6/8/10/12/13/13/13/11/8/6) sont une forme en cloche choisie pour traduire "
            "qualitativement \"concentré en milieu de distribution, sous-représenté en haut\", "
            "pas une distribution mesurée point par point. Appliquée telle quelle à "
            "`fonction_publique_reforme` (même population concernée, même limite)."
        ),
    },
    "fonction_publique_reforme": {
        "shares": [0.06, 0.08, 0.10, 0.12, 0.13, 0.13, 0.13, 0.11, 0.08, 0.06],
        "estimation": True,
        "source": "Identique à `fonction_publique` — même population d'agents publics concernée (fusion d'agences, digitalisation), voir cette entrée pour le détail de la source et des limites.",
        "note_rapprochement": "Voir `fonction_publique` ci-dessus pour le détail complet des limites de cette estimation de forme.",
    },
    "regimes_speciaux_retraite": {
        "shares": [0.03, 0.059, 0.07, 0.08, 0.089, 0.1, 0.112, 0.129, 0.162, 0.17],
        "estimation": True,
        "source": (
            "Réutilisation de la clé `retraites` (DREES, Les retraités et les retraites, éd. "
            "2025, part de la masse des pensions par décile) faute de publication qui ventile "
            "spécifiquement les pensions des régimes spéciaux par décile de niveau de vie."
        ),
        "note_rapprochement": (
            "ESTIMATION PAR PROXY, limite assumée : les régimes spéciaux (SNCF, RATP, "
            "industries électriques et gazières, etc.) ont une distribution de pensions qui "
            "peut différer de celle du régime général et des pensions \"en général\" — la "
            "Cour des comptes documente des pensions moyennes de certains régimes spéciaux "
            "(ex. SNCF) supérieures à la moyenne du régime général, ce qui pourrait biaiser "
            "cette clé vers le bas pour les déciles supérieurs (sous-estimation probable de "
            "D8-D10). Aucune publication dédiée n'existe pour corriger ce biais ; la clé "
            "`retraites` reste la moins mauvaise approximation disponible, pas une vraie "
            "source pour cette mesure précise."
        ),
    },
    "cdhr": {
        "shares": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0],
        "source": (
            "Périmètre légal de la CDHR (revenu fiscal de référence > 250k€ seul / 500k€ "
            "couple) : concerne exclusivement des foyers très au-dessus du seuil d'entrée "
            "du dernier décile (~4050€/mois, soit ~48,6k€/an, DECILE_SEUILS_EUR_MOIS)."
        ),
        "note_rapprochement": "Approximation : tous les foyers assujettis à la CDHR sont dans D10, mais tous les foyers de D10 n'y sont pas assujettis (la CDHR ne vise qu'une fraction de D10, ses hauts revenus).",
    },
    "taxe_holdings_patrimoniales": {
        "shares": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0],
        "source": (
            "Périmètre légal (holdings familiales détenant ≥5 M€ d'actifs financiers non "
            "professionnels) : concerne exclusivement des patrimoines très au-dessus du seuil "
            "d'entrée du dernier décile de niveau de vie."
        ),
        "note_rapprochement": "Même limite que cdhr ci-dessus : approximation par le haut, la mesure ne vise qu'une fraction très étroite de D10.",
    },
    # Ajoutée 2026-10 (handlers/fiscalite_menages.py::_apply_isf_climatique) : même principe
    # que cdhr/taxe_holdings_patrimoniales ci-dessus — 100% D10 non par hypothèse mais parce
    # que le périmètre du handler lui-même (seuil de patrimoine 0,8 à 2,0 M€ selon l'intensité,
    # 130k à 500k foyers concernés, soit le TOP 0,5% à 3% des patrimoines, IPP 2024) place la
    # population taxée entièrement au-dessus du seuil d'entrée de D10 (~48,6k€/an de niveau de
    # vie, DECILE_SEUILS_EUR_MOIS).
    "isf_climatique": {
        "shares": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0],
        "source": (
            "Périmètre du handler (seuil de patrimoine 0,8 à 2,0 M€, 130k à 500k foyers, soit "
            "le top 0,5% à 3% des patrimoines selon IPP 2024, cf. `_apply_isf_climatique`) : "
            "concerne exclusivement des foyers très au-dessus du seuil d'entrée du dernier "
            "décile de niveau de vie."
        ),
        "note_rapprochement": "Approximation par construction, comme cdhr/taxe_holdings_patrimoniales ci-dessus : tous les foyers assujettis sont dans D10, mais D10 est un décile de NIVEAU DE VIE (revenu), alors que l'assiette de cette mesure est un seuil de PATRIMOINE — même convention proxy revenu/patrimoine déjà acceptée pour `fiscalite_patrimoine`/`impot_societes` ci-dessus. Seule une fraction étroite de D10 (les plus hauts patrimoines) est réellement concernée.",
    },
}

# Champ(s) du dict d'impacts par mesure à sommer pour obtenir le delta Md€
# NET à ventiler (convention du moteur : positif = coût pour les finances
# publiques évité/gagné ; voir docstrings des handlers concernés).
_IMPACT_FIELDS = ("recettes", "depenses")


def _net_impact_md_eur(mesure_impacts: dict) -> float:
    """Delta Md€ net d'une mesure pour une année donnée, tel qu'exposé par
    ``report['measure_impacts_by_year']`` du moteur original. Convention du
    moteur : `recettes` positif = gain budgétaire, `depenses` négatif = la
    mesure fait ÉCONOMISER (donc `-depenses` est aussi un gain) — voir
    ``orchestrator.py`` / handlers individuels pour le détail par mesure."""
    total = 0.0
    for field in _IMPACT_FIELDS:
        val = mesure_impacts.get(field)
        if isinstance(val, (int, float)):
            total += val
    return total


def decile_breakdown(measure_impacts_by_year: list[dict]) -> dict:
    """Construit la ventilation par décile pour toutes les mesures
    reconnues (présentes dans DECILE_SHARES) à partir du champ
    ``measure_impacts`` déjà renvoyé par POST /simulate.

    Retourne un dict :
    {
      "par_mesure": {mesure: {"total_md_eur": float, "par_decile": {D1: .., ...},
                                "source": str, "note_rapprochement": str|None}},
      "total_par_decile": {D1: .., ..., D10: ..},
      "total_md_eur_ventile": float,
      "mesures_non_ventilees": [mesure, ...],
    }
    """
    # On prend la DERNIÈRE année disponible où chaque mesure apparaît (measure_impacts_by_year
    # est une liste par année ; l'impact d'une mesure y est présent à partir de son année
    # d'entrée en vigueur). On agrège le delta de la mesure sur la dernière année vue,
    # cohérent avec la convention "impact plein régime" déjà utilisée dans notre classeur Excel.
    latest_by_mesure: dict[str, dict] = {}
    for year_entry in measure_impacts_by_year or []:
        for key, val in year_entry.items():
            if key == "Année" or not isinstance(val, dict):
                continue
            latest_by_mesure[key] = val  # écrasé à chaque année -> reste la dernière rencontrée

    par_mesure = {}
    total_par_decile = {d: 0.0 for d in DECILES}
    total_md_eur_ventile = 0.0
    mesures_non_ventilees = []

    for mesure, impacts in latest_by_mesure.items():
        net_md_eur = _net_impact_md_eur(impacts)
        if mesure not in DECILE_SHARES:
            if abs(net_md_eur) > 1e-9:
                mesures_non_ventilees.append(mesure)
            continue
        cfg = DECILE_SHARES[mesure]
        shares = cfg["shares"]
        par_decile = {d: round(net_md_eur * s, 4) for d, s in zip(DECILES, shares)}
        par_mesure[mesure] = {
            "total_md_eur": round(net_md_eur, 4),
            "par_decile": par_decile,
            "source": cfg["source"],
            "note_rapprochement": cfg["note_rapprochement"],
            "estimation": cfg.get("estimation", False),
        }
        for d in DECILES:
            total_par_decile[d] += par_decile[d]
        total_md_eur_ventile += net_md_eur

    total_par_decile = {d: round(v, 4) for d, v in total_par_decile.items()}
    return {
        "par_mesure": par_mesure,
        "total_par_decile": total_par_decile,
        "total_md_eur_ventile": round(total_md_eur_ventile, 4),
        "mesures_non_ventilees": mesures_non_ventilees,
    }
