"""Hash pins for the statistics helpers.

The sealed overlay and XSMOM results were produced by exactly these functions, and a
sibling repo vendors PSR/DSR/BH from ``src/xsmom_stats.py``. A silent edit to any of them
fails here. To change one on purpose, update its pin below AND the list in that module's
"Provenance" docstring in the same commit.

Normalised source = ``inspect.getsource(fn)`` with trailing whitespace stripped from each
line, joined with "\\n", UTF-8, SHA-256.
"""

from __future__ import annotations

import hashlib
import inspect
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import seasonality, validation, xsmom_stats

PINS: dict[tuple[object, str], str] = {
    # src/seasonality.py — BH at q = 0.10, HAC t-test, moving-block bootstrap
    (seasonality, "bh_fdr"): "dcf0ecce7ebf1cc4c9af7da5b4289530604fb15d5e1a861fc883543ac0304dd0",
    (seasonality, "hac_diff_test"): "b059702e1db1cbd9eaebefab88a39f1d5a6b1ce12231029d08afb6ce02abdc6d",
    (seasonality, "block_bootstrap_ci"): "9035bd2d4365fd0475778f79ca7e2b0726215af69583c0a7052eaf7f85005bd6",
    # src/xsmom_stats.py — BH at alpha = 0.05, PSR/DSR, decomposition + block bootstrap
    (xsmom_stats, "benjamini_hochberg"): "f771d541e068aa7d4110f40edd6d33ea733c8e7fc24904ad7434a76e533cc3dd",
    (xsmom_stats, "_per_period_sharpe_moments"): "897f14d8b131a84dd561451bd1bc7eae95ff96c63877c0c895e64c3b94abb40c",
    (xsmom_stats, "probabilistic_sharpe_ratio"): "f4d5667ad64a1886949e3aae09274eb9fdfb468046dc36d8669b6c39a8bd6d7d",
    (xsmom_stats, "expected_max_sharpe"): "70366e46becab8a6d1e62f7d6b4f5411e4c8aba41953d4068015abc211a43c43",
    (xsmom_stats, "deflated_sharpe_ratio"): "382a84b652a70f9223b9aa9977c7a870b866c7a9c7a69564329939dbb008f4be",
    (xsmom_stats, "sharpe_pvalue_vs0"): "3dfeddff745063807823329d7127fc2fb1c2f36b6b990cb2468ddacb23d53878",
    (xsmom_stats, "lo_mackinlay_decomposition"): "433678d2ccd67b36a931e4f6cdd0a2a14f83fa7ba22656b9c41795b58623e097",
    (xsmom_stats, "decomposition_block_bootstrap"): "dcc95d7d34d8206c315f633137053706afcb306007eda6cf095678744c373bf9",
    (xsmom_stats, "term2_contains_zero"): "2cd73fceefd306f4763e494efab97b54fa9a5083e552277ec3cc1ddc40ab72dc",
    (xsmom_stats, "term2_precision"): "53008fc41576b7a66551b673bb7b12fec91414ee7afcf2ed2af348bf6f36f172",
    # src/validation.py — iid percentile bootstrap behind the core headline CI
    (validation, "bootstrap_ci"): "df91388430ef1c20ed4a166112ae9697ce58b2bb68575b848ce5a1e34f26f9b6",
}


def normalised_sha256(fn) -> str:
    src = "\n".join(line.rstrip() for line in inspect.getsource(fn).splitlines())
    return hashlib.sha256(src.encode("utf-8")).hexdigest()


@pytest.mark.parametrize(("module", "name"), list(PINS), ids=lambda x: getattr(x, "__name__", x))
def test_stats_helper_source_is_pinned(module, name):
    assert normalised_sha256(getattr(module, name)) == PINS[(module, name)]


@pytest.mark.parametrize(("module", "name"), list(PINS), ids=lambda x: getattr(x, "__name__", x))
def test_module_provenance_header_lists_the_pin(module, name):
    assert PINS[(module, name)] in module.__doc__, f"{module.__name__}.{name} missing from header"


def test_bh_default_levels_are_the_documented_ones():
    assert inspect.signature(seasonality.bh_fdr).parameters["q"].default == 0.10
    assert inspect.signature(xsmom_stats.benjamini_hochberg).parameters["alpha"].default == 0.05
