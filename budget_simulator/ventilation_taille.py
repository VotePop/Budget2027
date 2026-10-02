"""Module ventilation par taille d'entreprise — répartition, par catégorie
(microentreprises/TPE, PME, ETI, grandes entreprises), des impacts Md€ calculés
par le moteur macro-budgétaire (handlers ``competitivite.py`` notamment).

CONTEXTE : comme ``decile.py`` pour les ménages, ce module N'EST PAS dans le
dépôt original cturkieh/france-budget-simulateur (AGPL-3.0). Il comble un angle
absent du moteur (un seul indice « Compétitivité » macro, sans détail) : quelle
catégorie d'entreprise supporte ou bénéficie réellement de chaque mesure.

MÉTHODE : identique à ``decile.py`` — on reprend tel quel le delta Md€ NET
(recettes - dépenses) déjà calculé par les handlers pour chaque mesure, sans
rien recalculer, et on le ventile par catégorie de deux façons possibles :

1. Clé de répartition SOURCÉE (ex. ``impot_societes`` : répartition réelle de
   l'IS brut par catégorie d'entreprise, DGFiP/INSEE).
2. Ventilation à 100% sur une seule catégorie quand la mesure ELLE-MÊME est
   définie, par construction, comme ne concernant que cette catégorie — c'est
   le cas des 4 mesures « TGE » (très grandes entreprises) de ce moteur
   (``niches_fiscales_tge``, ``niches_sociales_tge``, ``subventions_tge``,
   ``is_exceptionnel_tge``), dont le docstring et la logique du handler
   d'origine (``budget_simulator/handlers/competitivite.py``) précisent déjà
   qu'elles ciblent exclusivement les grandes entreprises (« TGE » = 15k
   entreprises pour les niches fiscales, etc.). Ce n'est pas une hypothèse que
   nous ajoutons : c'est la définition même de la mesure dans le moteur.

CONVENTION "ESTIMATION" (2026-10-02) : certaines entrées ci-dessous portent un
champ ``"estimation": True``. Cela signifie que la clé n'est pas intégralement
sourcée pour les 4 catégories — une partie (généralement le solde ETI/GE à
l'intérieur d'un segment "500 salariés et plus" que les sources françaises ne
subdivisent pas) est complétée par une EXTRAPOLATION documentée, construite à
partir d'une source réelle mais appliquée hors de son périmètre exact (ex. le
ratio national ETI/GE en effectifs, appliqué à une sous-population dont on ne
sait pas si elle suit exactement ce même ratio). Ce n'est PAS un chiffre
inventé sans ancrage : c'est la moins mauvaise approximation disponible,
documentée comme telle (méthode + limites explicites dans `note_rapprochement`)
plutôt que de laisser la mesure "non ventilée". Directive utilisateur du
2026-10-02 : toute mesure concernée par une ventilation taille/décile doit en
avoir une, quitte à documenter une estimation imparfaite, plutôt que de rester
vide indéfiniment une fois la recherche de source complète épuisée.

LIMITES ASSUMÉES (à afficher côté client) :
- Seules les mesures listées dans TAILLE_SHARES sont ventilables.
- ``impots_production`` (réexaminée 2026-10, round 4 "chercher jusqu'à
  trouver") : RÉSOLUE en combinant DEUX sources officielles distinctes, sans
  inventer de pondération. (1) DGFiP Statistiques n°35 (2025), "Les impôts de
  production en 2023", Tableau 4 "Moyenne et dispersion du poids des impôts
  de production d'origine fiscale en 2023" (p.4) : poids moyen en % de la
  valeur ajoutée par catégorie — GE 3,4%, ETI 2,9%, PME 1,9% (microentreprises
  exclues du tableau, taux qualifié d'explicitement "négligeable" par la
  DGFiP). (2) Insee Focus n°372 (décembre 2025), "Le tissu productif français
  par catégorie d'entreprises en 2023" : valeur ajoutée par catégorie —
  microentreprises 219,2 Md€ (16,3%), PME hors micro 312,2 Md€ (23,2%), ETI
  354,7 Md€ (26,4%), GE 459,1 Md€ (34,1%), total 1 345,2 Md€. En multipliant
  le taux (1) par la valeur ajoutée (2) pour chaque catégorie, on obtient un
  montant réel d'impôts de production par catégorie (GE 15,61 Md€, ETI 10,29
  Md€, PME 5,93 Md€, MIC ≈ 0), dont on tire une part du total — ni le taux ni
  le poids économique ne sont inventés, seule leur multiplication est une
  opération arithmétique directe (même principe déjà accepté pour
  ``cotisations_patronales`` : une clé de masse salariale réutilisée telle
  quelle, pas une extrapolation vers une sous-catégorie non couverte par la
  source).
- ``cotisations_patronales`` (réexaminée 2026-10) : RÉSOLUE avec
  ``"estimation": True``. Base sourcée à 100% : PLFSS 2026, Annexe 4,
  Tableau 5 "Masse salariale (secteur privé) et exonérations par taille
  d'entreprise en 2024" (URSSAF Caisse Nationale — DSN 2024), colonne
  "Structure des exonérations générales (%)" par tranche d'effectifs :
  0 à 9 = 25,2% (MIC) ; 10-19/20-49/50-99/100-249 sommées = 47,3% (PME) ;
  250 à 499 = 6,1% (ETI pure) ; 500 et plus = 21,4% (mélange ETI 500-4999 et
  GE 5000+, la table URSSAF ne va pas plus loin). Pour ne pas laisser ce
  solde non ventilé, on le répartit au prorata du ratio national ETI/GE en
  EFFECTIFS SALARIÉS (Insee Focus n°372, 2023, « Le tissu productif français
  par catégorie d'entreprises » : ETI 3 826,0 milliers d'ETP / GE 4 167,9
  milliers d'ETP, soit 47,86% / 52,14% du total ETI+GE) — cf.
  `note_rapprochement` pour les limites de cette extrapolation.
- ``quotient_familial``, ``quotient_conjugal``, ``pfu_bareme``,
  ``coupe_prestations`` (nouvelles mesures, lot 2026-10 "grille de tri 12
  pistes") : hors périmètre de ce module par construction — ce sont des
  mesures qui s'appliquent à des FOYERS/MÉNAGES (barème IR, prestations
  sociales), pas à des entreprises ; comportement normal, pas une lacune
  (même constat déjà fait pour les mesures ménages existantes, cf.
  CHANGES.md entrée maquette "Économie").
- ``taxe_zucman`` (nouvelle mesure, lot 2026-10) : bien que l'assiette
  (patrimoine détenu via des holdings familiales) ait une dimension
  entreprise, comme `taxe_holdings_patrimoniales` ci-dessus, la mesure cible
  en droit le PATRIMOINE NET DU FOYER (personne physique), pas le résultat
  ou le chiffre d'affaires d'une catégorie d'entreprise au sens INSEE
  (MIC/PME/ETI/GE) — aucune source ne permet de ventiler ce patrimoine par
  taille d'entreprise détenue (holdings patrimoniales privées, non cotées,
  hors du périmètre statistique DGFiP/INSEE par taille). Reste "non
  ventilée" dans ce module, par choix de prudence assumé (même esprit que
  son absence de ventilation décile, cf. `decile.py`).
- ``regimes_speciaux_retraite`` (nouvelle mesure, lot 2026-10 "audit
  comparatif") : hors périmètre de ce module par construction — c'est une
  subvention budgétaire de l'État à des caisses de retraite (ménages
  pensionnés), pas une mesure touchant des entreprises classées par taille ;
  comportement normal, pas une lacune (même constat que pour les mesures
  ménages de la liste ci-dessus). Voir `decile.py` pour son statut "non
  ventilée" côté décile.
- ``smic`` (réexaminée 2026-10) : RÉSOLUE avec ``"estimation": True``, DEUX
  approximations empilées. (1) Assemblée nationale, rapport commission des
  affaires sociales n° l16b0489, tableau "Salariés bénéficiant de la
  revalorisation du Smic au 1ᵉʳ janvier 2021, par taille d'entreprise" (Dares,
  enquêtes Acemo) : effectifs par tranche — 1-9 24,1%, 10-19 10,9%, 20-49
  13,0%, 50-99 14,3%, 100-249 9,6%, 250-499 8,7%, 500+ 5,6% — CES 7 PARTS NE
  SOMMENT QU'À 86,2% (catégorie(s) manquante(s) ou non publiée(s) dans la
  table source) : on les RENORMALISE pour qu'elles somment à 100%, en
  supposant que la part manquante se répartit dans les mêmes proportions
  relatives entre tranches (hypothèse technique de normalisation, pas un
  chiffre inventé, mais à signaler). (2) le même ratio national ETI/GE en
  effectifs (47,86%/52,14%, Insee Focus n°372) que pour `cotisations_patronales`
  répartit ensuite le solde "500 et plus" renormalisé. Par ailleurs cette
  donnée est un comptage de SALARIÉS bénéficiaires (clé de population),
  utilisée comme proxy du coût Md€ en supposant un coût par salarié à peu
  près uniforme entre tranches — voir `note_rapprochement` pour le détail
  des 3 approximations cumulées.
- ``exonerations_salaires`` (réexaminée 2026-10) : RÉSOLUE avec
  ``"estimation": True`` — et correction de périmètre importante : le round 4
  avait cherché une donnée sur les allègements généraux bas salaires
  (open.urssaf.fr, bloqué), en confondant le nom de la mesure avec le
  dispositif "réduction générale" URSSAF. En réalité, le handler
  `_apply_exonerations_salaires` (handlers/additionnels.py) modélise une
  mesure différente et plus large du programme NFP 2027 : une exonération de
  cotisations sur TOUTE hausse de salaire au-dessus d'un seuil, appliquée à
  l'ENSEMBLE de la masse salariale privée (800 Md€), pas aux seuls bas
  salaires. La clé appropriée n'est donc pas une table d'exonérations ciblées
  mais la structure de la MASSE SALARIALE PRIVÉE elle-même par taille
  d'entreprise — qu'on a déjà, PLFSS 2026 Annexe 4 Tableau 5, colonne "Masse
  salariale (secteur privé, %)" : 0-9 12,0% (MIC), 10-19/20-49/50-99/100-249
  sommées 34,8% (PME), 250-499 7,8% (ETI pure), 500+ 45,3% (mélange ETI/GE,
  reparti comme ci-dessus via le ratio national 47,86%/52,14%). C'est une
  réutilisation DIRECTE et appropriée de la table (le périmètre de la mesure
  EST la masse salariale totale, pas une hypothèse de rapprochement), seul le
  solde ETI/GE reste une estimation au même titre que pour les deux mesures
  ci-dessus.
- ``transition_ecologique`` (réexaminée 2026-10) : RÉSOLUE avec
  ``"estimation": True`` — piste précédemment ÉCARTÉE (round 4), reprise
  après la directive utilisateur du 2026-10-02 ("extrapoler plutôt que
  laisser vide, mais le documenter"). Source : CSIA (Comité de surveillance
  des investissements d'avenir), « Première évaluation in itinere France
  2030 » (juin 2023), Tableau 3 p.42-43, engagements par type de
  bénéficiaire au 30 avril 2023 (13,8 Md€ engagés) : PME 22,1%, ETI 5,3%,
  GE 13,2%, organismes de recherche 34,6%, abondements fonds 18,4%, autres
  6,4%. Limites IMPORTANTES, non résolues par cette extrapolation : (1) ces
  parts couvrent TOUS les axes France 2030 (pas seulement la transition
  écologique) ; (2) photo partielle à une date (30/04/2023), pas un flux
  annuel stabilisé ; (3) aucune catégorie MIC distincte. Pour obtenir une clé
  à 4 catégories MIC/PME/ETI/GE malgré ces limites, on EXCLUT les catégories
  non assimilables à une taille d'entreprise (organismes de recherche,
  abondements de fonds, autres = 59,4% du total engagé) et on renormalise les
  3 catégories entreprise restantes (PME 22,1 + ETI 5,3 + GE 13,2 = 40,6) à
  100% : PME 54,43%, ETI 13,05%, GE 32,51%, MIC 0% (aucune donnée MIC
  disponible dans cette source). Ceci revient à supposer que le ratio
  PME/ETI/GE observé sur l'ENSEMBLE de France 2030 (tous axes) s'applique
  aussi à son volet transition écologique spécifiquement — hypothèse NON
  vérifiée par la source, la plus importante limite de cette estimation.
- Le delta ventilé est celui du PREMIER TOUR (recettes - dépenses), sans
  boucler sur les effets démographiques/croissance du moteur macro — même
  convention que ``decile.py``.
"""
from __future__ import annotations

from typing import Any

CATEGORIES = ["MIC", "PME", "ETI", "GE"]

# Chaque entrée : mesure du moteur -> (shares par catégorie (somme = 1.0), source,
# note de méthode si utile).
TAILLE_SHARES: dict[str, dict[str, Any]] = {
    "impot_societes": {
        "shares": {"MIC": 0.174, "PME": 0.261, "ETI": 0.235, "GE": 0.330},
        "source": (
            "INSEE Références, « Les entreprises en France », édition décembre 2023 "
            "(données DGFiP, IS brut par catégorie d'entreprise, 2021) : "
            "microentreprises 12,4 Md€ (17,4%), PME hors micro 18,6 Md€ (26,1%), "
            "ETI 16,7 Md€ (23,5%), grandes entreprises 23,5 Md€ (33,0%), total 71,2 Md€."
        ),
        "note_rapprochement": None,
    },
    "niches_fiscales_tge": {
        "shares": {"MIC": 0.0, "PME": 0.0, "ETI": 0.0, "GE": 1.0},
        "source": (
            "Mesure définie par construction dans le moteur (handlers/competitivite.py) "
            "comme ciblant exclusivement les très grandes entreprises (~15 000 "
            "entreprises) — 100% GE n'est pas une hypothèse ajoutée ici, c'est le "
            "périmètre même de la mesure d'origine."
        ),
        "note_rapprochement": None,
    },
    "niches_sociales_tge": {
        "shares": {"MIC": 0.0, "PME": 0.0, "ETI": 0.0, "GE": 1.0},
        "source": "Idem niches_fiscales_tge — mesure définie « TGE » par construction dans le moteur.",
        "note_rapprochement": None,
    },
    "subventions_tge": {
        "shares": {"MIC": 0.0, "PME": 0.0, "ETI": 0.0, "GE": 1.0},
        "source": "Idem niches_fiscales_tge — mesure définie « TGE » par construction dans le moteur.",
        "note_rapprochement": None,
    },
    "is_exceptionnel_tge": {
        "shares": {"MIC": 0.0, "PME": 0.0, "ETI": 0.0, "GE": 1.0},
        "source": "Idem niches_fiscales_tge — mesure définie « TGE » par construction dans le moteur.",
        "note_rapprochement": None,
    },
    # Ajoutées 2026-10 (budget_simulator/handlers/nouvelles_taxes_2027.py) : ``ttf`` et
    # ``taxe_gafa`` sont ventilées 100% GE non par hypothèse mais parce que leur PÉRIMÈTRE
    # LÉGAL LUI-MÊME exclut les MIC/PME/ETI (seuil de capitalisation boursière pour la TTF,
    # seuil de chiffre d'affaires mondial 750 M€ pour la taxe GAFA) — même principe que les
    # mesures « TGE » ci-dessus.
    "ttf": {
        "shares": {"MIC": 0.0, "PME": 0.0, "ETI": 0.0, "GE": 1.0},
        "source": (
            "Périmètre légal de la taxe (sociétés françaises cotées, seuil de "
            "capitalisation boursière ~1 Md€) : par construction, seules les grandes "
            "entreprises sont assujetties."
        ),
        "note_rapprochement": None,
    },
    "taxe_gafa": {
        "shares": {"MIC": 0.0, "PME": 0.0, "ETI": 0.0, "GE": 1.0},
        "source": (
            "Périmètre légal de la taxe (seuil de chiffre d'affaires numérique mondial "
            "750 M€) : par construction, seules les grandes entreprises sont assujetties."
        ),
        "note_rapprochement": None,
    },
    # Ajoutée 2026-10 (handlers/additionnels.py::_apply_taxe_superprofits) : même principe
    # que ttf/taxe_gafa ci-dessus — 100% GE non par hypothèse mais parce que le périmètre
    # même de la mesure (secteurs énergie/banques/luxe/tech concernés, seuil de chiffre
    # d'affaires 1 à 1,5 Md€, ~400 entreprises) correspond à la catégorie "grande entreprise"
    # au sens de la taxonomie INSEE par taille (CA très au-dessus des seuils MIC/PME/ETI).
    "taxe_superprofits": {
        "shares": {"MIC": 0.0, "PME": 0.0, "ETI": 0.0, "GE": 1.0},
        "source": (
            "Périmètre de la mesure (seuil de chiffre d'affaires 1 à 1,5 Md€, ~400 "
            "entreprises concernées, secteurs énergie/banques/luxe/tech, cf. "
            "`_apply_taxe_superprofits`) : par construction, seules les grandes entreprises "
            "au sens de la taxonomie INSEE par taille sont assujetties."
        ),
        "note_rapprochement": None,
    },
    # Ajoutée 2026-10 (lot "PLFSS 2026 Annexe 4", budget_simulator/handlers/
    # nouveaux_leviers_sociaux_2026.py::_apply_exoneration_heures_sup) : clé RÉELLE de
    # répartition de la déduction forfaitaire PATRONALE sur les heures supplémentaires,
    # PLFSS 2026, Annexe 4, Tableau 13 (p.45-46) et Tableau 22 (p.53), ligne "Déductions
    # sur les heures supplémentaires (entreprises de moins 250 salariés)", colonne 2026 (P)
    # — source Commission des comptes de la Sécurité sociale (CCSS) d'octobre 2025 : total
    # 872 M€, dont entreprises de moins de 20 salariés 504 M€ (57,8%) et dont entreprises
    # d'au moins 20 et de moins de 250 salariés 368 M€ (42,2%). ETI et GE sont à 0% NON par
    # hypothèse mais parce que le périmètre LÉGAL de ce dispositif est strictement plafonné
    # à moins de 250 salariés : la 2e LFR 2012 (article 3) a restreint la déduction
    # forfaitaire patronale TEPA aux entreprises de moins de 20 salariés, puis l'article 2
    # de la loi n° 2022-1158 du 16 août 2022 a créé, à compter du 1er octobre 2022, un
    # second dispositif de déduction forfaitaire (0,50 €/heure) pour les entreprises d'au
    # moins 20 et de moins de 250 salariés — les deux dispositifs coexistent et couvrent
    # ensemble tout le "moins de 250 salariés", sans aucune composante ETI/GE.
    "exoneration_heures_sup": {
        "shares": {"MIC": 0.57798, "PME": 0.42202, "ETI": 0.0, "GE": 0.0},
        "source": (
            "PLFSS 2026, Annexe 4, Tableau 13 (p.45-46) / Tableau 22 (p.53), ligne "
            "\"Déductions sur les heures supplémentaires (entreprises de moins 250 "
            "salariés)\", colonne 2026 (P), source Commission des comptes de la Sécurité "
            "sociale (CCSS) d'octobre 2025 : total 872 M€, dont entreprises de moins de 20 "
            "salariés 504 M€ (57,8%), dont entreprises d'au moins 20 et de moins de 250 "
            "salariés 368 M€ (42,2%). ETI=0%/GE=0% par construction : périmètre légal "
            "plafonné à moins de 250 salariés (2e LFR 2012 art. 3, complétée par l'article "
            "2 de la loi n° 2022-1158 du 16 août 2022 qui a étendu la déduction forfaitaire "
            "patronale, jusque-là réservée aux moins de 20 salariés, aux entreprises d'au "
            "moins 20 et de moins de 250 salariés à compter du 1er octobre 2022)."
        ),
        "note_rapprochement": (
            "Approximation de nomenclature assumée : la source utilise un seuil légal de "
            "20 salariés (\"moins de 20\"), pas le seuil INSEE de la catégorie MIC (0-9 "
            "salariés). La tranche \"10 à 19 salariés\", qui relève de la catégorie PME au "
            "sens INSEE, est donc incluse ici dans la part MIC (57,8%) plutôt que dans la "
            "part PME —léger sur-comptage de MIC et sous-comptage de PME par rapport à une "
            "ventilation strictement conforme à la taxonomie INSEE 0-9/10-249, faute d'une "
            "source qui isole le seuil 0-9 pour ce dispositif précis."
        ),
    },
    # Ajoutée 2026-10 (lot audit comparatif, budget_simulator/handlers/investissements.py::
    # _apply_credit_impot_recherche) : clé RÉELLE de répartition de la créance de CIR par
    # catégorie d'entreprise (MESR-DGRI, données 2023, relayées par financeinnovation.fr,
    # "Le crédit impôt recherche (CIR) en 2023") : PME 31%, ETI 28%, grandes entreprises 41%
    # de la créance CIR-recherche — ces 3 parts somment à 100%.
    "credit_impot_recherche": {
        "shares": {"MIC": 0.0, "PME": 0.31, "ETI": 0.28, "GE": 0.41},
        "source": (
            "MESR-DGRI, données 2023 (relayées par financeinnovation.fr, \"Le crédit "
            "impôt recherche (CIR) en 2023\") : PME 31% de la créance (81% des "
            "déclarants), ETI 28% (15% des déclarants), grandes entreprises 41% (3,5% "
            "des déclarants)."
        ),
        "note_rapprochement": (
            "La catégorie \"microentreprises\" n'est PAS isolée dans cette statistique "
            "officielle : le seuil \"PME\" utilisé est le seuil communautaire "
            "(<250 salariés, <=50 M€ de CA), qui englobe les microentreprises. MIC est "
            "donc conventionnellement mis à 0 et sa part réelle (non nulle mais non "
            "chiffrée séparément par la source) reste incluse dans PME — à traiter comme "
            "un sous-compte de PME, pas comme une absence réelle de bénéficiaires MIC."
        ),
    },
    # Ajoutée 2026-10 (round 4 "chercher jusqu'à trouver") : clé obtenue en combinant deux
    # sources officielles indépendantes — DGFiP Statistiques n°35 (2025), "Les impôts de
    # production en 2023", Tableau 4 (poids moyen en % de la VA par catégorie : GE 3,4%,
    # ETI 2,9%, PME 1,9%, micro exclue/"négligeable") et Insee Focus n°372 (déc. 2025), "Le
    # tissu productif français par catégorie d'entreprises en 2023" (VA par catégorie : MIC
    # 219,2 Md€, PME 312,2 Md€, ETI 354,7 Md€, GE 459,1 Md€). Montant = taux x VA par
    # catégorie (GE 15,61 Md€, ETI 10,29 Md€, PME 5,93 Md€, MIC ≈ 0), total 31,83 Md€, d'où
    # les parts ci-dessous.
    "impots_production": {
        "shares": {"MIC": 0.0, "PME": 0.1863, "ETI": 0.3233, "GE": 0.4904},
        "source": (
            "DGFiP Statistiques n°35 (2025), \"Les impôts de production en 2023\", Tableau 4 "
            "(poids moyen en % de la valeur ajoutée : GE 3,4%, ETI 2,9%, PME 1,9%) x Insee "
            "Focus n°372 (déc. 2025), \"Le tissu productif français par catégorie "
            "d'entreprises en 2023\" (valeur ajoutée 2023 : MIC 219,2 Md€, PME 312,2 Md€, "
            "ETI 354,7 Md€, GE 459,1 Md€) = montant d'impôts de production par catégorie "
            "(GE 15,61 Md€, ETI 10,29 Md€, PME 5,93 Md€, MIC négligeable), d'où les parts du "
            "total (31,83 Md€)."
        ),
        "note_rapprochement": (
            "Deux approximations assumées : (1) le taux DGFiP est une MOYENNE des taux "
            "individuels d'entreprises par catégorie, pas un ratio agrégat (total impôts / "
            "total VA de la catégorie) — les deux peuvent légèrement différer si la "
            "distribution des taux est asymétrique au sein d'une catégorie ; (2) les "
            "microentreprises sont mises à 0% faute de taux publié : la DGFiP les qualifie "
            "explicitement de \"négligeables\", mais leur part réelle n'est probablement pas "
            "strictement nulle."
        ),
    },
    # Ajoutée 2026-10 (round "extrapoler plutôt que laisser vide", directive utilisateur) :
    # base sourcée (PLFSS 2026 Annexe 4 Tableau 5, structure des exonérations générales) +
    # solde ETI/GE estimé via le ratio national ETI/GE en effectifs (Insee Focus n°372,
    # 3826,0/(3826,0+4167,9)=47,86% ETI, 52,14% GE) appliqué aux 27,5% restants
    # (6,1% ETI pure + 21,4% "500 et plus" mélangé).
    "cotisations_patronales": {
        "shares": {"MIC": 0.252, "PME": 0.473, "ETI": 0.16342, "GE": 0.11158},
        "estimation": True,
        "source": (
            "PLFSS 2026, Annexe 4, Tableau 5 \"Masse salariale (secteur privé) et "
            "exonérations par taille d'entreprise en 2024\" (URSSAF DSN 2024), structure "
            "des exonérations générales : MIC (0-9) 25,2%, PME (10-249, sommée) 47,3%, "
            "ETI pure (250-499) 6,1%, solde \"500 et plus\" 21,4% (mélange ETI 500-4999 et "
            "GE 5000+, non subdivisé par la source). Le solde est réparti au prorata du "
            "ratio national ETI/GE en effectifs salariés ETP (Insee Focus n°372, 2023 : "
            "ETI 3826,0 milliers / GE 4167,9 milliers, soit 47,86%/52,14% du total ETI+GE)."
        ),
        "note_rapprochement": (
            "ESTIMATION PAR EXTRAPOLATION pour la part ETI/GE uniquement (MIC et PME sont "
            "100% sourcés). Le ratio national ETI/GE en effectifs (toutes entreprises, tous "
            "secteurs) est appliqué à une sous-population précise (entreprises de 500+ "
            "salariés ayant des exonérations générales de cotisations) dont rien ne garantit "
            "qu'elle suit exactement ce même ratio national — par exemple si les grandes "
            "entreprises (GE) ont une masse salariale moyenne par salarié plus élevée que les "
            "ETI, leurs exonérations générales (dégressives avec le salaire) pourraient être "
            "proportionnellement plus faibles que leur seul poids en effectifs. Meilleure "
            "approximation disponible en l'absence d'une source qui subdivise directement le "
            "segment \"500 et plus\"."
        ),
    },
    # Ajoutée 2026-10 : même méthode que cotisations_patronales, appliquée à la table Dares
    # (effectifs bénéficiaires de la revalorisation du Smic par taille), avec une
    # renormalisation supplémentaire car les 7 tranches sources ne sommaient qu'à 86,2%.
    "smic": {
        "shares": {"MIC": 0.27958, "PME": 0.55452, "ETI": 0.13202, "GE": 0.03387},
        "estimation": True,
        "source": (
            "Assemblée nationale, rapport commission des affaires sociales n° l16b0489, "
            "tableau \"Salariés bénéficiant de la revalorisation du Smic au 1er janvier "
            "2021, par taille d'entreprise\" (Dares, enquêtes Acemo) : effectifs par tranche "
            "— 1-9 24,1%, 10-19 10,9%, 20-49 13,0%, 50-99 14,3%, 100-249 9,6%, 250-499 8,7%, "
            "500+ 5,6% (somme brute 86,2%, renormalisée à 100%). Solde \"500 et plus\" "
            "reparti ETI/GE via le même ratio national 47,86%/52,14% (Insee Focus n°372)."
        ),
        "note_rapprochement": (
            "TROIS approximations cumulées, la plus estimée de ce module : (1) la table "
            "source ne somme qu'à 86,2% (catégorie non publiée ou effectifs hors périmètre) "
            "— renormalisée en supposant une répartition proportionnelle de l'écart entre "
            "toutes les tranches ; (2) le comptage est un nombre de SALARIÉS bénéficiaires "
            "(clé de population), utilisé comme proxy du coût Md€ en supposant un coût par "
            "salarié à peu près uniforme entre tailles d'entreprise — non vérifié par la "
            "source ; (3) le solde ETI/GE du \"500 et plus\" est extrapolé via le ratio "
            "national (même limite que `cotisations_patronales`). Données de 2021 (dernière "
            "édition trouvée de cette table), pas actualisées."
        ),
    },
    # Ajoutée 2026-10 : réutilisation DIRECTE de la table masse salariale PLFSS Annexe 4
    # Tableau 5 (le périmètre de la mesure EST la masse salariale totale), solde ETI/GE
    # estimé comme pour les deux mesures ci-dessus.
    "exonerations_salaires": {
        "shares": {"MIC": 0.12, "PME": 0.348, "ETI": 0.29481, "GE": 0.23719},
        "estimation": True,
        "source": (
            "PLFSS 2026, Annexe 4, Tableau 5, colonne \"Masse salariale (secteur privé, %)\" "
            "par tranche d'effectifs : 0-9 12,0% (MIC), 10-19/20-49/50-99/100-249 sommées "
            "34,8% (PME), 250-499 7,8% (ETI pure), 500+ 45,3% (mélange ETI/GE, reparti via "
            "le ratio national ETI/GE en effectifs 47,86%/52,14%, Insee Focus n°372). "
            "Réutilisation directe : le handler `_apply_exonerations_salaires` applique un "
            "taux d'exonération uniforme à l'ensemble de la masse salariale privée (800 "
            "Md€), donc la structure de la masse salariale par taille EST la bonne clé de "
            "répartition, pas une approximation de périmètre."
        ),
        "note_rapprochement": (
            "Seul le solde ETI/GE (45,3% du total) est une estimation (même méthode et même "
            "limite que `cotisations_patronales` : le ratio national en effectifs est "
            "appliqué à une sous-population sans garantie qu'elle le suive exactement). MIC, "
            "PME et ETI pure (54,8% du total) sont directement tirés de la table sourcée."
        ),
    },
    # Ajoutée 2026-10 (reprise après directive utilisateur, round précédemment écarté) : CSIA,
    # France 2030, parts PME/ETI/GE renormalisées après exclusion des catégories non-entreprise.
    "transition_ecologique": {
        "shares": {"MIC": 0.0, "PME": 0.54433, "ETI": 0.13054, "GE": 0.32512},
        "estimation": True,
        "source": (
            "CSIA (Comité de surveillance des investissements d'avenir), « Première "
            "évaluation in itinere France 2030 » (juin 2023), Tableau 3 p.42-43, "
            "engagements par type de bénéficiaire au 30/04/2023 (13,8 Md€) : PME 22,1%, "
            "ETI 5,3%, GE 13,2%, organismes de recherche 34,6%, abondements fonds 18,4%, "
            "autres 6,4%. Les catégories non assimilables à une taille d'entreprise "
            "(organismes de recherche, fonds, autres = 59,4%) sont exclues, et les 3 "
            "catégories entreprise restantes renormalisées à 100% (22,1+5,3+13,2=40,6 -> "
            "PME 54,43%, ETI 13,05%, GE 32,51%)."
        ),
        "note_rapprochement": (
            "ESTIMATION avec limites importantes et non résolues : ces parts couvrent TOUS "
            "les axes de France 2030 (numérique, santé, énergie, etc.), pas seulement son "
            "volet transition écologique spécifiquement — on suppose que la répartition "
            "PME/ETI/GE est similaire sur ce sous-périmètre, hypothèse non vérifiée. Photo "
            "partielle à une date (30/04/2023), pas un flux annuel stabilisé. Aucune donnée "
            "MIC dans la source (mis à 0%, une sous-estimation probable pour ce type "
            "d'investissement surtout orienté grands projets)."
        ),
    },
}

_IMPACT_FIELDS = ("recettes", "depenses")


def _net_impact_md_eur(mesure_impacts: dict) -> float:
    """Delta Md€ net d'une mesure pour une année donnée — même convention que
    ``decile._net_impact_md_eur`` : `recettes` positif = gain budgétaire (donc
    coût net pour les entreprises concernées), `-depenses` est aussi un gain
    budgétaire."""
    total = 0.0
    for field in _IMPACT_FIELDS:
        val = mesure_impacts.get(field)
        if isinstance(val, (int, float)):
            total += val
    return total


def ventilation_taille(measure_impacts_by_year: list[dict]) -> dict:
    """Construit la ventilation par taille d'entreprise pour toutes les mesures
    reconnues (présentes dans TAILLE_SHARES) à partir du champ ``measure_impacts``
    déjà renvoyé par POST /simulate_decile (même structure que ``decile.decile_breakdown``).

    Retourne :
    {
      "par_mesure": {mesure: {"total_md_eur": float, "par_categorie": {MIC:.., ...},
                                "source": str, "note_rapprochement": str|None}},
      "total_par_categorie": {MIC:.., PME:.., ETI:.., GE:..},
      "total_md_eur_ventile": float,
      "mesures_non_ventilees": [mesure, ...],
    }
    """
    latest_by_mesure: dict[str, dict] = {}
    for year_entry in measure_impacts_by_year or []:
        for key, val in year_entry.items():
            if key == "Année" or not isinstance(val, dict):
                continue
            latest_by_mesure[key] = val

    par_mesure = {}
    total_par_categorie = {c: 0.0 for c in CATEGORIES}
    total_md_eur_ventile = 0.0
    mesures_non_ventilees = []

    for mesure, impacts in latest_by_mesure.items():
        net_md_eur = _net_impact_md_eur(impacts)
        if mesure not in TAILLE_SHARES:
            if abs(net_md_eur) > 1e-9:
                mesures_non_ventilees.append(mesure)
            continue
        cfg = TAILLE_SHARES[mesure]
        shares = cfg["shares"]
        par_categorie = {c: round(net_md_eur * shares.get(c, 0.0), 4) for c in CATEGORIES}
        par_mesure[mesure] = {
            "total_md_eur": round(net_md_eur, 4),
            "par_categorie": par_categorie,
            "source": cfg["source"],
            "note_rapprochement": cfg["note_rapprochement"],
            "estimation": cfg.get("estimation", False),
        }
        for c in CATEGORIES:
            total_par_categorie[c] += par_categorie[c]
        total_md_eur_ventile += net_md_eur

    total_par_categorie = {c: round(v, 4) for c, v in total_par_categorie.items()}
    return {
        "par_mesure": par_mesure,
        "total_par_categorie": total_par_categorie,
        "total_md_eur_ventile": round(total_md_eur_ventile, 4),
        "mesures_non_ventilees": mesures_non_ventilees,
    }
