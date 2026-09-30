"""Tests du module AJOUT NON-ORIGINAL `budget_simulator/decile.py` — ventilation
par décile de niveau de vie. N'appartient pas au dépôt cturkieh/france-budget-
simulateur d'origine ; vérifie que notre extension respecte ses propres
invariants sans toucher au moteur macro existant."""
import pytest

from budget_simulator.decile import DECILE_SHARES, decile_breakdown


def test_toutes_les_cles_de_repartition_totalisent_100_pour_cent():
    """Chaque table de parts par décile doit sommer à 1.0 (100%) : sinon une
    mesure ventilée perdrait ou gagnerait artificiellement du Md€ au passage."""
    for mesure, cfg in DECILE_SHARES.items():
        total = sum(cfg["shares"])
        # Tolérance 0.005 : même convention que les contrôles de cohérence du
        # classeur Excel du projet (arrondi des sources à 3-5 décimales).
        assert total == pytest.approx(1.0, abs=0.005), (
            f"{mesure} : les parts par décile totalisent {total}, pas 1.0"
        )


def test_toutes_les_cles_ont_exactement_10_deciles():
    for mesure, cfg in DECILE_SHARES.items():
        assert len(cfg["shares"]) == 10, f"{mesure} n'a pas 10 valeurs de décile"


def test_decile_breakdown_ventile_une_mesure_connue():
    measure_impacts_by_year = [
        {"Année": 2025},
        {"Année": 2026, "tva_rate": {"recettes": 10.0, "depenses": 0.0}},
    ]
    out = decile_breakdown(measure_impacts_by_year)
    assert "tva_rate" in out["par_mesure"]
    assert out["par_mesure"]["tva_rate"]["total_md_eur"] == pytest.approx(10.0)
    # La somme des 10 déciles doit reconstituer le total (pas de fuite Md€)
    par_decile = out["par_mesure"]["tva_rate"]["par_decile"]
    assert sum(par_decile.values()) == pytest.approx(10.0, abs=1e-3)
    assert out["total_md_eur_ventile"] == pytest.approx(10.0)
    assert out["mesures_non_ventilees"] == []


def test_decile_breakdown_signale_les_mesures_non_couvertes_sans_les_inventer():
    """Une mesure non listée dans DECILE_SHARES (ex. fraude_fiscale) ne doit
    JAMAIS recevoir de répartition inventée — elle doit apparaître dans
    `mesures_non_ventilees` et ne pas contaminer `total_par_decile`."""
    measure_impacts_by_year = [
        {"Année": 2026, "fraude_fiscale": {"depenses": -5.0}},
    ]
    out = decile_breakdown(measure_impacts_by_year)
    assert "fraude_fiscale" not in out["par_mesure"]
    assert "fraude_fiscale" in out["mesures_non_ventilees"]
    assert out["total_md_eur_ventile"] == 0.0
    assert all(v == 0.0 for v in out["total_par_decile"].values())


def test_decile_breakdown_agrege_plusieurs_mesures_sur_le_meme_decile():
    measure_impacts_by_year = [
        {"Année": 2026, "tva_rate": {"recettes": 10.0}, "csg": {"recettes": 5.0}},
    ]
    out = decile_breakdown(measure_impacts_by_year)
    assert set(out["par_mesure"]) == {"tva_rate", "csg"}
    attendu_total_d1 = (
        out["par_mesure"]["tva_rate"]["par_decile"]["D1"]
        + out["par_mesure"]["csg"]["par_decile"]["D1"]
    )
    assert out["total_par_decile"]["D1"] == pytest.approx(attendu_total_d1, abs=1e-3)


def test_decile_breakdown_gere_une_liste_vide_sans_erreur():
    out = decile_breakdown([])
    assert out["par_mesure"] == {}
    assert out["total_md_eur_ventile"] == 0.0
    assert all(v == 0.0 for v in out["total_par_decile"].values())
