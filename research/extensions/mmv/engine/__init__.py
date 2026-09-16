"""CTA-EDGE-04-MMV — sealed-contract implementation (S2 BUILD).

Implements, and only implements, the design sealed at S1:

    contract  research/extensions/mmv/MMV_PREREGISTRATION.md
              sha256 4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225
    seal      research/extensions/mmv/MMV_SEAL_MANIFEST.md
              sha256 75016e778ad58e8fe16e4833cf91c19eb52448b4d42138ab265460f371e8c0d5
    commit    cdb01fdc903e97671c3ef50fde6875628ca39ac8

This package makes NO scientific choice. Every constant here traces to a sealed
clause, and every clause it cannot answer is an Owner decision, not a builder
decision.

S2 authorizes implementation and SYNTHETIC validation only. Nothing in this
package may be executed against the real 218 canonical decision dates to build
the candidate feature, its positions, its first-release concordance or its
Gate 0.5 result. Those are S3 objects and require an explicit Owner
authorization that does not exist.

Modules
-------
pit          latest-known-as-of vintage resolver for the ALFRED legs
policy       administered-policy resolver on ANNOUNCEMENT authority
legs         the three primitive macro legs (growth, inflation, policy)
votes        the frozen 15-instrument coefficient table and raw direction
gate05       the PnL-free position-level separability screen
concordance  the first-release descriptive diagnostic (no threshold, no verdict)
risk         integration with the canonical portfolio risk wrapper
start        the structural start rule
"""

from __future__ import annotations

SEAL_ID = "CTA-EDGE-04-MMV-SEAL-01"
SEAL_SHA256 = "75016e778ad58e8fe16e4833cf91c19eb52448b4d42138ab265460f371e8c0d5"
PREREG_SHA256 = "4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225"
SEALED_COMMIT = "cdb01fdc903e97671c3ef50fde6875628ca39ac8"

#: Contract section C: the information cutoff, 15:45:00 America/New_York.
CUTOFF_HOUR, CUTOFF_MINUTE = 15, 45

__all__ = ["SEAL_ID", "SEAL_SHA256", "PREREG_SHA256", "SEALED_COMMIT",
           "CUTOFF_HOUR", "CUTOFF_MINUTE"]
