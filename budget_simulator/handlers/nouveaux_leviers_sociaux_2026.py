"""Nouveaux leviers sociaux — fork VotePop, ajoutés 2026-10 à la demande de
l'utilisateur (PAS dans le dépôt original cturkieh/france-budget-simulateur,
ni dans les lots fork précédents).

MÊME CONVENTION D'HONNÊTETÉ que ``handlers/nouvelles_taxes_2027.py`` : modèle
linéaire simple, coefficients par EXTRAPOLATION/ANALOGIE avec des mécanismes
déjà calibrés ailleurs dans ce moteur (notamment ``cotisations_patronales``,
``handlers/competitivite.py``) — PAS une élasticité dédiée publiée pour cette
mesure précise. Détail des hypothèses et sources : ``constants.py`` § Nouveaux
leviers sociaux 2026-10.

- ``exoneration_heures_sup`` : exonération de cotisations PATRONALES sur les
  heures travaillées au-delà de 35h/semaine. Mesure STANDALONE (id propre),
  à distinguer des 2 autres leviers demandés dans le même lot (âge du taux
  plein, indexation SMIC) qui sont des SOUS-PARAMÈTRES de mesures existantes
  (``retraites``/``smic``) et vivent donc dans leurs handlers respectifs
  (``handlers/depenses.py``, ``handlers/additionnels.py``), pas ici.

Effet emploi NON modélisé : la littérature sur les heures supplémentaires
défiscalisées (loi TEPA 2007-2012) est ambiguë sur l'arbitrage heures
travaillées / nouvelles embauches, et aucune élasticité consensuelle n'a été
identifiée pour ce lot — seuls les effets recettes et compétitivité sont
chiffrés, pour éviter un coefficient emploi inventé.

Le mixin accède à ``self.debug_logs``, attribut d'instance de
``BudgetSimulatorV45`` (même convention que les autres mixins de
``handlers/``).
"""
import logging
from typing import TYPE_CHECKING, Dict, Tuple

from ..constants import (
    EXONERATION_HEURES_SUP_BASE_MD_EUR,
    EXONERATION_HEURES_SUP_COEFF_COMPETITIVITE,
    POLICY_START_YEAR,
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


class NouveauxLeviersSociaux2026Mixin(_MixinBase):
    """Handler du nouveau levier social ajouté au fork en 2026-10."""

    def _apply_exoneration_heures_sup(self, measure: Dict, params: Dict, year: int, gdp: float, inflation: float, unemployment: float) -> Tuple[float, float, ImpactsDict]:
        """Exonération de cotisations patronales sur les heures travaillées au-delà de
        35h/semaine. `taux`=0 (défaut) = statu quo (aucune exonération spécifique
        aujourd'hui). Base de cotisations concernée ≈4,17 Md€/an : 650 millions d'heures
        sup/an secteur privé (DARES, enquête Acemo 2016, citée par OFCE) × salaire horaire
        brut moyen 23,75€ (INSEE, Insee Première n°2079, oct. 2025, salaires secteur privé
        2024) × taux de cotisations patronales de référence 27% — cf constants.py pour le
        détail et les URLs. Modèle linéaire : l'exonération réduit les recettes de
        cotisations proportionnellement au taux. Effet compétitivité one-time par ANALOGIE
        avec le coefficient Md€ de `cotisations_patronales` (DG Trésor 2019). Pas d'effet
        emploi/chômage modélisé (littérature TEPA ambiguë sur l'arbitrage heures/embauches,
        cf docstring module)."""
        taux = params.get('taux', 0)
        if not taux:
            return 0, 0, {}

        years_elapsed = year - POLICY_START_YEAR

        # Recettes : exonération = moins de cotisations patronales perçues sur
        # l'assiette heures sup (pérenne, proportionnelle au taux d'exonération).
        delta_revenue = -taux * EXONERATION_HEURES_SUP_BASE_MD_EUR

        # Compétitivité : baisse de coût du travail marginal -> gain de
        # compétitivité, ONE-TIME (structure de coûts), même coefficient Md€
        # que `cotisations_patronales` (ESTIMATION PAR ANALOGIE).
        impact_competitivite = _one_time_level(
            years_elapsed, -delta_revenue * EXONERATION_HEURES_SUP_COEFF_COMPETITIVITE
        )

        impacts = {'recettes': delta_revenue, 'competitivite': impact_competitivite}
        _log_debug(self.debug_logs,
            f"Y{year}: Exonération heures sup taux {taux*100:.0f}% -> "
            f"recettes {delta_revenue:+.2f} Md€"
        )
        return 0, delta_revenue, impacts
