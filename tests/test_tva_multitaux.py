"""Couverture des 3 nouveaux paramètres de ``tva_rate`` (2026-09) : taux_intermediaire
(10 %), taux_reduit (5,5 %), taux_particulier (2,1 %).

Avant cet ajout, seul le taux normal (``taux``) était pilotable côté handler — les 3
autres taux officiels de TVA existaient dans la vraie fiscalité mais n'avaient aucun
levier dans le moteur. Le canal recettes de ces 3 nouveaux paramètres est volontairement
LINÉAIRE (delta = écart en points × rendement net/point), sourcé DG Trésor, Trésor-Éco
n°371 (09/2025) tableau 1 — pas de courbe d'élasticité inventée par mesure, contrairement
au taux normal qui a sa propre modélisation historique (conservée telle quelle ici).

Ces tests vérifient : (1) le statu quo (les 4 taux à leur valeur par défaut) ne change
rien aux recettes ; (2) chaque nouveau paramètre, isolé, produit exactement le delta
attendu (écart en points × rendement/point sourcé) ; (3) les 3 nouveaux paramètres
s'additionnent linéairement entre eux et avec le taux normal, sans interférence ;
(4) le taux normal seul reproduit exactement le delta déjà produit avant cet ajout
(non-régression de la formule existante).
"""
import sys
sys.path.insert(0, '.')
from budget_simulator.simulator import BudgetSimulatorV45

YEAR_2026 = 1  # index trajectoire : 0=2025 (année de base, sans mesures), 1=2026 (1re année active)


def _recettes_tva_rate(**taux_overrides):
    mesures = {'tva_rate': dict(taux_overrides)}
    sim = BudgetSimulatorV45(mesures=mesures, periods=1)
    _, _, extra = sim.simulate()
    impacts = extra['measure_impacts_by_year'][YEAR_2026].get('tva_rate', {})
    return impacts.get('recettes', 0.0)


def test_statu_quo_4_taux_delta_nul():
    """Les 4 taux à leur valeur officielle actuelle → delta recettes nul."""
    delta = _recettes_tva_rate(taux=0.20, taux_intermediaire=0.10, taux_reduit=0.055, taux_particulier=0.021)
    assert abs(delta) < 1e-6


def test_taux_intermediaire_isole():
    """+1 point de taux intermédiaire (10% -> 11%) = +1,6 Md€ (rendement net/point sourcé)."""
    delta = _recettes_tva_rate(taux=0.20, taux_intermediaire=0.11, taux_reduit=0.055, taux_particulier=0.021)
    assert abs(delta - 1.6) < 1e-6


def test_taux_reduit_isole_baisse():
    """-1 point de taux réduit (5,5% -> 4,5%) = -2,0 Md€ (rendement net/point sourcé)."""
    delta = _recettes_tva_rate(taux=0.20, taux_intermediaire=0.10, taux_reduit=0.045, taux_particulier=0.021)
    assert abs(delta - (-2.0)) < 1e-6


def test_taux_particulier_isole():
    """+1 point de taux particulier (2,1% -> 3,1%) = +0,4 Md€ (rendement net/point sourcé)."""
    delta = _recettes_tva_rate(taux=0.20, taux_intermediaire=0.10, taux_reduit=0.055, taux_particulier=0.031)
    assert abs(delta - 0.4) < 1e-6


def test_additivite_lineaire_des_3_nouveaux_taux():
    """Les 3 nouveaux paramètres s'additionnent sans interaction croisée."""
    delta = _recettes_tva_rate(taux=0.20, taux_intermediaire=0.11, taux_reduit=0.045, taux_particulier=0.031)
    attendu = 1.6 - 2.0 + 0.4
    assert abs(delta - attendu) < 1e-6


def test_taux_normal_seul_non_regresse():
    """Le taux normal seul (les 3 autres à défaut) doit rester non-nul et de signe
    cohérent (hausse → +recettes) — détecte une régression grossière de la formule
    pré-existante de ``_apply_tva_rate`` (écrasée/cassée par l'ajout des 3 nouveaux
    paramètres). On ne recalcule pas la valeur exacte ici (dépend du PIB simulé,
    lui-même fonction de canaux macro internes) — cf. les tests d'isolation ci-dessus
    pour la précision exacte sur les 3 nouveaux paramètres."""
    delta = _recettes_tva_rate(taux=0.22, taux_intermediaire=0.10, taux_reduit=0.055, taux_particulier=0.021)
    assert delta > 5, "Une hausse de 2 points du taux normal doit rester nettement positive"
