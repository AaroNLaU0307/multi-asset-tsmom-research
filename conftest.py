"""Pytest configuration.

Exclude the XSMOM quarantine holding-pen from test collection. ``_quarantine_xsmom/``
contains separated cross-sectional-momentum (XSMOM) code that is not part of this
TSMOM repo (it is also git-ignored); its tests import modules that intentionally no
longer live under ``src/``, so collecting them would error. This keeps the documented
repo-root ``python -m pytest -q`` green.
"""

collect_ignore = ["_quarantine_xsmom"]
