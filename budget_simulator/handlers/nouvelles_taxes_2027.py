"""Nouveaux leviers fiscaux — fork VotePop, ajoutés 2026-10 (PAS dans le dépôt
original cturkieh/france-budget-simulateur).

CONTEXTE : comparaison menée avec monbudgetpourlafrance.fr et l'IPP (voir
CHANGES.md) pour identifier des leviers fiscaux absents du moteur d'origine.
4 candidats jugés suffisamment sourcés ont été retenus ici (CVAE écartée —
risque de double-comptage avec ``impots_production`` ; Pilier 2/impôt
minimum mondial et taxation du cannabis écartées — rendement trop incertain
ou hypothèse non actée) :

- ``ttf`` : taxe sur les transactions financières (achats d'actions de
  sociétés françaises cotées, seuil de capitalisation ~1 Md€).
- ``taxe_gafa`` : taxe sur les services numériques ("taxe GAFA"), seuil de
  chiffre d'affaires mondial 750 M€.
- ``cdhr`` : Contribution Différentielle sur les Hauts Revenus (impôt
  minimum sur les très hauts revenus, PLF 2025).
- ``taxe_holdings_patrimoniales`` : taxe sur le patrimoine financier des
  holdings "patrimoniales" familiales (PLF 2026, article 3).
- ``taxe_zucman`` (ajouté 2026-10, lot "grille de tri 12 pistes") : plancher
  d'imposition de 2% sur le patrimoine net des foyers détenant plus de
  100 M€ (proposition Gabriel Zucman, rapport au G20 2024, ~1800 foyers en
  France). DISTINCTE de ``isf_climatique`` : cette dernière est un ISF
  PROGRESSIF classique (seuil ~0,8-2 M€, barème 0-1%, bonus actifs verts,
  remplace l'IFI) qui touche un bien plus grand nombre de foyers patrimoniaux
  "ordinaires" ; ``taxe_zucman`` est un PLANCHER anti-optimisation ne visant
  que l'ultra-haut de la distribution (>100 M€, holdings), sans bonus
  écologique ni remplacement d'un impôt existant. Les deux peuvent en théorie
  coexister dans un scénario sans double-compter la même assiette (seuils
  disjoints), mais ce n'est pas garanti pour les foyers à la frontière — non
  modélisé ici (limite assumée).

MODÉLISATION — LIMITE ASSUMÉE COMMUNE AUX 4 MESURES : le rendement est
modélisé en LOI LINÉAIRE simple (delta proportionnel à l'écart au taux/
barème actuel), sans courbe d'élasticité comportementale propre sourcée pour
CES mesures précises (contrairement à ``tva_rate``/``impot_societes`` qui
ont leurs propres élasticités documentées ailleurs dans ce moteur). Les
impacts macro secondaires (compétitivité, Gini) sont de même une
EXTRAPOLATION PAR ANALOGIE avec l'ordre de grandeur déjà utilisé pour
``taxe_superprofits`` dans ``additionnels.py`` (même moteur, mesure de
nature comparable — taxe ciblée sur une assiette étroite), faute
d'élasticité dédiée publiée pour ces 4 mesures. Aucune de ces 4 mesures
n'a de clé de ventilation par décile/taille d'entreprise sourcée à ce
stade — elles apparaissent donc "non ventilées" dans ``decile.py``/
``ventilation_taille.py``, à l'exception de ``ttf``/``taxe_gafa`` : ces deux
mesures sont ventilées 100% "GE" dans ``ventilation_taille.py`` non pas par
hypothèse mais parce que leur PÉRIMÈTRE LÉGAL LUI-MÊME ne vise que les
grandes entreprises (seuils de capitalisation/chiffre d'affaires), même
principe que les mesures "TGE" déjà présentes.

Sources détaillées (montants, taux, dates) : voir CHANGES.md, entrée
"2026-10 — nouveaux leviers fiscaux".

Le mixin accède à ``self.mesures`` et ``self.debug_logs``, attributs
d'instance de ``BudgetSimulatorV45`` (même convention que les autres
mixins de ``handlers/``).
"""
import logging
from typing import TYPE_CHECKING, Dict, Tuple

from ..constants import (
    POLICY_START_YEAR,
    TAXE_ZUCMAN_RENDEMENT_BRUT_PROPOSANT_MD, TAXE_ZUCMAN_RENDEMENT_NET_CRITIQUE_MD,
)
from .._logging import _log_debug
from ._phasing import _one_time_level
from ._types import ImpactsDict

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ._types import _SimulatorState

    _MixinBase = _SimulatorState
else:
    _MixinBase = object


class NouvellesTaxes2027Mixin(_MixinBase):
    """Handlers des 4 nouveaux leviers fiscaux ajoutés au fork en 2026-10."""

    def _apply_ttf(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """Taxe sur les transactions financières. Taux actuel 0.4% (relevé depuis 0.3% en
        avril 2025) -> rendement 2.5 Md€/an (2025). Le relèvement de 0.1pt (0.3%->0.4%) a
        généré ~0.5 Md€/an supplémentaire -> modèle linéaire rendement/point = 500 Md€ par
        point de taux plein (0.5 Md€ / 0.001 de taux). Source : moneyvox.fr, "Taxe sur les
        transactions financières : quel bilan 15 ans après ?" (2025)."""
        taux = params.get('taux', 0.004)
        years_elapsed = year - POLICY_START_YEAR
        RENDEMENT_PAR_POINT = 500.0  # Md€ par 100% de taux ; 0.001 de taux -> 0.5 Md€
        delta_revenue = (taux - 0.004) * RENDEMENT_PAR_POINT

        if abs(delta_revenue) < 1e-9:
            return 0, 0, {}

        # Impact compétitivité : extrapolation par analogie avec taxe_superprofits
        # (-0.005 pour 15 Md€ de recette) — pas d'élasticité TTF-spécifique sourcée.
        # Limite assumée : le risque de délocalisation des transactions (place financière)
        # n'est pas modélisé indépendamment du niveau de recette généré.
        impact_competitivite = _one_time_level(years_elapsed, -0.005 * (delta_revenue / 15))

        impacts = {'recettes': delta_revenue, 'competitivite': impact_competitivite}
        _log_debug(self.debug_logs, f"Y{year}: TTF taux {taux*100:.2f}% -> recettes {delta_revenue:+.2f} Md€")
        return 0, delta_revenue, impacts

    def _apply_taxe_gafa(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """Taxe sur les services numériques ("taxe GAFA"). Taux actuel 3%, seuil CA mondial
        750 M€ -> rendement ~0.7 Md€/an (2024). Modèle linéaire : rendement proportionnel au
        taux (assiette assujettie supposée stable ; le relèvement de seuil à 2 Md€ proposé en
        PLF 2026 réduirait le nombre d'entreprises assujetties, NON modélisé ici — limite
        assumée). Source : legifiscal.fr, "PLF 2026 : un amendement double le taux de la taxe
        GAFAM" (28/10/2025)."""
        taux = params.get('taux', 0.03)
        years_elapsed = year - POLICY_START_YEAR
        RENDEMENT_BASE = 0.7  # Md€/an au taux actuel 3%
        TAUX_BASE = 0.03
        delta_revenue = (taux / TAUX_BASE - 1) * RENDEMENT_BASE if TAUX_BASE else 0.0

        if abs(delta_revenue) < 1e-9:
            return 0, 0, {}

        # Impact compétitivité : extrapolation par analogie avec taxe_superprofits,
        # coefficient légèrement supérieur (secteur tech plus mobile) — non sourcé spécifiquement.
        impact_competitivite = _one_time_level(years_elapsed, -0.003 * (delta_revenue / 0.7))

        impacts = {'recettes': delta_revenue, 'competitivite': impact_competitivite}
        _log_debug(self.debug_logs, f"Y{year}: Taxe GAFA taux {taux*100:.1f}% -> recettes {delta_revenue:+.2f} Md€")
        return 0, delta_revenue, impacts

    def _apply_cdhr(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """Contribution Différentielle sur les Hauts Revenus. Impôt minimum sur les très
        hauts revenus (PLF 2025). Prévision initiale 2.0 Md€, révisée à 1.5 Md€, mais
        rendement RÉELLEMENT CONSTATÉ (DGFiP) très inférieur : ~0.4 Md€ (2025), ~0.65 Md€
        projetés (2026) -- écart attribué à l'optimisation comportementale (report de
        dividendes, arbitrage rémunération/dividendes des dirigeants-actionnaires).
        `intensite`=1.0 = régime actuel (rendement RÉEL 2026, pas la prévision initiale).
        LIMITE ASSUMÉE : loi linéaire simple autour du rendement réel constaté ; ne modélise
        pas de "re-saturation" de l'écart comportemental si l'intensité augmente au-delà de 1
        (aucune étude ne permet de chiffrer à quel point un durcissement réduirait
        l'optimisation). Source : Deloitte Avocats, "La CDHR : un impôt minimum sur les
        revenus du capital... au rendement décevant"."""
        intensite = params.get('intensite', 1.0)
        years_elapsed = year - POLICY_START_YEAR
        RENDEMENT_REEL_2026 = 0.65  # Md€, projection DGFiP citée par Deloitte Avocats
        delta_revenue = (intensite - 1.0) * RENDEMENT_REEL_2026

        if abs(delta_revenue) < 1e-9:
            return 0, 0, {}

        # Impact Gini : extrapolation par analogie (redistribution capital -> État), même
        # ordre de grandeur que taxe_superprofits rapporté à son propre rendement de référence.
        impact_gini = _one_time_level(years_elapsed, -0.01 * (delta_revenue / RENDEMENT_REEL_2026))

        impacts = {'recettes': delta_revenue, 'gini': impact_gini}
        _log_debug(self.debug_logs, f"Y{year}: CDHR intensité {intensite:.1f} -> recettes {delta_revenue:+.2f} Md€")
        return 0, delta_revenue, impacts

    def _apply_taxe_holdings_patrimoniales(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """Taxe sur le patrimoine financier des holdings "patrimoniales" familiales (PLF
        2026, article 3) : 2% sur la valeur nette des actifs financiers non professionnels de
        holdings familiales détenant >=5 M€ d'actifs concernés, dont les revenus passifs
        dépassent 50% du total. Rendement estimé ~1.0 Md€/an à compter de 2026. Modèle
        linéaire (rendement proportionnel au taux). `taux`=0.02 (2%) = régime PLF 2026 adopté,
        valeur par défaut = loi en vigueur (même convention que les autres leviers fiscaux de
        ce mockup). Source : legifiscal.fr, "PLF 2026 : instauration d'une taxe sur le
        patrimoine financier des holdings patrimoniales" (10/2025)."""
        taux = params.get('taux', 0.02)
        years_elapsed = year - POLICY_START_YEAR
        RENDEMENT_BASE = 1.0  # Md€/an au taux actuel 2% (PLF 2026)
        TAUX_BASE = 0.02
        delta_revenue = (taux / TAUX_BASE - 1) * RENDEMENT_BASE if TAUX_BASE else 0.0

        if abs(delta_revenue) < 1e-9:
            return 0, 0, {}

        # Impact Gini : extrapolation par analogie avec taxe_superprofits (taxe assise sur du
        # patrimoine financier détenu par des holdings familiales -> redistribution capital ->
        # État), coefficient identique à taxe_superprofits faute de source dédiée.
        impact_gini = _one_time_level(years_elapsed, -0.01 * (delta_revenue / max(RENDEMENT_BASE, 1e-9)))

        impacts = {'recettes': delta_revenue, 'gini': impact_gini}
        _log_debug(self.debug_logs, f"Y{year}: Taxe holdings patrimoniales taux {taux*100:.1f}% -> recettes {delta_revenue:+.2f} Md€")
        return 0, delta_revenue, impacts

    def _apply_taxe_zucman(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """Taxe "Zucman" : plancher d'imposition de 2% sur le patrimoine net des foyers
        détenant plus de 100 M€ (~1800 foyers en France), proposition Gabriel Zucman (rapport
        au G20, 2024). `intensite`=0 (défaut) = non appliquée, `intensite`=1.0 = taux plein 2%.
        DEUX estimations de rendement, délibérément TOUTES LES DEUX exposées (pas de
        "vrai" chiffre tranché par le moteur, le débat n'étant pas tranché dans la réalité) :
        - Estimation du PROPOSANT (Zucman) : 20 Md€/an (±5 Md€), Public Sénat, "Taxe Zucman :
          quels sont les arguments pour, et les arguments contre ?".
        - Contre-estimation (critique sourcée) : iFRAP, "Fiscalité des riches : le mirage des
          milliards € de recettes", chiffre un rendement RÉEL de 2 à 3 Md€/an, au motif que
          l'estimation Zucman ne défalque pas l'IS déjà acquitté par les sociétés détenues au
          niveau des holdings (double imposition du même résultat économique). Risque
          constitutionnel documenté par ailleurs : le Conseil constitutionnel avait censuré en
          2012 un taux marginal de 1,8% jugé confiscatoire (même source Public Sénat).
        `part_critique` (0 à 1, défaut 0,5) : curseur SECONDAIRE assumé par ce moteur (pas une
        pondération publiée) pour permettre à l'utilisateur-analyste de situer son scénario
        entre les deux bornes sourcées, plutôt que d'en choisir une arbitrairement à sa place.
        0 = rendement plein du proposant (20 Md€ au taux plein), 1 = rendement net de la
        critique (2,5 Md€ au taux plein, milieu de la fourchette 2-3 Md€ iFRAP)."""
        intensite = params.get('intensite', 0.0)
        part_critique = params.get('part_critique', 0.5)
        part_critique = max(0.0, min(1.0, part_critique))

        if abs(intensite) < 1e-9:
            return 0, 0, {}

        rendement_taux_plein = (
            (1 - part_critique) * TAXE_ZUCMAN_RENDEMENT_BRUT_PROPOSANT_MD
            + part_critique * TAXE_ZUCMAN_RENDEMENT_NET_CRITIQUE_MD
        )
        delta_revenue = intensite * rendement_taux_plein

        # Gini : ANALOGIE avec `taxe_holdings_patrimoniales`/`cdhr` (même nature : taxe
        # ciblée sur une assiette patrimoniale ultra-étroite -> redistribution capital ->
        # État), même coefficient de référence faute d'élasticité dédiée publiée.
        years_elapsed = year - POLICY_START_YEAR
        impact_gini = _one_time_level(years_elapsed, -0.01 * (delta_revenue / max(rendement_taux_plein, 1e-9)))
        # Compétitivité : risque d'exil fiscal/optimisation accrue aux ultra-hauts
        # patrimoines (holdings), ANALOGIE avec `isf_climatique` (-0.002 pour son rendement
        # de référence 12 Md€), rapporté ici au rendement de ce levier.
        impact_competitivite = _one_time_level(years_elapsed, -0.002 * (delta_revenue / max(rendement_taux_plein, 1e-9)))

        impacts = {'recettes': delta_revenue, 'gini': impact_gini, 'competitivite': impact_competitivite}
        _log_debug(self.debug_logs,
            f"Y{year}: Taxe Zucman intensité {intensite*100:.0f}% (part_critique {part_critique:.2f}) -> "
            f"recettes {delta_revenue:+.2f} Md€"
        )
        return 0, delta_revenue, impacts
