"""Section 4 — Pression fiscale ménages.

Mesures couvertes (8 handlers) :
- ``tva_rate`` : taux de TVA général (base 20 %). Élasticité conso, effet Laffer
  au-delà de 22 %. Effets gini/PA/compétitivité one-time. Depuis 2026-09, porte
  aussi les 3 autres taux officiels (intermédiaire 10 %, réduit 5,5 %,
  particulier 2,1 %) — canal recettes LINÉAIRE uniquement (rendement/point DG
  Trésor Trésor-Éco n°371), pas de canal gini/PA/compétitivité propre à ces 3.
- ``tva_energie`` : taux de TVA énergie (gaz + électricité, base 20 %). Slider
  unique vers 5,5 % (NFP/RN). Phasing 1 an, effets NIVEAU one-time.
- ``impot_revenu`` : barème IR — taux 5e tranche + décote. Assiette MARGINALE
  (au-dessus de 160 950 €), effet Laffer via ETI tranche supérieure.
- ``csg`` : taux global CSG (base 9,7 %) + option progressivité par décile
  (neutre recettes, forte réduction Gini). Recettes RÉCURRENTES, PA/Gini one-time.
- ``cotisations_salariales`` : baisse en points (0-5), -6 Md€/pt. PA/Gini one-time.
- ``elargissement_ir`` : % de foyers imposables cible (0,45 → 0,70). Recettes
  classes moyennes D4-D6.
- ``fiscalite_patrimoine`` : IFI + succession + foncière regroupés, slider
  intensité ±0,3. Effet redistributif fort.
- ``isf_climatique`` : ISF avec bonus actifs verts, slider intensité 0-100 %,
  remplace l'IFI (croissance +2 %/an). Phasing 2 ans (cadastre), plafond 18 Md€.
- ``quotient_familial`` (ajouté 2026-10, lot "grille de tri 12 pistes") :
  abaissement du plafond de l'avantage du quotient familial (plafond actuel
  1791€/demi-part). Modèle linéaire calé sur le seul point de calibration
  réel disponible : la baisse PLF 2014 (2000€->1500€ = +1,03 Md€).
- ``quotient_conjugal`` (ajouté 2026-10) : individualisation de l'IR des
  couples mariés/pacsés (fin de l'imposition commune), slider intensité
  0-100 % interpolant vers le scénario "individualisation complète avec
  option" de l'Insee (+7,2 Md€). Mesure STRUCTURELLE distincte du quotient
  familial (mécanisme différent : parts du couple vs parts des enfants),
  sourcée séparément (Insee Analyses n°53 décompose le coût total 29,7 Md€
  en 10,8 Md€ conjugal / 19,0 Md€ familial).
- ``pfu_bareme`` (ajouté 2026-10) : retour au barème progressif de l'IR pour
  les revenus du capital, à la place du prélèvement forfaitaire unique (PFU,
  30 %). Slider intensité 0-100 %, calé sur le coût permanent du PFU estimé
  par le comité d'évaluation France Stratégie (1,4-1,7 Md€/an), net d'un
  facteur comportemental (rebond de distribution de dividendes observé par
  l'IPP lors du passage au PFU, supposé symétrique en cas de retour arrière).
- ``accises`` (ajouté 2026-10, demande utilisateur "accise ok" suite à
  comparaison avec le projet tiers github.com/Vadech/moi-president) : levier
  sur le NIVEAU GLOBAL des droits d'accise indirects — TICPE (carburants) +
  droits de consommation sur le tabac + droits sur les alcools —, distinct de
  ``tva_rate``/``tva_energie`` (TVA ad valorem) : ce sont des droits
  SPÉCIFIQUES (montant fixe par unité physique, pas un taux proportionnel).
  Slider ``variation_pct`` (variation relative appliquée aux 3 composantes
  simultanément). Assiette 49,0 Md€/an (TICPE 30,5 + tabac 13,95 +
  alcool 4,565, sources Trésor/Sénat n°638/DGDDI, cf. constants.py), élasticité
  -0,4 reprise PAR ANALOGIE du tabac (Sénat n°638) faute d'élasticité dédiée
  publiée pour les 3 composantes combinées. Gini/PA calibrés PAR ANALOGIE sur
  une vraie étude de régressivité décile trouvée pour ces 3 taxes précisément
  (Insee ES413, Ruiz & Trannoy 2008) mais non convertible en clé de décile
  faute de revenu moyen par décile publié dans la même étude — ``accises``
  reste "non ventilée" dans ``decile.py`` (cf. docstring de ce module).

Convention d'application :
- Effets ``gini`` / ``pouvoir_achat`` / ``competitivite`` en mode NIVEAU
  one-time, gated selon DEUX idiomes distincts coexistant dans le monolithe :
  - ``self._is_first_year_change(<measure>, params)`` : tva_rate,
    impot_revenu, elargissement_ir, fiscalite_patrimoine, cotisations_salariales.
  - ``years_elapsed == 0`` : tva_energie, isf_climatique, et csg (pour ses
    effets PA/Gini).
  Cas mixte : ``csg`` combine les deux — PA/Gini gated ``years_elapsed == 0``
  MAIS son sous-effet ``competitivite`` (mode progressif) gated
  ``self._is_first_year_change('csg_competitivite', ...)``. Cette nuance
  sémantique est PRÉSERVÉE telle quelle depuis le monolithe — toute
  unification éventuelle = chantier dédié avec double validation adverse
  + golden master audité (pas une simple refactor cosmétique).
- Effet ``recettes`` : RÉCURRENT (proportionnel au taux) pour csg/tva ;
  one-shot delta pour les barèmes.
- Voir docs/METHODOLOGIE.md § "Effets NIVEAU vs FLUX" pour le contrat de gating.

Sources principales :
- OFCE 2024 (TVA et inégalités, CSG régressive), INSEE 2018 (hausse TVA),
  CAE 2022/2024 (répercussion prix, attractivité).
- DG Trésor, Trésor-Éco n°371 (09/2025) : rendement net par point pour les 3
  taux de TVA autres que le taux normal (intermédiaire/réduit/particulier).
- DGFiP POTE 2024, DG Trésor 2018, IPP TAXIPP 2024 (barème IR, Laffer).
- DREES 2024, OFCE 2023 (progressivité CSG, modèle Allemagne).
- URSSAF 2024, DARES (cotisations salariales).
- EU Tax Observatory 2024, Gabriel Zucman, IPP 2025 (ISF climatique).

Couplages avec ``BudgetSimulatorV45`` (instance hôte du mixin) :
- Lit ``self.debug_logs`` et la méthode ``self._is_first_year_change`` (base
  class, simulator.py).
- N'écrit aucun attribut d'instance.
"""
from typing import TYPE_CHECKING, Dict, Tuple

from ..constants import (
    ACCISES_BASE_TOTAL_MD_EUR, ACCISES_ELASTICITE_PRIX, ACCISES_GINI_FACTEUR,
    ACCISES_PART_REVENU_MOYENNE, ETI_TRANCHE_SUPERIEURE, POLICY_START_YEAR,
    PFU_BAREME_FACTEUR_COMPORTEMENTAL, PFU_BAREME_RENDEMENT_BRUT_MD,
    QUOTIENT_CONJUGAL_RENDEMENT_INDIVIDUALISATION_MD,
    QUOTIENT_FAMILIAL_PLAFOND_REF_EUR, QUOTIENT_FAMILIAL_RENDEMENT_PAR_EURO_MD,
)
from .._logging import _log_debug
from ._phasing import _one_time_level, _year_phasing
from ._types import ImpactsDict


# Idiome mixin-self typing : NE PAS factoriser dans _types.py (casse la
# liaison self mypy + risque MRO). Réplication volontaire 7×. Cf Lot D.
if TYPE_CHECKING:
    from ._types import _SimulatorState

    _MixinBase = _SimulatorState
else:
    _MixinBase = object


class FiscaliteMenagesMixin(_MixinBase):
    """Handlers Section 4 — Pression fiscale ménages."""

    def _apply_tva_rate(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        rate = params.get('taux', 0.20)
        consumption_base = 0.53 * gdp
        base_elasticity = -0.2 if rate > 0.20 else -0.1
        if unemployment > 0.10:
            base_elasticity *= 1.2
        adjusted_base = consumption_base * (1 + base_elasticity * (rate - 0.20))
        delta_revenue = (rate - 0.20) * adjusted_base * 0.9
        if rate > 0.22:
            # BUG corrigé 2026-10 (fork VotePop) : ce facteur d'amortissement comportemental
            # n'était borné nulle part. Il était sans risque tant que le curseur restait dans
            # la plage d'origine du moteur (15-25%), mais une fois la plage élargie (demande
            # explicite d'aller au-delà de 25%, voir CHANGES.md), le facteur devenait NUL vers
            # 37% de taux puis NÉGATIF au-delà (ex. -8,7 à 50%) — ce qui inversait le signe de
            # `delta_revenue` : le moteur affichait alors qu'une TVA à 50% rapportait MOINS que la
            # TVA actuelle à 20%, et par ricochet (signe inversé côté ménages dans le mockup) que
            # les ménages "gagnaient de l'argent" en augmentant la TVA — économiquement absurde,
            # confirmé et reproduit lors d'un test utilisateur. Plancher à 0 : au-delà du point où
            # l'effet comportemental (élasticité-prix, ETI) compenserait entièrement l'effet
            # mécanique, le modèle affiche une saturation (recette additionnelle nulle) plutôt
            # qu'une réversion de signe — pas une nouvelle hypothèse, un garde-fou sur une
            # extrapolation qui n'était valide que sur un intervalle étroit à l'origine.
            damping = 1 - 0.2 * (rate - 0.22) / 0.03
            delta_revenue *= max(0.0, damping)

        # === RECETTES — 3 AUTRES TAUX DE TVA (2026-09) ===
        # Ajout (2026-09) : jusqu'ici seul le taux normal était pilotable. Le canal
        # recettes des 3 autres taux officiels (intermédiaire 10 %, réduit 5,5 %,
        # particulier 2,1 %) est modélisé ICI en LINÉAIRE — pas de courbe d'élasticité
        # propre à chaque taux (contrairement au taux normal ci-dessus), faute de
        # source distincte par taux pour un effet comportemental. Rendement net par
        # point directement repris de l'étude officielle (pas une assiette dérivée
        # par nous) : DG Trésor, Trésor-Éco n°371 (09/2025), "Analyse de la
        # composition des recettes de TVA", tableau 1 — rendement NET par point de
        # TVA en 2025 (net = brut corrigé de la TVA payée par les administrations
        # publiques elles-mêmes, à partir du compte 2022 Insee semi-définitif) :
        #   taux normal (20 %) : 7,5 Md€/point (brut 8,9) — NON repris ici, cf. plus haut
        #   taux intermédiaire (10 %) : 1,6 Md€/point (brut 1,9)
        #   taux réduit (5,5 %)       : 2,0 Md€/point (brut 2,4)
        #   taux particulier (2,1 %)  : 0,4 Md€/point (brut 0,4)
        # Limite assumée : les canaux gini/pouvoir_achat/compétitivité ci-dessous
        # restent calculés uniquement sur le taux normal — aucune source distincte
        # par taux pour ces canaux n'a été trouvée, donc aucun chiffre n'est inventé
        # pour les 3 nouveaux paramètres sur ces canaux.
        RENDEMENT_NET_TVA_INTERMEDIAIRE_PAR_POINT_MD_EUR = 1.6
        RENDEMENT_NET_TVA_REDUIT_PAR_POINT_MD_EUR = 2.0
        RENDEMENT_NET_TVA_PARTICULIER_PAR_POINT_MD_EUR = 0.4
        taux_intermediaire = params.get('taux_intermediaire', 0.10)
        taux_reduit = params.get('taux_reduit', 0.055)
        taux_particulier = params.get('taux_particulier', 0.021)
        delta_revenue += (taux_intermediaire - 0.10) / 0.01 * RENDEMENT_NET_TVA_INTERMEDIAIRE_PAR_POINT_MD_EUR
        delta_revenue += (taux_reduit - 0.055) / 0.01 * RENDEMENT_NET_TVA_REDUIT_PAR_POINT_MD_EUR
        delta_revenue += (taux_particulier - 0.021) / 0.01 * RENDEMENT_NET_TVA_PARTICULIER_PAR_POINT_MD_EUR

        # === IMPACTS MACROÉCONOMIQUES ===
        # Gini : Impact ONE-TIME (changement structure fiscale)
        if self._is_first_year_change('tva_rate', {'rate': rate}):
            # Gini : TVA = impôt RÉGRESSIF (touche + les pauvres)
            # Règle : TVA 20%→22% = +0.005 Gini (OFCE 2024)
            gini = 0.005 * (rate - 0.20) / 0.02
        else:
            gini = 0.0

        # Pouvoir d'achat : Impact ONE-TIME de NIVEAU (changement structure fiscale).
        # Règle : TVA +1pt = -0.002 PA agrégé (INSEE 2018 "Hausse TVA et inégalités" :
        # +3pt TVA = -0.6% niveau de vie corrigé sur 3 ans → -0.2%/pt).
        # NIVEAU et non flux annuel : la consommation s'ajuste UNE FOIS au nouveau prix relatif.
        if self._is_first_year_change('tva_rate_pa', {'rate': rate}):
            pouvoir_achat = -0.002 * (rate - 0.20) / 0.01
        else:
            pouvoir_achat = 0.0

        # Compétitivité : Impact ONE-TIME (changement structure fiscale)
        # Règle : TVA +2% = -0.0005 compétitivité (CAE 2022, répercussion prix)
        if self._is_first_year_change('tva_rate_competitivite', {'rate': rate}):
            competitivite = -0.0005 * (rate - 0.20) / 0.02  # ONE-TIME changement taux
        else:
            competitivite = 0.0  # Niveau conservé dans indice

        _log_debug(self.debug_logs, f"Mesure tva_rate: Δdép=0.0 Md€, Δrec={delta_revenue:.1f} Md€")
        impacts = {
            'recettes': delta_revenue,
            'gini': gini,
            'pouvoir_achat': pouvoir_achat,
            'competitivite': competitivite
        }
        return 0, delta_revenue, impacts

    def _apply_tva_energie(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """TVA énergie (actuel 20%). NFP/RN: 5.5% → -17 Md€ recettes, +1.5% PA. Conso 120 Md€/an. Effets NIVEAU one-time.
        Sources: NFP 2027, OFCE 2024. Voir METHODOLOGIE.md § Mesures Presidentielles 2027."""
        # ===== PARAMÈTRES - TAUX UNIQUE GAZ + ÉLECTRICITÉ =====
        # Slider unique : 20% (status quo) → 5.5% (NFP/RN)
        taux_energie = params.get('taux', 0.20)  # 0.055 à 0.20 (défaut 20%)
        taux_elec = taux_energie
        taux_gaz = taux_energie

        # Année de référence
        years_elapsed = year - POLICY_START_YEAR

        # ===== PHASING 1 AN (mesure législative rapide) =====
        phasing = _year_phasing(years_elapsed, (1.0,))  # effet immédiat dès l'entrée en vigueur

        # ===== CONSOMMATION ÉNERGIE =====
        # Base 2024 : électricité 60 Md€, gaz 60 Md€
        conso_electricite = 60.0  # Md€
        conso_gaz = 60.0  # Md€

        # ===== RECETTES TVA ACTUELLES (20%) =====
        recettes_actuelles_elec = conso_electricite * 0.20
        recettes_actuelles_gaz = conso_gaz * 0.20
        recettes_actuelles_total = recettes_actuelles_elec + recettes_actuelles_gaz  # 24 Md€

        # ===== RECETTES TVA NOUVELLES =====
        recettes_nouvelles_elec = conso_electricite * taux_elec
        recettes_nouvelles_gaz = conso_gaz * taux_gaz
        recettes_nouvelles_total = recettes_nouvelles_elec + recettes_nouvelles_gaz

        # ===== DELTA RECETTES =====
        delta_revenue = (recettes_nouvelles_total - recettes_actuelles_total) * phasing

        # ===== IMPACTS MACROÉCONOMIQUES =====
        # Pouvoir achat : énergie = 10% budget ménages
        # Baisse TVA 20% → 5.5% = -14.5 points → +14.5% baisse prix TTC → +1.45% PA
        # IMPORTANT : Effet NIVEAU (one-time), pas FLUX (recurring)
        # → Impact PA appliqué UNIQUEMENT l'année de mise en œuvre (years_elapsed == 0)
        # CONVENTION : delta_tva = TAUX_NOUVEAU - TAUX_ANCIEN (cohérent avec TVA générale)
        # Ex slider 5.5% : taux_energie=0.055 → delta_tva_moyen = (0.055-0.20) = -0.145
        # Impact PA = -(-0.145) × 0.10 = +0.0145 (+1.45% PA) ✅
        delta_tva_moyen = ((taux_elec + taux_gaz) / 2) - 0.20
        part_energie_budget = 0.10  # Énergie = 10% budget ménages (INSEE 2024)

        # Impact PA = one-time boost l'année de mise en œuvre seulement
        # (années suivantes : niveau déjà atteint, pas d'impact additionnel)
        impact_pa = _one_time_level(years_elapsed, -delta_tva_moyen * part_energie_budget * phasing)

        # Gini : léger effet positif (ménages modestes dépensent + en % pour énergie)
        # Baisse TVA énergie réduit inégalités (énergie = 15% budget classes populaires vs 7% classes aisées)
        # Impact appliqué UNE FOIS (changement structure prix relatifs)
        impact_gini = _one_time_level(years_elapsed, delta_tva_moyen * 0.05 * phasing)

        # Compétitivité : neutre (entreprises ont déjà TVA déductible)
        impact_competitivite = 0.0

        impacts = {
            'recettes': delta_revenue,
            'gini': impact_gini,
            'pouvoir_achat': impact_pa,
            'competitivite': impact_competitivite
        }

        _log_debug(self.debug_logs,
            f"Y{year}: TVA énergie - Élec {taux_elec*100:.1f}%, Gaz {taux_gaz*100:.1f}%, "
            f"Recettes {delta_revenue:+.1f} Md€, PA {impact_pa:+.2%}"
        )

        return 0, delta_revenue, impacts

    def _apply_impot_revenu(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        taux_sup = params.get('taux_superieur', 0.45)
        decote = params.get('decote', 1.0)

        # Bareme IR — assiette MARGINALE uniquement (fix bug ×3.6 surestimation).
        # Le delta de taux de la 5e tranche ne s'applique qu'a la fraction du revenu
        # AU-DESSUS du seuil 160 950 EUR (PLF 2025), pas a tout le revenu (220k EUR).
        # Sources : DGFiP POTE 2024, DG Tresor 2018, IPP TAXIPP 2024.
        foyers_riches = 400_000           # Foyers RNI > 160 950 EUR (DGFiP 2024)
        revenu_moyen_tranche = 220_000    # Revenu moyen foyer 5e tranche
        seuil_tranche_sup = 160_950       # Seuil 5e tranche, bareme PLF 2025
        assiette_marginale = revenu_moyen_tranche - seuil_tranche_sup  # ~59 050 EUR

        # Effet mecanique (avant comportement)
        delta_taux_brut = (taux_sup - 0.45) * foyers_riches * assiette_marginale / 1e9

        # Effet Laffer / elasticite revenu imposable (Saez-Diamond 2011, ETI=0.25 sur tranche sup).
        # Taux marginal effectif total = IR + CSG (9.7%) + CEHR (4% en moyenne sur tranche sup).
        # Calibrage 45→55% : 1.95 Md€ post-Laffer (vs DG Tresor 2018 fourchette 1-3 Md€).
        taux_marginal_total_avant = 0.45 + 0.097 + 0.04
        taux_marginal_total_apres = taux_sup + 0.097 + 0.04
        if taux_marginal_total_avant < 1.0 and taux_sup > 0.45:
            delta_net_of_tax = (
                (1 - taux_marginal_total_apres) - (1 - taux_marginal_total_avant)
            ) / (1 - taux_marginal_total_avant)
            facteur_comportemental = max(0.5, 1 + ETI_TRANCHE_SUPERIEURE * delta_net_of_tax)
        else:
            facteur_comportemental = 1.0

        delta_taux = delta_taux_brut * facteur_comportemental
        delta_decote = (1.0 - decote) * 7.5
        delta_revenue = delta_taux + delta_decote

        # === IMPACTS MACROÉCONOMIQUES ===
        # Gini : Impact ONE-TIME (changement barème fiscal)
        if self._is_first_year_change('impot_revenu', {'taux_sup': taux_sup, 'decote': decote}):
            # IR = impôt PROGRESSIF (redistribution forte)
            # Règle : Taux sup 45%→50% = -0.008 Gini (OFCE 2023)
            gini = -0.008 * (taux_sup - 0.45) / 0.05
            # Décote : Baisse décote = hausse impôt classes moyennes = +Gini
            gini += 0.003 * (1.0 - decote)
        else:
            gini = 0.0

        # Pouvoir d'achat : Impact ONE-TIME de NIVEAU (changement barème fiscal).
        # Règle : Hausse taux sup = -0.001 PA (concentré hauts revenus). Décote touche classes moyennes.
        # Le barème modifie le revenu disponible UNE FOIS, pas chaque année (TAXIPP/IPP convention).
        params_ir_pa = {'taux_sup': taux_sup, 'decote': decote}
        if self._is_first_year_change('impot_revenu_pa', params_ir_pa):
            pouvoir_achat = -0.001 * (taux_sup - 0.45) / 0.05
            pouvoir_achat += -0.002 * (1.0 - decote)
        else:
            pouvoir_achat = 0.0

        # Compétitivité : Impact ONE-TIME (changement structure fiscale)
        # Règle : Taux sup 45%→50% = -0.0002 (CAE 2024, attractivité hauts revenus/expatriation)
        params_ir_comp = {'taux_sup': taux_sup, 'decote': decote}
        if self._is_first_year_change('impot_revenu_competitivite', params_ir_comp):
            competitivite = -0.0002 * (taux_sup - 0.45) / 0.05  # ONE-TIME changement taux
        else:
            competitivite = 0.0  # Niveau conservé dans indice

        impacts = {
            'recettes': delta_revenue,
            'gini': gini,
            'pouvoir_achat': pouvoir_achat,
            'competitivite': competitivite
        }
        return 0, delta_revenue, impacts

    def _apply_csg(self, measure: Dict, params: Dict, year: int,
                   gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """
        CSG avec 2 paramètres indépendants:
        - taux (0.08-0.12): Taux global CSG, défaut 0.097
        - progressive (0/1): Activation progressivité par décile

        Mode flat (progressive=0): Tous paient le même taux
        Mode progressif (progressive=1): Taux par décile, neutre recettes
          D1-D3 (30%): taux - 3.7 pts
          D4-D6 (30%): taux - 1.2 pts
          D7-D8 (20%): taux + 0.8 pts
          D9 (10%): taux + 2.8 pts
          D10 (10%): taux + 6.3 pts

        Sources: DREES 2024, OFCE 2023 progressivité CSG, Modèle Allemagne
        """
        taux_global = params.get('taux', 0.097)
        progressive = params.get('progressive', 0)  # 0 ou 1

        CSG_BASE = 0.097  # Taux CSG réel actuel 9.7%
        CSG_RECETTES_BASE = 140.0  # Md€ (DREES 2024)

        # Année de référence pour phasing (impacts one-time)
        years_elapsed = year - POLICY_START_YEAR

        # ===== EFFET 1 : VARIATION TAUX GLOBAL =====
        delta_taux_global = taux_global - CSG_BASE

        # Impact recettes (proportionnel, RÉCURRENT chaque année)
        delta_recettes = CSG_RECETTES_BASE * (delta_taux_global / CSG_BASE)

        # Impact PA et Gini : ONE-TIME (changement de niveau, pas flux annuel)
        # Justification économique : Un changement de taux CSG modifie le niveau
        # du revenu disponible UNE SEULE FOIS (effet de niveau), comme TVA/IR ;
        # années suivantes : niveau déjà atteint, plus d'impact marginal.
        # Impact PA global (inverse, tous déciles touchés également) :
        #   -1 pt CSG = -1% PA (OFCE 2024).
        # Impact Gini du taux : LÉGÈREMENT RÉGRESSIF — CSG touche pensions (taux
        #   remplacement faible) et patrimoine. Règle : CSG +1 pt = +0.002 Gini
        #   (OFCE 2024 "CSG légèrement régressive"). CSG 9.7 % (défaut 2025) →
        #   delta=0 → impact=0 (status quo) ; CSG 10.5 % → delta=+0.8 pt →
        #   impact=+0.0016 Gini.
        impact_pa_taux = _one_time_level(years_elapsed, -0.01 * (delta_taux_global / 0.01))
        impact_gini_taux = _one_time_level(years_elapsed, 0.002 * (delta_taux_global / 0.01))

        # ===== EFFET 2 : PROGRESSIVITÉ (si activée) =====
        impact_pa_progressif = 0.0
        impact_gini_progressif = 0.0
        impact_emploi_progressif = 0.0
        impact_competitivite = 0.0

        if progressive == 1:
            # Recettes : NEUTRE (ajustement automatique des taux par décile)
            # Pas de delta_recettes additionnel

            # IMPACTS ONE-TIME : appliqués uniquement l'année 0 (changement de
            # niveau) ; années suivantes : maintien du niveau (pas de cumul).
            # PA : effet différentiel net POSITIF (+0.4 %) — déciles bas (forte
            #   propension conso) gagnent plus que hauts perdent.
            # Gini : FORTE réduction inégalités (OFCE 2023, modèle Allemagne).
            # Emploi : via boost consommation (multiplicateur 0.6) — +0.73 %
            #   conso → +0.44 % PIB → -0.15 % chômage (Okun -0.35).
            impact_pa_progressif = _one_time_level(years_elapsed, +0.004)
            impact_gini_progressif = _one_time_level(years_elapsed, -0.015)
            impact_emploi_progressif = _one_time_level(years_elapsed, -0.0015)

            # Compétitivité : Impact ONE-TIME (changement structure fiscale)
            # Signal taux marginal D10 → attractivité fiscale
            params_csg_comp = {'progressive': progressive, 'taux': taux_global}
            if self._is_first_year_change('csg_competitivite', params_csg_comp):
                impact_competitivite = -0.003  # ONE-TIME année activation
            else:
                impact_competitivite = 0.0  # Années suivantes (niveau conservé dans indice)
        # progressive != 1 : impact_competitivite reste à 0.0 (init ci-dessus)

        # ===== IMPACTS TOTAUX =====
        impacts = {
            'recettes': delta_recettes,
            'pouvoir_achat': impact_pa_taux + impact_pa_progressif,
            'gini': impact_gini_taux + impact_gini_progressif,
            'chomage': impact_emploi_progressif,
            'competitivite': impact_competitivite
        }

        # Logs détaillés
        if progressive == 1:
            taux_d1_d3 = taux_global - 0.037
            taux_d10 = taux_global + 0.063
            _log_debug(self.debug_logs,
                       f"Y{year}: CSG {taux_global*100:.1f}% progressive - "
                       f"D1-D3:{taux_d1_d3*100:.1f}%, D10:{taux_d10*100:.1f}%, "
                       f"Recettes {delta_recettes:+.1f}Md€, PA {impacts['pouvoir_achat']*100:+.2f}%, "
                       f"Gini {impact_gini_progressif:.3f}")
        else:
            _log_debug(self.debug_logs,
                       f"Y{year}: CSG {taux_global*100:.1f}% flat - "
                       f"Recettes {delta_recettes:+.1f}Md€, PA {impacts['pouvoir_achat']*100:+.2f}%")

        return 0, delta_recettes, impacts

    def _apply_cotisations_salariales(self, measure: Dict, params: Dict, year: int,
                                      gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """
        Baisse cotisations salariales (22% actuellement)

        Paramètre:
        - baisse_points (-3 à 5): points de cotisations, positif = baisse, négatif = hausse

        Impact: -1 point = +0.5% pouvoir d'achat, coût 6 Md€ (linéaire, donc symétrique pour
        une hausse : +1 point = -0.5% pouvoir d'achat, +6 Md€ recettes)
        Sources: URSSAF 2024, DARES pouvoir d'achat, OFCE multiplicateurs

        AJOUT 2026-10 (fork VotePop) : borne basse étendue de 0 à -3 pour permettre une HAUSSE
        des cotisations salariales (le moteur original ne permettait que la baisse) — demande
        explicite ("on ne peut pas monter du coup ?"). Toutes les formules ci-dessous étaient
        déjà linéaires en `baisse_points`, donc s'étendent correctement par symétrie à une
        valeur négative ; aucune nouvelle élasticité inventée.
        """
        baisse_points = params.get('baisse_points', 0.0)  # -3.0 à 5.0
        baisse_points = max(-3, min(5, baisse_points))  # Clamp -3..5

        if baisse_points == 0:
            return 0.0, 0.0, {}

        # ===== COÛT BUDGÉTAIRE =====
        # -1 point cotisations = -6 Md€ recettes sociales
        COUT_PAR_POINT = 6.0  # Md€
        delta_revenue = -baisse_points * COUT_PAR_POINT

        # ===== IMPACTS MACROÉCONOMIQUES =====
        impacts = {
            'recettes': delta_revenue,
        }

        # ONE-TIME gate: PA et Gini ne s'appliquent que la première année de changement
        is_first_year = self._is_first_year_change('cotisations_salariales', {'baisse_points': baisse_points})

        # Pouvoir d'achat: +0.5% par point (OFCE 2024) — ONE-TIME
        # Baisse cotis → salaire net augmente → PA augmente
        if is_first_year:
            impacts['pouvoir_achat'] = 0.005 * baisse_points
        else:
            impacts['pouvoir_achat'] = 0.0

        # Gini: Impact ONE-TIME (première année changement seulement)
        if is_first_year:
            # Gini: INÉGALITAIRE (bénéfice absolu croît avec revenu)
            # Baisse cotis = MOINS de redistribution sociale → Gini AUGMENTE
            # Mécanisme : -1 pt cotis → -6 Md€ sécu → moins de transferts progressifs
            # Source: OFCE 2023 - Baisse uniforme 3 pts = +0.008 Gini
            # Donc: -1 pt cotis = +0.0027 Gini (hausse inégalités)
            # ATTENTION AU SIGNE : baisse_points POSITIF → Gini AUGMENTE (+)
            impacts['gini'] = 0.0027 * baisse_points
        else:
            # Années suivantes : impact déjà intégré
            impacts['gini'] = 0.0

        # Compétitivité: Neutre (ne change pas coût travail pour entreprises)
        impacts['competitivite'] = 0.0

        # Emploi: Légèrement positif via consommation
        # +0.5% PA → +0.3% conso → +0.05% emploi (multiplier 0.6)
        impacts['chomage'] = -0.0005 * baisse_points

        _log_debug(self.debug_logs,
                   f"Y{year}: Cotisations salariales -{baisse_points:.1f} pts - "
                   f"Taux effectif {22-baisse_points:.1f}%, coût {delta_revenue:.1f}Md€, "
                   f"PA +{impacts['pouvoir_achat']*100:.2f}%")

        return 0, delta_revenue, impacts

    def _apply_elargissement_ir(self, measure: Dict, params: Dict, year: int,
                                gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """
        Élargissement base IR (45% → 70% contribuables)

        Paramètres:
        - taux_contribuables_cible (0.20-1.00): % foyers imposables cible

        Implique plusieurs leviers techniques (baisse seuil entrée, gel barème,
        réduction abattements, plafonnement QF, restriction niches fiscales...)

        Sources: DGFiP 2024 (19M/41M foyers imposés = 45%), France Stratégie, OFCE

        AJOUT 2026-10 (fork VotePop) : bornes étendues de [0.45, 0.70] à [0.20, 1.00] — demande
        explicite ("pourquoi ne pas permettre de descendre ou de monter plus haut ?"). La formule
        `nouveaux_contrib = FOYERS_TOTAL * (taux_cible - TAUX_ACTUEL)` était déjà linéaire, donc
        s'étend correctement dans les deux sens (réduction de la base en dessous de 45%, ou
        universalisation à 100%) sans nouvelle hypothèse ajoutée.
        """
        taux_cible = params.get('taux_contribuables_cible', 0.45)  # 0.20-1.00

        # Clamp paramètre
        taux_cible = max(0.20, min(1.00, taux_cible))

        # Statu quo - Mise à jour DGFiP 2024
        TAUX_ACTUEL = 0.45  # 19M foyers / 41M total = 45% (DGFiP 2024)
        FOYERS_TOTAL = 41_000_000  # DGFiP/INSEE 2024

        if taux_cible == TAUX_ACTUEL:
            return 0.0, 0.0, {}

        # ===== NOUVEAUX CONTRIBUABLES =====
        nouveaux_contrib = FOYERS_TOTAL * (taux_cible - TAUX_ACTUEL)

        # ===== RECETTES ADDITIONNELLES =====
        # Nouveaux contribuables: revenus D4-D6 (classes moyennes basses)
        # Revenu imposable moyen: 18,000€
        # Taux effectif moyen: ~3% (après décote)
        REVENU_MOYEN_NOUVEAUX = 18000  # €
        TAUX_EFFECTIF_MOYEN = 0.03

        recettes_nouvelles = (nouveaux_contrib * REVENU_MOYEN_NOUVEAUX *
                             TAUX_EFFECTIF_MOYEN / 1e9)

        delta_revenue = recettes_nouvelles

        # ===== IMPACTS MACROÉCONOMIQUES =====
        impacts = {
            'recettes': delta_revenue,
        }

        delta_contrib = taux_cible - TAUX_ACTUEL

        # Gini: Impact ONE-TIME (changement structure fiscale)
        if self._is_first_year_change('elargissement_ir', {'taux_cible': taux_cible}):
            # Légèrement régressif (élargit mais touche classes moyennes D4-D6)
            impacts['gini'] = 0.005 * (delta_contrib / 0.20)
        else:
            impacts['gini'] = 0.0

        # Pouvoir d'achat: ONE-TIME (changement barème = ajustement revenu disponible une fois)
        if self._is_first_year_change('elargissement_ir_pa', {'taux_cible': taux_cible}):
            impacts['pouvoir_achat'] = -0.0006 * (delta_contrib / 0.20)
        else:
            impacts['pouvoir_achat'] = 0.0

        # Compétitivité: Neutre
        impacts['competitivite'] = 0.0

        _log_debug(self.debug_logs,
                   f"Y{year}: Élargissement IR - "
                   f"Contrib. {taux_cible*100:.1f}% (+{nouveaux_contrib/1e6:.1f}M foyers), "
                   f"Recettes +{delta_revenue:.1f}Md€")

        return 0, delta_revenue, impacts

    def _apply_fiscalite_patrimoine(self, measure: Dict, params: Dict, year: int,
                                    gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """
        Fiscalité patrimoine regroupée: IFI + Succession + Foncière

        Paramètre:
        - intensite (-0.3 à +0.3): Variation fiscalité patrimoine
          -0.3 = baisse 30% (convergence UE)
           0   = statu quo (53 Md€)
          +0.3 = hausse 30%

        Sources: DGFiP 2024, IPP taxation patrimoine UE, OCDE wealth tax
        """
        intensite = params.get('intensite', 0.0)  # -0.3 à +0.3
        # Redondant depuis Lot C Item 1 : la porte unique (engine/orchestrator
        # → _param_domain) borne déjà intensite à [-0.3, 0.3] en amont.
        # Conservé pour défense en profondeur et garantie golden master
        # byte-identique — ne pas retirer sans régénération auditée.
        intensite = max(-0.3, min(0.3, intensite))

        if intensite == 0:
            return 0.0, 0.0, {}

        # ===== BUDGET ACTUEL =====
        IFI_BASE = 2.0      # Md€
        SUCCESSION_BASE = 15.0  # Md€
        FONCIERE_BASE = 36.0    # Md€
        TOTAL_BASE = IFI_BASE + SUCCESSION_BASE + FONCIERE_BASE  # 53 Md€

        # ===== VARIATION =====
        delta_revenue = TOTAL_BASE * intensite

        # ===== IMPACTS MACROÉCONOMIQUES =====
        impacts = {
            'recettes': delta_revenue,
        }

        # Gini: Impact ONE-TIME (changement structure fiscale)
        if self._is_first_year_change('fiscalite_patrimoine', {'intensite': intensite}):
            # Fort effet redistributif si hausse (patrimoine concentré D9-D10)
            impacts['gini'] = -0.010 * (delta_revenue / 10.0)
        else:
            impacts['gini'] = 0.0

        # Pouvoir d'achat: ONE-TIME (changement structure fiscale)
        if self._is_first_year_change('fiscalite_patrimoine_pa', {'intensite': intensite}):
            impacts['pouvoir_achat'] = -0.0005 * intensite
        else:
            impacts['pouvoir_achat'] = 0.0

        # Compétitivité: Impact ONE-TIME (changement structure fiscale)
        # Règle : Hausse 10 Md€ = -0.002 compétitivité (exil fiscal entrepreneurs)
        params_patrimoine_comp = {'intensite': intensite}
        if self._is_first_year_change('fiscalite_patrimoine_competitivite', params_patrimoine_comp):
            impacts['competitivite'] = -0.002 * (delta_revenue / 10.0)  # ONE-TIME changement intensité
        else:
            impacts['competitivite'] = 0.0  # Niveau conservé dans indice

        _log_debug(self.debug_logs,
                   f"Y{year}: Fiscalité patrimoine {intensite*100:+.0f}% - "
                   f"Total = {TOTAL_BASE*(1+intensite):.1f}Md€ "
                   f"(delta {delta_revenue:+.1f}Md€)")

        return 0, delta_revenue, impacts

    def _apply_isf_climatique(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """ISF climatique. Slider intensité 0-100%. NFP: seuil 1.3M€, taux 1%, bonus 30% → 0-18 Md€. Remplace IFI (2 Md€).
        Sources: NFP 2027, OFCE 2024, EU Tax Observatory 2024. Voir METHODOLOGIE.md § Mesures Presidentielles 2027."""
        # ===== PARAMÈTRES - SLIDER INTENSITÉ UNIQUE =====
        # intensite : 0% (IFI maintenu) → 100% (ISF NFP maximal)
        # Mapping automatique : intensité → (seuil, taux, bonus)
        intensite = params.get('intensite', 0.0)  # 0.0 à 1.0 (0% à 100%)

        # Interpolation linéaire selon intensité
        # Intensité 0%   : IFI maintenu (seuil 2.0M€, taux 0%)
        # Intensité 50%  : ISF modéré (seuil 1.4M€, taux 0.6%, bonus 25%)
        # Intensité 100% : ISF NFP (seuil 1.3M€, taux 1%, bonus 30%)
        seuil_entree = 2.0 - (intensite * 0.7)  # 2.0 → 1.3 M€
        taux_max = intensite * 0.01  # 0% → 1.0%
        bonus_eco = 0.20 + (intensite * 0.10)  # 20% → 30%

        # Année de référence
        years_elapsed = year - POLICY_START_YEAR

        # ===== IFI DYNAMIQUE =====
        # IFI actuel avec croissance +2%/an (inflation patrimoniale INSEE 2015-2025)
        ifi_actuel = 2.0 * (1.02 ** max(0, years_elapsed))

        # Si maintien IFI actuel (seuil très élevé ou taux nul)
        # → Retourner 0 (pas de changement budgétaire par rapport à la baseline)
        # L'IFI continue à générer ses 2 Md€/an dans la baseline, mais aucun delta ici
        if seuil_entree >= 2.0 or taux_max == 0:
            return 0, 0, {'recettes': 0}

        # ===== PHASING 2 ANS (cadastre fiscal) =====
        # 0.5 l'année de mise en place, 1.0 ensuite (plein effet)
        phasing = _year_phasing(years_elapsed, (0.5, 1.0))

        # ===== NOMBRE DE FOYERS CONCERNÉS =====
        # Distribution patrimoniale française (IPP 2024) :
        # - 0.8M€ : 500k foyers (top 3%)
        # - 1.3M€ : 350k foyers (top 1.5%, proposition NFP)
        # - 1.6M€ : 220k foyers (top 1%)
        # - 2.0M€ : 130k foyers (top 0.5%)
        if seuil_entree <= 0.8:
            foyers_concernes = 500_000
        elif seuil_entree <= 1.3:
            foyers_concernes = 350_000
        elif seuil_entree <= 1.6:
            foyers_concernes = 220_000
        else:
            foyers_concernes = 130_000

        # ===== ASSIETTE MOYENNE PAR FOYER =====
        # Patrimoine moyen au-dessus du seuil (INSEE 2024, IPP 2025)
        # Calibré pour correspondre aux estimations OFCE 2024 (12 Md€ brutes pour NFP)
        if seuil_entree <= 0.8:
            assiette_moyenne = 3.0  # M€ (top 3%)
        elif seuil_entree <= 1.3:
            assiette_moyenne = 4.8  # M€ (top 1.5%, NFP cible)
        elif seuil_entree <= 1.6:
            assiette_moyenne = 5.5  # M€ (top 1%)
        else:
            assiette_moyenne = 6.5  # M€ (ultra-riches top 0.5%)

        # ===== BARÈME PROGRESSIF =====
        # Simplifié : taux effectif moyen = 75% du taux max
        # Barème NFP réel : 0.5% (1.3-2.5M€), 0.7% (2.5-5M€), 1.0% (>5M€)
        # Sources : OFCE 2024, IPP 2025 (estim. recettes 12 Md€ pour NFP)
        taux_effectif_moyen = taux_max * 0.75

        # ===== BONUS ÉCOLOGIQUE =====
        # Abattement sur actifs verts (énergies renouvelables, forêts certifiées)
        # Hypothèse : 20% du patrimoine éligible en moyenne
        part_actifs_verts = 0.20
        reduction_assiette = assiette_moyenne * part_actifs_verts * bonus_eco
        assiette_nette = assiette_moyenne - reduction_assiette

        # ===== RECETTES BRUTES =====
        # foyers × assiette(M€) × taux → millions € → Md€
        recettes_brutes = foyers_concernes * assiette_nette * taux_effectif_moyen * phasing / 1000  # Md€

        # ===== ÉVASION FISCALE =====
        # Exil fiscal et optimisation (Suisse, Luxembourg, trust)
        # Sources : EU Tax Observatory 2024, Gabriel Zucman
        taux_evasion = 0.15  # 15% patrimoine échappe à l'impôt
        recettes_nettes = recettes_brutes * (1 - taux_evasion)

        # ===== PLAFOND RÉALISTE =====
        # EU Tax Observatory 2024 : plafond 18 Md€ (scénarios ambitieux possibles)
        plafond_max = 18.0
        if recettes_nettes > plafond_max:
            recettes_nettes = plafond_max

        # ===== RECETTES NETTES (après remplacement IFI) =====
        # L'ISF Climatique REMPLACE l'IFI actuel
        # → Delta = Recettes ISF - Recettes IFI perdues (avec croissance +2%/an)
        delta_revenue = recettes_nettes - ifi_actuel

        # ===== IMPACTS MACROÉCONOMIQUES =====
        # Basés sur recettes_nettes (assiette totale taxée, effet redistributif absolu)
        # Sources : OFCE 2024, IPP 2025
        # IMPORTANT : Effets NIVEAU (one-time), pas FLUX (recurring)

        # Gini : -0.020 pour 12 Md€ (réduction forte inégalités via redistribution)
        # Impact appliqué UNE FOIS (changement structure revenus/patrimoine)
        impact_gini = _one_time_level(years_elapsed, -0.020 * (recettes_nettes / 12) * phasing)

        # Pouvoir d'achat : -0.001 (quasi-neutre, touche 1% population)
        # Impact appliqué UNE FOIS (changement consommation hauts patrimoines)
        impact_pa = _one_time_level(years_elapsed, -0.001 * (recettes_nettes / 12) * phasing)

        # Compétitivité : -0.002 (risque exil entrepreneurs)
        # Impact appliqué UNE FOIS (changement structure productive)
        impact_competitivite = _one_time_level(years_elapsed, -0.002 * (recettes_nettes / 12) * phasing)

        impacts = {
            'recettes': delta_revenue,
            'gini': impact_gini,
            'pouvoir_achat': impact_pa,
            'competitivite': impact_competitivite
        }

        _log_debug(self.debug_logs,
            f"Y{year}: ISF climatique - Seuil {seuil_entree}M€, Taux {taux_max*100:.1f}%, "
            f"Foyers {foyers_concernes/1000:.0f}k, Brutes {recettes_brutes:.1f} Md€, "
            f"Nettes {recettes_nettes:.1f} Md€, IFI {ifi_actuel:.1f} Md€, Delta {delta_revenue:+.1f} Md€"
        )

        return 0, delta_revenue, impacts

    def _apply_quotient_familial(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """Abaissement du plafond de l'avantage du quotient familial (par demi-part
        additionnelle). Plafond actuel (revenus 2024, impôt 2025) : 1791€ (Légifiscal/Sénat
        PLF 2025). Modèle LINÉAIRE calé sur le seul point de calibration réel disponible :
        la baisse PLF 2014 (2000€->1500€, -500€) avait été chiffrée par le gouvernement à
        +1,03 Md€ (Légifiscal, "PLF 2014 : abaissement du plafond de l'avantage procuré par
        le quotient familial"). `plafond`=1791 (défaut) = régime actuel, statu quo.
        LIMITE ASSUMÉE : pas d'élasticité comportementale dédiée publiée (pas de
        réoptimisation des revenus/structure familiale modélisée), et le coefficient est
        extrapolé hors de la plage observée (-500€) si l'écart demandé est plus grand — à
        traiter comme un ordre de grandeur, pas une prévision précise à grande échelle. Sans
        clé de ventilation par décile sourcée séparément pour LE QUOTIENT FAMILIAL SEUL
        (Insee Analyses n°53 ne publie qu'une concentration agrégée conjugal+familial par
        vingtile, pas un tableau décile par décile par dispositif) : mesure "non ventilée"
        dans decile.py, cf. docstring du module."""
        plafond = params.get('plafond', QUOTIENT_FAMILIAL_PLAFOND_REF_EUR)
        ecart_eur = QUOTIENT_FAMILIAL_PLAFOND_REF_EUR - plafond  # >0 si baisse du plafond

        if abs(ecart_eur) < 1e-9:
            return 0, 0, {}

        delta_revenue = ecart_eur * QUOTIENT_FAMILIAL_RENDEMENT_PAR_EURO_MD

        # Gini : ESTIMATION PAR ANALOGIE avec `impot_revenu` (même nature : barème IR
        # progressif, pas d'élasticité dédiée publiée pour CE levier précis). Progressif
        # (bénéficiaires concentrés dans les déciles supérieurs, Insee Analyses n°53).
        if self._is_first_year_change('quotient_familial', {'plafond': plafond}):
            gini = -0.004 * delta_revenue
            pouvoir_achat = -0.001 * delta_revenue
        else:
            gini = 0.0
            pouvoir_achat = 0.0

        impacts = {'recettes': delta_revenue, 'gini': gini, 'pouvoir_achat': pouvoir_achat}
        _log_debug(self.debug_logs,
            f"Y{year}: Quotient familial - Plafond {plafond:.0f}€ (réf. {QUOTIENT_FAMILIAL_PLAFOND_REF_EUR:.0f}€) -> "
            f"recettes {delta_revenue:+.2f} Md€"
        )
        return 0, delta_revenue, impacts

    def _apply_quotient_conjugal(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """Individualisation de l'impôt sur le revenu des couples mariés/pacsés (fin de
        l'imposition commune, 2 parts). `intensite`=0 (défaut) = statu quo (imposition
        commune maintenue), `intensite`=1.0 = individualisation complète avec option de
        rattachement des enfants conservée, +7,2 Md€/an (Insee, Économie et Statistique
        n°526-527, 2021, Allègre et al., simulation de 3 réformes du quotient conjugal —
        scénario retenu : celui qui préserve le mieux la progressivité sans pénaliser la
        prise en charge des enfants). Interpolation LINÉAIRE entre les deux bornes : les 2
        autres scénarios chiffrés par la même étude (réduction à 1,5 part : 3,8-4,8 Md€ ;
        plafonnement façon quotient familial : 2,9 Md€) ne sont pas modélisés ici, faute de
        source pour une interpolation non-linéaire entre les 3. Mesure STRUCTURELLE
        distincte de `quotient_familial` (mécanisme différent, sourcée séparément : Insee
        Analyses n°53 décompose le coût total 29,7 Md€ en 10,8 Md€ conjugal / 19,0 Md€
        familial — pas de double-comptage entre les deux leviers). Sans clé de ventilation
        par décile sourcée séparément pour ce levier précis (même limite que
        `quotient_familial` ci-dessus, Insee Analyses n°53 n'étant pas assez détaillée) :
        mesure "non ventilée" dans decile.py."""
        intensite = params.get('intensite', 0.0)

        if abs(intensite) < 1e-9:
            return 0, 0, {}

        delta_revenue = intensite * QUOTIENT_CONJUGAL_RENDEMENT_INDIVIDUALISATION_MD

        # Gini : ESTIMATION PAR ANALOGIE avec `impot_revenu`/`quotient_familial` (même
        # nature : réforme du barème IR, progressive car les gains de l'imposition commune
        # sont concentrés chez les couples aisés à un seul revenu, Insee 2021). Pouvoir
        # d'achat : concentré sur les couples mariés aisés, effet agrégat faible.
        if self._is_first_year_change('quotient_conjugal', {'intensite': intensite}):
            gini = -0.004 * delta_revenue
            pouvoir_achat = -0.0005 * delta_revenue
        else:
            gini = 0.0
            pouvoir_achat = 0.0

        impacts = {'recettes': delta_revenue, 'gini': gini, 'pouvoir_achat': pouvoir_achat}
        _log_debug(self.debug_logs,
            f"Y{year}: Quotient conjugal - Intensité {intensite*100:.0f}% -> recettes {delta_revenue:+.2f} Md€"
        )
        return 0, delta_revenue, impacts

    def _apply_pfu_bareme(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """Retour au barème progressif de l'IR pour les revenus du capital, à la place du
        prélèvement forfaitaire unique (PFU, taux global 30% depuis 2018). `intensite`=0
        (défaut) = PFU maintenu (statu quo), `intensite`=1.0 = retour intégral au barème.
        Rendement BRUT calé sur le coût permanent du PFU estimé par le comité d'évaluation
        France Stratégie (1,4-1,7 Md€/an, milieu de fourchette 1,55 Md€ retenu ; Sénat,
        rapport n°19-042-1, "Transformation de l'ISF en IFI et création du PFU : un premier
        bilan"). Facteur comportemental 0,85 : ESTIMATION (pas une élasticité publiée pour
        le sens inverse de la réforme) assumant qu'un retour au barème réduirait
        symétriquement le rebond de distribution de dividendes mesuré par l'IPP lors du
        passage au PFU (note n°46, 2019 : dividendes 29,8->37,1 Md€ entre 2017 et 2018,
        ~0,5 Md€ de recettes IR+PS additionnelles sur un rendement PFU réel 2018 de 3,5 Md€,
        soit 1 - 0,5/3,5 ≈ 0,85). Sans clé de ventilation par décile sourcée pour ce levier
        (IPP note n°46 ne publie pas de répartition par décile des bénéficiaires du PFU) :
        mesure "non ventilée" dans decile.py."""
        intensite = params.get('intensite', 0.0)

        if abs(intensite) < 1e-9:
            return 0, 0, {}

        delta_revenue = intensite * PFU_BAREME_RENDEMENT_BRUT_MD * PFU_BAREME_FACTEUR_COMPORTEMENTAL

        # Gini : ESTIMATION PAR ANALOGIE avec `fiscalite_patrimoine` (même nature :
        # fiscalité du capital, progressive car les revenus du capital sont concentrés dans
        # les déciles supérieurs, DGFiP). Compétitivité : léger effet négatif (attractivité
        # de l'épargne/investissement), ANALOGIE avec `isf_climatique`.
        if self._is_first_year_change('pfu_bareme', {'intensite': intensite}):
            gini = -0.004 * delta_revenue
            competitivite = -0.0015 * delta_revenue
        else:
            gini = 0.0
            competitivite = 0.0

        impacts = {'recettes': delta_revenue, 'gini': gini, 'competitivite': competitivite}
        _log_debug(self.debug_logs,
            f"Y{year}: PFU->barème - Intensité {intensite*100:.0f}% -> recettes {delta_revenue:+.2f} Md€"
        )
        return 0, delta_revenue, impacts

    def _apply_bareme_indexation(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """Ajout 2026-10 (fork VotePop, demande utilisateur suite à confusion avec
        `impot_revenu` : "il manque une carte avec un curseur d'ajustement des tranches
        des gens (tous niveaux) proportionnellement, comme ce qui se passe chaque année").
        DISTINCT de `impot_revenu` : ce dernier ne touche QUE le taux de la tranche
        supérieure (hauts revenus) et la décote (bas de barème) ; ce levier-ci simule un
        ajustement de l'INDEXATION DE TOUTES LES TRANCHES sur l'inflation — le mécanisme
        qui, chaque année, relève (ou non) les seuils du barème pour suivre la hausse des
        prix. Un barème sous-indexé ("gel du barème") fait mécaniquement payer PLUS
        d'impôt à TOUS les foyers imposables (leur revenu nominal progresse avec
        l'inflation, les seuils non) ; un barème sur-indexé fait l'inverse.

        `ajustement_pts` = écart d'indexation en points par rapport à l'inflation
        constatée (0 = indexation normale/statu quo, valeur par défaut). Négatif =
        sous-indexation ("gel" partiel ou total) = hausse d'impôt pour tous les foyers
        imposables. Positif = sur-indexation = baisse d'impôt pour tous.

        Calibrage : ESTIMATION PROPRE, pas une projection officielle. Point de référence
        repris de la presse économique lors des débats PLF 2025 sur un gel du barème
        (ordre de grandeur ~3,7 Md€/an pour un gel total face à une inflation d'environ
        2 pts), d'où un rendement d'environ 1,85 Md€ par point de sous-indexation,
        appliqué ICI de façon linéaire et constante (pas de recalibrage dynamique sur
        l'inflation réellement simulée année par année — limite assumée). Ventilation par
        décile dans decile.py (`DECILE_SHARES["bareme_indexation"]`) : ESTIMATION PAR
        ANALOGIE avec la concentration connue de l'IR par décile (DGFiP), faute de table
        dédiée à l'effet d'un écart d'indexation du barème — cf. docstring de cette clé pour
        le détail et les limites assumées.
        """
        ajustement_pts = params.get('ajustement_pts', 0.0)

        if abs(ajustement_pts) < 1e-9:
            return 0, 0, {}

        RENDEMENT_PAR_POINT_MD = 1.85  # Estimation propre (voir docstring), non sourcée officiellement
        delta_revenue = -ajustement_pts * RENDEMENT_PAR_POINT_MD

        # Gini / pouvoir d'achat : effet DIFFUS sur tous les foyers imposables (pas ciblé
        # comme `impot_revenu`/tranche sup), donc un impact par unité de recette plus
        # faible — ESTIMATION PAR ANALOGIE avec les autres leviers IR de ce fichier.
        if self._is_first_year_change('bareme_indexation', {'ajustement_pts': ajustement_pts}):
            gini = -0.0015 * delta_revenue
            pouvoir_achat = -0.0008 * delta_revenue
        else:
            gini = 0.0
            pouvoir_achat = 0.0

        impacts = {'recettes': delta_revenue, 'gini': gini, 'pouvoir_achat': pouvoir_achat}
        _log_debug(self.debug_logs,
            f"Y{year}: Indexation barème - Ajustement {ajustement_pts:+.1f}pt -> recettes {delta_revenue:+.2f} Md€"
        )
        return 0, delta_revenue, impacts

    def _apply_accises(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """Levier sur le NIVEAU GLOBAL des droits d'accise indirects — TICPE
        (carburants) + droits de consommation sur le tabac + droits sur les alcools —,
        ajouté 2026-10 suite à une comparaison avec un simulateur tiers
        (github.com/Vadech/moi-president) qui porte ce lever sous le nom "Excises/
        product taxes" ; confirmation explicite utilisateur ("accise ok"). DISTINCT de
        `tva_rate`/`tva_energie` : ce sont des droits SPÉCIFIQUES (montant fixe par
        unité physique — hL, 1000 cigarettes — indexé), pas un taux ad valorem, donc un
        levier séparé plutôt qu'un paramètre de plus sur `tva_rate`.
        `variation_pct`=0 (défaut) = statu quo ; une variation relative est appliquée
        IDENTIQUEMENT aux 3 composantes (pas de curseur séparé par produit, faute
        d'élasticité comportementale publiée distinguant les 3 avec la même précision).
        Assiette 49,0 Md€/an = TICPE 30,5 Md€ (2022, ministère Transition écologique,
        ordre de grandeur stable 2023-2024) + droits tabac 13,95 Md€ (2024 prévision,
        Sénat rapport n°638 2023-2024, données DGDDI) + droits alcools 4,565 Md€ (2024
        provisoire, même source) — cf. constants.py pour le détail et les URLs. Élasticité
        -0,4 : ESTIMATION PAR ANALOGIE, reprise du tabac (seule élasticité-prix publiée
        avec cette précision parmi les 3, même rapport Sénat n°638) et appliquée aux 3
        composantes faute de mieux, même démarche que `tva_rate`/`tva_energie`
        ci-dessus. LIMITE ASSUMÉE : pas de ventilation par décile sourcée construite ici
        malgré une étude de régressivité réelle trouvée pour CES 3 taxes précisément
        (Insee ES413, Ruiz & Trannoy 2008, taux d'effort D1 4,3% vs D10 1,3% du revenu) —
        cette étude ne publie pas le revenu moyen par décile dans le même tableau, et le
        croiser avec une autre source pour fabriquer les 10 parts sommant à 1 serait une
        combinaison non publiée telle quelle (même discipline que `quotient_familial`
        ci-dessus) ; `accises` reste "non ventilée" dans `decile.py`, mais le facteur
        gini/pouvoir d'achat ci-dessous EST calibré (par analogie, cf. constants.py) sur
        cette étude pour refléter une régressivité plus marquée que `tva_energie`."""
        variation_pct = params.get('variation_pct', 0.0)

        if abs(variation_pct) < 1e-9:
            return 0, 0, {}

        # === RECETTES ===
        # Amortissement comportemental (élasticité-prix -0,4, cf. docstring/constants.py) :
        # une hausse (variation_pct>0) réduit le volume consommé, donc l'assiette
        # effective ; une baisse l'augmente symétriquement — même mécanique que
        # `tva_rate` (adjusted_base ci-dessus dans ce fichier).
        adjusted_base = ACCISES_BASE_TOTAL_MD_EUR * (1 + ACCISES_ELASTICITE_PRIX * variation_pct)
        delta_revenue = variation_pct * max(0.0, adjusted_base)

        # === IMPACTS MACROÉCONOMIQUES ===
        # Effets NIVEAU one-time (changement structurel du niveau des droits, pas un flux
        # qui s'accumulerait année après année) — même idiome que `tva_energie` ci-dessus
        # (years_elapsed == 0), pas `_is_first_year_change` (cohérence avec le handler le
        # plus proche par nature : taxe de consommation régressive à taux modifiable).
        years_elapsed = year - POLICY_START_YEAR
        phasing = _year_phasing(years_elapsed, (1.0,))  # effet immédiat, pas de montée en charge

        # Gini : accises = régressives (Insee ES413 : D1 paie 4,3% de son revenu en
        # accises comportementales contre 1,3% pour D10). Une hausse (variation_pct>0)
        # dégrade le Gini (+), une baisse l'améliore (-).
        gini = _one_time_level(years_elapsed, ACCISES_GINI_FACTEUR * variation_pct * phasing)

        # Pouvoir d'achat : une hausse de variation_pct renchérit le prix TTC des produits
        # concernés d'environ variation_pct (la hausse du droit spécifique se répercute sur
        # le prix), pesant sur le pouvoir d'achat à hauteur de la part de ces 3 produits
        # dans le revenu disponible (ACCISES_PART_REVENU_MOYENNE, cf. constants.py).
        pouvoir_achat = _one_time_level(years_elapsed, -variation_pct * ACCISES_PART_REVENU_MOYENNE * phasing)

        # Compétitivité : NON modélisée (0,0), faute de source dédiée — contrairement à
        # `impots_production`/`cotisations_patronales`, ces 3 accises pèsent
        # essentiellement sur la consommation FINALE des ménages (TICPE bénéficie déjà de
        # remboursements partiels pour le transport routier professionnel/l'agriculture,
        # qui amortissent l'impact entreprise ; droits tabac/alcool sont des taxes de
        # consommation finale par construction). Laissé à 0,0 plutôt qu'un chiffre inventé.
        competitivite = 0.0

        impacts = {
            'recettes': delta_revenue,
            'gini': gini,
            'pouvoir_achat': pouvoir_achat,
            'competitivite': competitivite,
        }
        _log_debug(self.debug_logs,
            f"Y{year}: Accises (TICPE+tabac+alcool) - Variation {variation_pct*100:+.1f}% -> "
            f"recettes {delta_revenue:+.2f} Md€"
        )
        return 0, delta_revenue, impacts

