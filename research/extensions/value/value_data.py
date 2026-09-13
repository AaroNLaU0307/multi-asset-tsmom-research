# -*- coding: utf-8 -*-
"""Value data layer: deterministic loading and the sealed real-FX algebra.

Every loader returns a monthly series indexed by a `YYYY-MM` *reference month*
string. Applying the causal cut-off is a separate, explicit step
(`admissible_at`), so the reference month and the month it may enter a signal
are never conflated — the distinction §3.2 of the sealed contract insists on.

Nothing in this module computes a return, a Sharpe, a correlation or a verdict.
"""
import io
import json
import os
import re
import zipfile

from value_contract import (FX_WEIGHTS, LAG_CAPE_MONTHS, LAG_CPI_MONTHS,
                            RAW_DIR, REPO, STALENESS_MONTHS)


# --------------------------------------------------------------------------- #
# month arithmetic on "YYYY-MM"
# --------------------------------------------------------------------------- #
def m_key(s):
    return int(s[:4]) * 12 + (int(s[5:7]) - 1)


def m_str(k):
    return "%04d-%02d" % (k // 12, k % 12 + 1)


def m_shift(s, n):
    return m_str(m_key(s) + n)


def m_range(a, b):
    return [m_str(k) for k in range(m_key(a), m_key(b) + 1)]


def _raw(name):
    return os.path.join(REPO, RAW_DIR, name)


# --------------------------------------------------------------------------- #
# loaders — each returns {reference_month: float}
# --------------------------------------------------------------------------- #
def load_fred_daily_to_monthly(filename):
    """Business-daily FRED CSV -> last observation within each calendar month.

    The 1-business-day market lag of §3.2 does not move a value across a month
    boundary except at a month's first business day, so month-end sampling with
    a same-month last observation is the faithful reading. `admissible_at`
    enforces the lag explicitly rather than leaving it implicit here.
    """
    out = {}
    text = io.open(_raw(filename), encoding="utf-8", errors="replace").read()
    for line in text.strip().split("\n")[1:]:
        if not line.strip():
            continue
        d, _, v = line.partition(",")
        v = v.strip()
        if v in (".", ""):
            continue
        out[d[:7]] = float(v)          # later dates overwrite -> month's last
    return out


def load_shiller_cape(filename="shiller_ie_data.xls"):
    """Shiller CAPE, column index 16 of sheet 'Data'. Reconstructed, not vintage."""
    import xlrd
    sh = xlrd.open_workbook(_raw(filename)).sheet_by_name("Data")
    out = {}
    for r in range(7, sh.nrows):
        v = sh.cell_value(r, 0)
        c = sh.cell_value(r, 16)
        if isinstance(v, float) and v > 1800 and isinstance(c, float) and c > 0:
            y = int(v)
            mo = int(round((v - y) * 100))
            if 1 <= mo <= 12:
                out["%04d-%02d" % (y, mo)] = float(c)
    return out


def load_cpi_us(filename="CPIAUCNS.csv"):
    return load_fred_daily_to_monthly(filename)


def load_cpi_eur(filename="euro_hicp_eurostat_ecoicop2_I25.json"):
    d = json.load(io.open(_raw(filename), encoding="utf-8"))
    idx = d["dimension"]["time"]["category"]["index"]
    vals = d["value"]
    return {p: float(vals[str(i)]) for p, i in idx.items() if str(i) in vals}


def load_cpi_gbp(filename="uk_cpi_ons_D7BT.json"):
    M = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
         "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
    d = json.load(io.open(_raw(filename), encoding="utf-8"))
    out = {}
    for m in d["months"]:
        out["%s-%02d" % (m["date"][:4], M[m["date"][-3:]])] = float(m["value"])
    return out


SEK_HISTORICAL = "sweden_cpi_scb_KPI2020M1980_000007T9.json"
SEK_CURRENT = "sweden_cpi_scb_KPI2020M_00000808.json"
SEK_JUNCTION_LAST_HISTORICAL = "2025-12"
SEK_JUNCTION_FIRST_CURRENT = "2026-01"


class SwedishCompositionError(ValueError):
    """The authorised two-table join failed. There is no fallback."""


def _scb_numeric(filename):
    d = json.load(io.open(_raw(filename), encoding="utf-8"))
    out = {}
    for row in d["data"]:
        k = row["key"][0]                       # e.g. 1980M01
        v = row["values"][0]
        if v not in ("..", ".", ""):
            out["%s-%s" % (k[:4], k[5:7])] = float(v)
    return out


def load_cpi_sek(historical=SEK_HISTORICAL, current=SEK_CURRENT):
    """VALUE_S1_DATA_IDENTITY_AMENDMENT_001 — the authorised two-table object.

        month <= 2025M12  ->  KPI2020M1980 / 000007T9
        month >= 2026M01  ->  KPI2020M     / 00000808

    STRICT CONCATENATION. Both legs are official SCB all-items Fixed CPI, NSA,
    on the same 2020=100 basis, so no rescaling, bridging or interpolation is
    performed or permitted. Every failure below is loud: there is no silent
    fallback and no Shadow-CPI fallback.
    """
    for f in (historical, current):
        if not os.path.isfile(_raw(f)):
            raise SwedishCompositionError("required SCB component missing: %s" % f)

    hist = _scb_numeric(historical)
    curr = _scb_numeric(current)
    if not hist or not curr:
        raise SwedishCompositionError("an SCB component carries no numeric value")

    if SEK_JUNCTION_LAST_HISTORICAL not in hist:
        raise SwedishCompositionError(
            "historical leg is missing the junction month %s"
            % SEK_JUNCTION_LAST_HISTORICAL)
    if SEK_JUNCTION_FIRST_CURRENT not in curr:
        raise SwedishCompositionError(
            "current leg is missing the junction month %s"
            % SEK_JUNCTION_FIRST_CURRENT)

    hist = {m: v for m, v in hist.items() if m <= SEK_JUNCTION_LAST_HISTORICAL}
    curr = {m: v for m, v in curr.items() if m >= SEK_JUNCTION_FIRST_CURRENT}

    overlap = sorted(set(hist) & set(curr))
    if overlap:
        raise SwedishCompositionError("legs overlap at %s" % overlap)
    if m_key(min(curr)) - m_key(max(hist)) != 1:
        raise SwedishCompositionError(
            "junction gap between %s and %s" % (max(hist), min(curr)))

    out = dict(hist)
    out.update(curr)
    months = sorted(out)
    for i in range(len(months) - 1):
        if m_key(months[i + 1]) - m_key(months[i]) != 1:
            raise SwedishCompositionError(
                "internal gap between %s and %s" % (months[i], months[i + 1]))
    return out


def load_cpi_chf(filename="swiss_cpi_snb.csv"):
    text = io.open(_raw(filename), encoding="utf-8-sig",
                   errors="replace").read()
    out = {}
    for mth, val in re.findall(r'^"(\d{4}-\d{2})";"LD2010100";"([\d.]+)"',
                               text, re.M):
        out[mth] = float(val)
    return out


def load_cpi_jpy(filename="japan_cpi_estat_000040482943.csv"):
    """All items = Group/Item code 0001, which is column index 1 of the file."""
    text = io.open(_raw(filename), encoding="cp932", errors="replace").read()
    out = {}
    for line in text.split("\n"):
        if not re.match(r"^\d{6},", line):
            continue
        cells = line.split(",")
        v = cells[1].strip()
        if v in ("", "-", "*"):
            continue
        out["%s-%s" % (cells[0][:4], cells[0][4:6])] = float(v)
    return out


def load_cpi_cad(filename="canada_cpi_statcan_18100004.zip"):
    """StatCan table 18-10-0004: all-items, Canada, monthly, NSA."""
    z = zipfile.ZipFile(_raw(filename))
    main = [n for n in z.namelist()
            if n.lower().endswith(".csv") and "MetaData" not in n][0]
    out = {}
    with z.open(main) as fh:
        # StatCan writes a UTF-8 BOM before the first header cell; without
        # stripping it the REF_DATE lookup fails and the loader silently
        # returns nothing.
        header = fh.readline().decode("utf-8-sig", "replace")
        cols = [c.strip().strip('"') for c in header.split(",")]
        try:
            i_ref = cols.index("REF_DATE")
            i_geo = cols.index("GEO")
            i_prod = cols.index("Products and product groups")
            i_uom = cols.index("UOM")
            i_val = cols.index("VALUE")
        except ValueError as exc:
            raise ValueError("StatCan 18-10-0004 header changed: %s" % exc)
        need = max(i_ref, i_geo, i_prod, i_uom, i_val)
        for raw in fh:
            cells = _split_csv(raw.decode("utf-8", "replace"))
            if len(cells) <= need:
                continue
            # The table carries several "All-items" variants on different bases;
            # the sealed object is the 2002=100 all-items index for Canada.
            if (cells[i_geo] != "Canada" or cells[i_prod] != "All-items"
                    or cells[i_uom] != "2002=100"):
                continue
            v = cells[i_val].strip()
            if v in ("", ".."):
                continue
            out[cells[i_ref][:7]] = float(v)
    if not out:
        raise ValueError("StatCan loader matched no rows — refusing to return "
                         "an empty CPI series silently")
    return out


def _split_csv(line):
    """Minimal quoted-CSV split; StatCan quotes fields containing commas."""
    out, cur, q = [], [], False
    for ch in line.rstrip("\r\n"):
        if ch == '"':
            q = not q
        elif ch == "," and not q:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return [c.strip() for c in out]


CPI_LOADERS = {"US": load_cpi_us, "EUR": load_cpi_eur, "JPY": load_cpi_jpy,
               "GBP": load_cpi_gbp, "CAD": load_cpi_cad, "SEK": load_cpi_sek,
               "CHF": load_cpi_chf}
FX_FILES = {"EUR": "DEXUSEU.csv", "JPY": "DEXJPUS.csv", "GBP": "DEXUSUK.csv",
            "CAD": "DEXCAUS.csv", "SEK": "DEXSDUS.csv", "CHF": "DEXSZUS.csv"}
FX_INVERT = {"EUR": True, "GBP": True,
             "JPY": False, "CAD": False, "SEK": False, "CHF": False}


# --------------------------------------------------------------------------- #
# causal availability
# --------------------------------------------------------------------------- #
def admissible_at(series, t, lag_months):
    """The most recent value whose declared lag has elapsed as of month-end t.

    Returns (reference_month, value) or (None, None). Never looks forward.
    """
    latest_allowed = m_key(t) - lag_months
    best = None
    for ref in series:
        k = m_key(ref)
        if k <= latest_allowed and (best is None or k > best):
            best = k
    if best is None:
        return None, None
    return m_str(best), series[m_str(best)]


def is_stale(ref_month, t, lag_months, staleness=STALENESS_MONTHS):
    """Stale iff the admissible value is older than the lag plus the tolerance."""
    if ref_month is None:
        return True
    return (m_key(t) - m_key(ref_month)) > (lag_months + staleness)


# --------------------------------------------------------------------------- #
# the sealed real-FX algebra  (§2.2.1)
# --------------------------------------------------------------------------- #
def s_foreign_per_usd(quote, inverted):
    """S_f = foreign units per USD. DEXUSEU / DEXUSUK are quoted the other way."""
    if quote is None or quote <= 0:
        return None
    return (1.0 / quote) if inverted else quote


def r_bilateral(s_f, p_us, p_f):
    """r_f(t) = log S_f(t) + log P_US(t-2) - log P_f(t-2)."""
    import math
    if not s_f or not p_us or not p_f or s_f <= 0 or p_us <= 0 or p_f <= 0:
        return None
    return math.log(s_f) + math.log(p_us) - math.log(p_f)


def r_basket(legs, weights=None):
    """r_basket(t) = sum_f w_f * r_f(t). Weighted mean of logs = weighted
    geometric mean of the levels. Returns None if any weighted leg is missing —
    a partial basket is not the sealed object."""
    w = weights or FX_WEIGHTS
    total = 0.0
    for cur, weight in w.items():
        v = legs.get(cur)
        if v is None:
            return None
        total += weight * v
    return total


def x_uup(basket):
    return None if basket is None else -basket


def x_fxy(r_jpy):
    return None if r_jpy is None else +r_jpy


# --------------------------------------------------------------------------- #
# object construction (inputs only — no returns, no performance)
# --------------------------------------------------------------------------- #
def build_fx_objects(fx_monthly, cpi_monthly, months):
    """UUP and FXY object series over `months`, using the §3.2 cut-offs."""
    uup, fxy, prov = {}, {}, {}
    for t in months:
        legs, ok = {}, True
        for cur in FX_WEIGHTS:
            q_ref, q = admissible_at(fx_monthly[cur], t, 0)
            p_us_ref, p_us = admissible_at(cpi_monthly["US"], t, LAG_CPI_MONTHS)
            p_f_ref, p_f = admissible_at(cpi_monthly[cur], t, LAG_CPI_MONTHS)
            stale = (is_stale(q_ref, t, 0) or is_stale(p_us_ref, t, LAG_CPI_MONTHS)
                     or is_stale(p_f_ref, t, LAG_CPI_MONTHS))
            r = None if stale else r_bilateral(
                s_foreign_per_usd(q, FX_INVERT[cur]), p_us, p_f)
            legs[cur] = r
            if r is None:
                ok = False
        b = r_basket(legs) if ok else None
        uup[t] = x_uup(b)
        fxy[t] = x_fxy(legs.get("JPY"))
        prov[t] = {k: (v is not None) for k, v in legs.items()}
    return uup, fxy, prov


def build_objects(months, sources=None):
    """All five sealed objects over `months`. Values may be None (stale/missing).

    `sources` lets a test inject synthetic inputs; production passes None and the
    pinned raw files are read.
    """
    s = sources or {}
    cape = s.get("cape") or load_shiller_cape()
    tlt = s.get("tlt") or load_fred_daily_to_monthly("DFII20.csv")
    credit = s.get("credit") or load_fred_daily_to_monthly("BAA10Y.csv")
    fx = s.get("fx") or {c: load_fred_daily_to_monthly(f)
                         for c, f in FX_FILES.items()}
    cpi = s.get("cpi") or {c: fn() for c, fn in CPI_LOADERS.items()}

    uup, fxy, _prov = build_fx_objects(fx, cpi, months)
    out = {"SPY": {}, "TLT": {}, "LQD": {}, "UUP": uup, "FXY": fxy}
    for t in months:
        c_ref, c = admissible_at(cape, t, LAG_CAPE_MONTHS)
        out["SPY"][t] = (None if is_stale(c_ref, t, LAG_CAPE_MONTHS) or not c
                         else 1.0 / c)          # real earnings yield
        t_ref, tv = admissible_at(tlt, t, 0)
        out["TLT"][t] = None if is_stale(t_ref, t, 0) else tv
        d_ref, dv = admissible_at(credit, t, 0)
        out["LQD"][t] = None if is_stale(d_ref, t, 0) else dv
    return out
