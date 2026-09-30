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
  (ex. fraude_fiscale, éducation, transition écologique...) n'ont pas de clé
  de répartition par décile sourcée de notre côté — elles restent "non
  ventilées" plutôt que de se voir attribuer une hypothèse inventée.
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
    "retraites": {
        "shares": [0.03, 0.059, 0.07, 0.08, 0.089, 0.1, 0.112, 0.129, 0.162, 0.17],
        "source": "Part de la masse des pensions de retraite par décile — DREES, Les retraités et les retraites, éd. 2025, voir classeur Excel.",
        "note_rapprochement": None,
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
