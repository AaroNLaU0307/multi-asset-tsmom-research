# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - S2A acquisition of the primary SPECIFICATION-HISTORY documents.

Section L requires the quotation-basis / multiplier / tick history to be dated from
primary exchange sources, with each saved document hashed. This module fetches and
pins those documents. It reads no market data and computes nothing.

The documents:

  CFE-IC-2007-003.pdf   CFE Information Circular IC07-03, 7 March 2007, "Rescaling of
                        VIX and VXD Futures Contracts". THE primary source for the
                        2007 quotation / multiplier break: effective 26 March 2007,
                        price divided by 10, multiplier $100 -> $1,000, minimum tick
                        $0.10 -> 0.01 index point, dollar value per tick unchanged
                        at $10. This is the document section F.5 requires.

  datashop_vx_note.html Cboe DataShop product note restating the same break and
                        linking the circular; a second Cboe-official corroboration.

  Mini-VIX-Futures-Product-Launch.pdf
                        Cboe release note for the Mini VX (VXM) contract; the $100
                        multiplier used ONLY by the section D.4 granularity check.

The contract-specification, holiday-calendar, fee-schedule and historical-data index
pages are fetched by `vrp_acquire.py`.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import vrp_acquire as A  # noqa: E402

EXTRA_DOCUMENTS = [
    ("CFE-IC-2007-003.pdf",
     "https://cdn.cboe.com/resources/regulation/circulars/general/CFE-IC-2007-003.pdf",
     "CFE Information Circular IC07-03 (7 Mar 2007): rescaling of VIX futures effective "
     "26 Mar 2007; multiplier $100 -> $1,000; price divided by 10; minimum tick $0.10 -> "
     "0.01 index point; dollar value per tick unchanged. PRIMARY source for the section "
     "F.5 quotation/multiplier break."),
    ("datashop_vx_note.html",
     "https://datashop.cboe.com/cfe-vix-volatility-index-futures-trades-quotes",
     "Cboe DataShop VX product note: 'Prior to 3/23/2007, VIX had a $100x multiplier. On "
     "3/26/2007 we changed this multiplier to $1000x and divided the display price by 10.' "
     "Corroborates IC07-03."),
    ("Mini-VIX-Futures-Product-Launch.pdf",
     "https://cdn.cboe.com/resources/release_notes/2020/Mini-VIX-Futures-Product-Launch.pdf",
     "Cboe Mini VIX (VXM) futures product launch release note; $100 multiplier, used ONLY "
     "by the section D.4 integer-granularity check."),
    ("cboe_vxm_specifications.html",
     "https://www.cboe.com/tradable_products/vix/mini_vix_futures/",
     "Cboe Mini VIX futures product page (granularity check only)."),
]


def main() -> int:
    print("TSMOM-VRP-01 S2A - primary specification-history documents")
    print("=" * 78)
    rows = []
    for name, url, what in EXTRA_DOCUMENTS:
        data, status = A._fetch(url)
        if data is None:
            print("  %-42s UNAVAILABLE (http %s)" % (name, status))
            rows.append({"file_name": name, "url": url, "documents": what,
                         "status": "UNAVAILABLE", "http_status": status})
            continue
        row = A._store(name, data, url, directory=A.DOC_DIR)
        row["documents"] = what
        row["source"] = "Cboe / CFE primary rule, circular or product documentation"
        row["source_authority_level"] = "1 / PRIMARY"
        row["status"] = "ACQUIRED"
        rows.append(row)
        print("  %-42s %8d bytes  sha256 %s" % (name, len(data), row["sha256"][:16]))

    import json
    with open(A.MANIFEST_JSON, encoding="utf-8") as fh:
        manifest = json.load(fh)
    existing = {r["file_name"] for r in manifest.get("specification_documents", [])}
    manifest["specification_documents"] = (
        [r for r in manifest.get("specification_documents", []) if r["file_name"] in existing]
        + [r for r in rows if r["file_name"] not in existing])
    with open(A.MANIFEST_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    print("\nmanifest updated: %s" % A.MANIFEST_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
