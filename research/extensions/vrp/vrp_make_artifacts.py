# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - generate the tracked S2 provenance artifacts.

Writes, from the acquisition manifest and the specification registry:

    VRP_DATA_MANIFEST.md            the section L provenance manifest (tracked; the raw
                                    bytes themselves stay git-ignored under data/vix/)
    VRP_SPECIFICATION_REGISTRY.md   the dated quotation/multiplier/tick/expiry break table
    VRP_NORMALIZED_SCHEMA.md        the normalized-layer schema and its derivation rules

No price, return, basis, carry or outcome appears in any of them.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import vrp_calendar as vcal      # noqa: E402
import vrp_specs as vspecs       # noqa: E402

MANIFEST_JSON = os.path.join(REPO, "data", "vix", "manifests", "vrp_raw_manifest.json")
S2A_RESULT = os.path.join(REPO, "data", "vix", "manifests", "vrp_s2a_result.json")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("  wrote %-44s %d bytes" % (os.path.basename(path), len(text.encode("utf-8"))))


def data_manifest(manifest, counts):
    rows = sorted(manifest["contract_files"], key=lambda r: (r["contract_month"], r["endpoint"]))
    docs = [d for d in manifest["specification_documents"] if d.get("status") == "ACQUIRED"]
    unavailable = manifest["unavailable_contracts"]

    out = []
    a = out.append
    a("# TSMOM-VRP-01 — DATA MANIFEST (S2A acquisition and hash pinning)\n")
    a("```")
    a("LINEAGE                    = TSMOM-VRP-01")
    a("CONTRACT                   = VRP_PREREGISTRATION.md §L (data acquisition contract)")
    a("S1_SEAL_COMMIT             = 16d84545ba1385a482dbac7e776b31275f6fa5f7")
    a("ACQUIRED_UTC               = %s" % manifest["generated_utc"])
    a("RAW_DATA_COMMITTED         = NO  (data/ is git-ignored; this manifest and the hashes are tracked)")
    a("LICENSE_STATUS             = Cboe personal / research use; NO REDISTRIBUTION;")
    a("                             raw bytes retained in the git-ignored data/vix/ tree")
    a("TRANSFORMATION_STATUS      = RAW for every file below; the normalized layer is derived")
    a("                             and re-derivable from these bytes alone")
    a("CREDENTIALS                = NONE. Both endpoints are public and unauthenticated; no")
    a("                             key, token or secret was used, sent, stored, logged or hashed.")
    a("```\n")

    a("## 1. Sources and authority\n")
    a("Both endpoints are **Cboe official** (`SOURCE_AUTHORITY_LEVEL = 1 / PRIMARY`). No vendor")
    a("copy is used anywhere in this lineage, so §L's fallback-authority clause is never")
    a("exercised. The settlement field taken is the official **`Settle`** column — never")
    a("`Close`, never last trade, never the Special Opening Quotation.\n")
    a("| # | Endpoint | Pattern | Covers |")
    a("|---|---|---|---|")
    a("| 1 | Cboe delisted-contract archive | `https://cdn.cboe.com/resources/futures/archive/"
      "volume-and-price/CFE_<code><yy>_VX.csv` | the older monthly contracts, whole contract life |")
    a("| 2 | Cboe market-statistics historical data | `https://cdn.cboe.com/data/us/futures/"
      "market_statistics/historical_data/VX/VX_<final_settlement_date>.csv` | the newer monthly contracts |")
    a("")
    a("**Operative-source rule (mechanical; uses no return and cannot change an estimand).**")
    a("Where both endpoints serve one contract, the operative file is the one with the greater")
    a("number of rows carrying an official settlement; ties break by greater row count, then by")
    a("ARCHIVE. Both files are pinned either way and their comparable settlements are")
    a("cross-checked on every common date.\n")

    a("## 2. Coverage summary (mechanical counts only)\n")
    a("```")
    for key in ("CONTRACT_COUNT", "FIRST_AVAILABLE_DATE", "LAST_AVAILABLE_DATE",
                "EXCHANGE_SESSIONS", "CHAIN_DAYS", "NUMBER_OF_ROWS",
                "NUMBER_OF_SETTLED_ROWS", "NUMBER_OF_DUPLICATES",
                "STAGE_A_FIRST_MONTH", "STAGE_A_LAST_MONTH", "STAGE_A_MONTHS",
                "MONTHLY_CONTRACT_COUNT_IN_WINDOW",
                "NUMBER_OF_MISSING_SETTLEMENTS_IN_WINDOW",
                "NUMBER_OF_CONTRACTS_WITH_GAPS_IN_WINDOW",
                "SPECIFICATION_BREAK_COUNT", "TICK_HISTORY_BREAK_COUNT",
                "EXPIRY_RULE_BREAK_COUNT", "EXPIRY_RULE_MATCH_COUNT",
                "CALENDAR_MISMATCH_COUNT", "CALENDAR_DECLARED_CFE_ONLY_SESSIONS"):
        if key in counts:
            a("%-42s = %s" % (key, counts[key]))
    a("RAW_CONTRACT_FILES_PINNED                  = %d" % len(rows))
    a("SPECIFICATION_DOCUMENTS_PINNED             = %d" % len(docs))
    a("TOTAL_RAW_BYTES                            = %d" % sum(int(r["bytes"]) for r in rows))
    a("```\n")

    a("### Calendar months with no listed standard monthly VX contract\n")
    a("Established mechanically at acquisition: neither Cboe endpoint serves a file for these")
    a("months while serving one for every neighbouring month. These are **listing-history**")
    a("facts, not data gaps — §F.3 orders contracts by final-settlement date and never assumes")
    a("consecutive calendar months.\n")
    a("```")
    a(", ".join(vspecs.NEVER_LISTED_MONTHS))
    a("```\n")
    a("The remaining entries below (2004-01 … 2004-04) precede the VX listing date")
    a("(2004-03-26) and no contract for them ever existed.\n")
    a("| contract month | rule-derived expiry | archive HTTP | current HTTP |")
    a("|---|---|---|---|")
    for r in unavailable:
        a("| %s | %s | %s | %s |" % (r["contract_month"], r["rule_expiry"],
                                     r["archive_status"], r["current_status"]))
    a("")

    a("## 3. Specification / calendar / fee documents — pinned\n")
    a("| file | SHA256 | bytes | source URL | documents |")
    a("|---|---|---|---|---|")
    for d in docs:
        a("| `%s` | `%s` | %d | %s | %s |" % (d["file_name"], d["sha256"], d["bytes"],
                                              d["url"], d.get("documents", "")))
    a("")

    a("## 4. Raw contract files — pinned\n")
    a("Every row: FILE NAME · RAW SHA256 · BYTE SIZE · ACQUISITION_TIMESTAMP_UTC · ENDPOINT ·")
    a("CONTRACT MONTH · rule-derived final settlement. `TRANSFORMATION_STATUS = RAW` throughout;")
    a("raw bytes are never edited in place and a re-fetch that differs from the pinned hash")
    a("fails the acquisition loudly.\n")
    a("| contract month | expiry | endpoint | file | SHA256 | bytes | acquired (UTC) |")
    a("|---|---|---|---|---|---|---|")
    for r in rows:
        a("| %s | %s | %s | `%s` | `%s` | %d | %s |" % (
            r["contract_month"], r["rule_expiry"], r["endpoint"], r["file_name"],
            r["sha256"], r["bytes"], r["acquisition_timestamp_utc"]))
    a("")
    a("*Recompute every hash before use. Chat-carried bytes are never a source of truth.*")
    return "\n".join(out) + "\n"


def specification_registry():
    out = []
    a = out.append
    a("# TSMOM-VRP-01 — SPECIFICATION REGISTRY (dated break table)\n")
    a("```")
    a("LINEAGE   = TSMOM-VRP-01")
    a("GOVERNS   = VRP_PREREGISTRATION.md §F.5 (specification breaks) and §G (tick history)")
    a("RULE      = specification changes are EXPLICIT METADATA. They are never inferred from a")
    a("            price jump. Every span is sourced to a saved, hashed primary Cboe document.")
    a("BASIS     = everything is converted to the common $1,000-per-point economic basis:")
    a("            price_comparable = price_quoted * M_quoted / 1000")
    a("            tick_comparable  = tick_quoted  * M_quoted / 1000")
    a("```\n")

    a("## 1. Quotation basis, multiplier and tick\n")
    a("| span start | span end | M_quoted ($/quoted pt) | tick_quoted | conversion factor | "
      "tick_comparable | tick documented | primary source |")
    a("|---|---|---|---|---|---|---|---|")
    for row in vspecs.registry_rows():
        a("| %s | %s | %.0f | %.2f | %.3f | %.2f | %s | `%s` |" % (
            row["start"], row["end"], row["m_quoted_usd_per_quoted_point"],
            row["tick_quoted_points"], row["conversion_factor_to_common_basis"],
            row["tick_comparable_points"], "YES" if row["tick_documented"] else "NO (see §3)",
            row["source_document"]))
    a("")
    a("### The 2007 rescaling — CFE Information Circular IC07-03\n")
    a("Saved and hashed as `CFE-IC-2007-003.pdf`. Dated 7 March 2007, it states:\n")
    a("> The rescaling will be effective March 26, 2007 and will apply to all VIX and VXD")
    a("> futures contracts. … CFE will divide the VIX and VXD futures contracts by 10 … Second,")
    a("> CFE will increase the current multiplier for the VIX and VXD futures contracts from")
    a("> \\$100 to \\$1,000. As a result, the traded futures price will be reduced by a factor of")
    a("> ten and the minimum tick will be reduced from \\$0.10 to 0.01 index point, but the")
    a("> dollar value of both will remain the same.\n")
    a("and tabulates the two practices side by side:\n")
    a("| | futures price | contract multiplier | contract value | minimum tick | value per tick |")
    a("|---|---|---|---|---|---|")
    a("| Current practice (pre-2007-03-26) | 103.90 | $100 | $10,390 | $0.10 | $10 |")
    a("| Rescaled practice (from 2007-03-26) | 10.39 | $1,000 | $10,390 | 0.01 index point | $10 |")
    a("")
    a("The §F.5 conversion reproduces exactly this economic continuity: the comparable price is")
    a("unchanged across the break and the comparable tick is worth $10 on both sides.")
    a("`test_i07_*` assert both, and `test_i07_stress_loss_is_invariant_to_the_quotation_basis`")
    a("asserts that the §D.1 stress loss does not depend on the quotation basis.\n")

    a("## 2. Expiry-rule registry\n")
    a("VX has had two published monthly final-settlement rules. The registry reproduces the")
    a("observed final settlement of **every one of the 264 expired acquired contracts** with")
    a("**zero mismatches** (`test_i03_expiry_rule_reproduces_every_observed_final_settlement`).\n")
    a("| contract months | rule | holiday adjustment |")
    a("|---|---|---|")
    a("| VX listing (2004-03) … 2004-10 | the Wednesday immediately prior to the third Friday of "
      "the **expiring** month | if that Wednesday, or the Friday it is measured against, is a "
      "Cboe Options holiday → the business day immediately preceding that Wednesday |")
    a("| 2004-11 … present | the Wednesday **thirty days** prior to the third Friday of the "
      "**following** calendar month (the rule transcribed in §F.2 and §L) | as above |")
    a("")
    a("**Where the boundary is, and how far the data pins it.** The two rules give the same date")
    a("in most months, so the observed history cannot date the change to the month; it brackets")
    a("it exactly. The last contract whose observed final settlement follows the ORIGINAL rule")
    a("and not the current one is **2004-07** (observed 2004-07-14, current rule 2004-07-21) and")
    a("**2004-10** (observed 2004-10-13, current rule 2004-10-20). The first contract whose")
    a("observed final settlement follows the CURRENT rule and not the original one is **2005-12**")
    a("(observed 2005-12-21, original rule 2005-12-14). For every contract month in between the")
    a("two rules agree, so the choice of boundary inside (2004-10, 2005-12] changes **no date**")
    a("this lineage uses. 2004-11 is taken as the boundary.\n")
    a("This is outside the frozen Stage-A window in any case: §F.6 puts the first eligible")
    a("complete month at **2006-09**.\n")

    a("## 3. The one undocumented span, and the sealed rule that closes it\n")
    a("The exact date on which the **outright** minimum increment moved from 0.01 to 0.05 index")
    a("points is not established by any primary Cboe document this session could obtain and read.")
    a("(CFE-2009-01, whose title suggested it, is in fact a Threshold-Width amendment and says")
    a("nothing about the tick; it is deliberately **not** cited.)\n")
    a("§G fixes what to do:\n")
    a("> If the contemporaneous tick is undocumented for a span, the **largest tick documented")
    a("> for the contract on the comparable basis** is used for that span (conservative; declared).\n")
    a("So the whole post-rescaling span carries `tick_comparable = 0.05`, the largest documented")
    a("comparable tick. **This is economically inert and provably so**: §G charges")
    a("`cost_points = max(0.10, tick_comparable)`, and every tick documented for this contract on")
    a("the comparable basis lies in [0.01, 0.05] — all below `c0 = 0.10`. So `cost_points = 0.10`")
    a("throughout the window regardless of which value is assumed.")
    a("`test_i08_cost_invariant_to_tick_assumption` asserts exactly that, and")
    a("`test_i08_cost_points_never_below_the_contemporaneous_tick` asserts")
    a("`cost_points >= tick_comparable` on every date in the window.\n")
    a("**Consequence for the acceptance contract:** item 8's requirement — \"undocumented span →")
    a("the largest documented tick is applied and disclosed\" — is satisfied here, by this")
    a("disclosure and that test. The undocumented span cannot move any cost, any Stage-A return")
    a("or any estimand.\n")

    a("## 4. Exchange calendar\n")
    a("The **operative** CFE business-day calendar is the union of official settlement dates")
    a("across every acquired monthly contract — §L's own construction for this calendar, and the")
    a("only definition under which \"a missing official settlement on an exchange business day\"")
    a("(§F.4) is well posed. It is cross-checked against the rule-derived US equity / Cboe")
    a("Options holiday calendar over the whole acquired range.\n")
    a("Result: **zero unexplained differences**. Three dates are declared exceptions on which the")
    a("US equity market was closed but CFE held a session and published official VX settlements:\n")
    a("| date | why |")
    a("|---|---|")
    a("| 2015-04-03 | Good Friday; CFE held a session (the US employment report fell that day) |")
    a("| 2018-12-05 | national day of mourning for President G. H. W. Bush; NYSE and Cboe Options "
      "closed, CFE traded |")
    a("| 2025-01-09 | national day of mourning for President Carter; same pattern |")
    a("")
    a("`vrp_calendar.CFE_OPEN_WHEN_EQUITIES_CLOSED` declares them, and")
    a("`check_calendar_consistency` FAILS on any mismatch not listed there.\n")
    a("There are **no** rule business days without any VX settlement anywhere in the record.\n")
    a("*Any receiver recomputes the document hashes in `VRP_DATA_MANIFEST.md` before use.*")
    return "\n".join(out) + "\n"


def normalized_schema():
    out = []
    a = out.append
    a("# TSMOM-VRP-01 — NORMALIZED DATA SCHEMA\n")
    a("```")
    a("LINEAGE = TSMOM-VRP-01")
    a("LAYERS  = RAW (immutable, git-ignored, hash-pinned)")
    a("          -> NORMALIZED (derived in memory by vrp_raw/vrp_chain; re-derivable from the")
    a("             raw bytes alone, so it is never a separate source of truth)")
    a("RULE    = every normalized value points back to an exact raw SHA256 input via")
    a("          VRP_DATA_MANIFEST.md; nothing is normalised from an unpinned byte")
    a("```\n")
    a("## 1. Raw row (as published by Cboe)\n")
    a("| column | use |")
    a("|---|---|")
    a("| `Trade Date` | parsed as `YYYY-MM-DD` (current endpoint) or `M/D/YYYY` (archive) |")
    a("| `Futures` | the contract label, e.g. `F (Jan 2024)`; used as a POSITIVE identity check "
      "that the file served for a monthly expiry really is that monthly contract |")
    a("| `Settle` | **the official settlement — the only price field this lineage reads** |")
    a("| `Total Volume`, `Open Interest` | carried for diagnostics only; never a price |")
    a("| `Open`, `High`, `Low`, `Close` | **never read.** §A5 forbids last trade as a price; "
      "`check_no_last_trade_price` asserts the loader does not read them |")
    a("")
    a("## 2. Normalized contract record\n")
    a("| field | derivation |")
    a("|---|---|")
    a("| `root` | `\"VX\"` (standard monthly only; no weekly, no mini for pricing) |")
    a("| `final_settlement_date` | the contract's own last settled row once expired (§L PRIMARY); "
      "for a still-listed contract, the rule-derived date (there is no final-settlement row yet) |")
    a("| identity key | `(root, final_settlement_date)` — §J.3; never the symbol string alone |")
    a("| `contract_month` | `YYYY-MM` delivery month |")
    a("| `settle_present` | `Settle` parses to a strictly positive number. A zero/blank `Settle` "
      "is **no official settlement** (Cboe publishes all-zero placeholder rows for listed-but-"
      "unsettled days) and triggers §F.4, not a price |")
    a("| `price_comparable` | `settle_quoted * M_quoted / 1000`, with `M_quoted` from the dated "
      "specification registry — never inferred from the prices themselves |")
    a("")
    a("## 3. Chain day (the constant-maturity layer)\n")
    a("| field | derivation |")
    a("|---|---|")
    a("| `front_key` / `second_key` | the first and second eligible monthly contracts: `E_k` is "
      "the earliest monthly final settlement `> d`; front is `F_k`, second is `F_(k+1)` |")
    a("| `w_front` / `w_second` | `dr(d)/dt` and `1 - w_front` over `P_k = { business days d : "
      "E_(k-1) <= d < E_k }`; a pure function of the calendar |")
    a("| `front_price` / `second_price` | comparable settlements, with §F.4 carry-forward applied |")
    a("| `front_carried` / `second_carried` | TRUE when the day's value is a carried-forward prior "
      "official settlement; counted per contract per calendar month against the max of 2 |")
    a("")
    a("## 4. Month status (§F.4 / §F.6)\n")
    a("A calendar month is VALID iff no held contract exceeds **2** carry-forward business days in")
    a("it and no held contract lacks a settlement entirely. §F.6's first eligible complete month is")
    a("the start of the maximal terminal run of valid months ending at the Stage-A last month —")
    a("determined from availability under this rule alone, never from outcomes.\n")
    a("Result on the acquired chain: **first eligible complete month = 2006-09**, and every month")
    a("from 2006-09 through 2026-08 is valid with **zero** carry-forward days.\n")
    a("## 5. What the normalized layer never contains\n")
    a("No return, no cumulative return, no basis, no carry, no roll yield, no average price, no")
    a("strategy quantity and no outcome of any kind. Stage A (`vrp_stage_a`) is the only module")
    a("that forms a return, and during S2 it refuses to run on real data.\n")
    return "\n".join(out) + "\n"


def main() -> int:
    with open(MANIFEST_JSON, encoding="utf-8") as fh:
        manifest = json.load(fh)
    counts = {}
    if os.path.isfile(S2A_RESULT):
        with open(S2A_RESULT, encoding="utf-8") as fh:
            counts = json.load(fh).get("counts", {})
    print("TSMOM-VRP-01 - generating tracked S2 artifacts")
    write(os.path.join(HERE, "VRP_DATA_MANIFEST.md"), data_manifest(manifest, counts))
    write(os.path.join(HERE, "VRP_SPECIFICATION_REGISTRY.md"), specification_registry())
    write(os.path.join(HERE, "VRP_NORMALIZED_SCHEMA.md"), normalized_schema())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
