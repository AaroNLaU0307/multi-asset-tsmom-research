"""CTA-EDGE-04-MMV — S1 raw macro data freeze.

Acquires and pins EXACTLY the six sealed inputs of MMV-OD-2 plus the vintage calendars
needed for the MMV-OD-1 latest-known-as-of rule. It computes NO macro feature, NO
composite, NO position and NO return.

    python research/extensions/mmv/mmv_data_freeze.py

CREDENTIAL HANDLING. The key is read from the process environment, or — when that value
is stale or malformed — from the Windows User-scope persisted variable via the registry,
so it never passes through a shell, a command line, an argument list or a log. It is
never printed, never written to any file, and is redacted from every error path. The
manifest stores request parameters with `api_key` replaced by `<REDACTED>`.

WHAT IS FETCHED, per series:
  series           the authoritative metadata (title, units, frequency, seasonal adj.)
  observations     output_type=1 over the FULL real-time range. This is ALFRED's compact
                   revision history: one row per (reference date, value-interval), each
                   carrying realtime_start / realtime_end. The vintage as known on date
                   t is exactly the rows with realtime_start <= t <= realtime_end, which
                   is what MMV-OD-1 requires and what makes the rule provable.
  vintagedates     every date on which the series was revised or extended - the release
                   calendar the same-day 15:45 ET cutoff rule is applied against.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)

OUT_DIR = os.path.join("data", "mmv")
MANIFEST = os.path.join(OUT_DIR, "MMV_RAW_MANIFEST.json")

#: The six sealed inputs. NOTHING else may be added here — MMV-OD-2 forbids
#: CPIAUCSL, CPILFESL, PCEPILFE, FEDFUNDS, DGS2 and any traded yield.
SERIES = ("INDPRO", "PAYEMS", "CPILFENS", "DFEDTAR", "DFEDTARL", "DFEDTARU")

#: Series whose vintage history is load-bearing for MMV-OD-1. The policy target is
#: administered and never revised, so its vintage calendar is fetched for proof, not
#: because the signal needs it.
FULL_REALTIME_START = "1776-07-04"      # FRED's documented earliest real-time date
FULL_REALTIME_END = "9999-12-31"        # FRED's documented latest real-time date

API = "https://api.stlouisfed.org/fred/"


def _credential() -> tuple[str, str]:
    """Return (key, source). Never logs or returns the value anywhere else."""
    def ok(v: str) -> bool:
        return len(v) == 32 and v.isalnum() and v == v.lower()

    env = os.environ.get("FRED_API_KEY", "")
    if ok(env):
        return env, "process environment"
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                reg, _ = winreg.QueryValueEx(k, "FRED_API_KEY")
            if ok(reg):
                return reg, ("Windows User-scope persisted variable (the process "
                             "environment carried a stale value)")
        except OSError:
            pass
    raise SystemExit("FRED credential absent or malformed; refusing to continue. "
                     "No revised-FRED substitution is permitted.")


KEY, KEY_SOURCE = _credential()


def _redact(s: str) -> str:
    return s.replace(KEY, "<REDACTED>")


class VintageLimit(RuntimeError):
    """FRED refuses output_type=1 when a real-time window spans > 2000 vintages."""


def _get(path: str, **params):
    """One API call. Returns parsed JSON and the raw bytes actually received."""
    p = dict(params)
    p["api_key"] = KEY
    p["file_type"] = "json"
    url = API + path + "?" + urllib.parse.urlencode(p)
    req = urllib.request.Request(url, headers={"User-Agent": "mmv-s1-datafreeze/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
            return json.loads(raw.decode("utf-8")), raw
        except urllib.error.HTTPError as e:
            body = _redact(e.read().decode("utf-8", "replace")[:300])
            if "maximum number of vintage dates" in body:
                raise VintageLimit(body)
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise SystemExit(f"FRED {path} failed: HTTP {e.code} {body}")
        except Exception as e:                                   # noqa: BLE001
            if isinstance(e, VintageLimit):
                raise
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise SystemExit(f"FRED {path} failed: {_redact(type(e).__name__ + ': ' + str(e))}")


def _redacted_params(**params) -> dict:
    p = dict(params)
    p["api_key"] = "<REDACTED>"
    p["file_type"] = "json"
    return p


def _sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _write(name: str, payload) -> tuple[str, str, int]:
    path = os.path.join(OUT_DIR, name)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with open(path, "wb") as fh:
        fh.write(blob)
    return path, hashlib.sha256(blob).hexdigest(), len(blob)


def _observations_window(sid: str, rt_start: str, rt_end: str) -> list:
    rows, offset = [], 0
    while True:
        doc, _ = _get("series/observations", series_id=sid,
                      realtime_start=rt_start, realtime_end=rt_end,
                      output_type=1, limit=100000, offset=offset)
        got = doc.get("observations", [])
        rows.extend(got)
        total = int(doc.get("count", len(rows)))
        offset += len(got)
        if not got or offset >= total:
            break
    return rows


def fetch_observations(sid: str, vintages: list) -> tuple[list, str]:
    """Full ALFRED revision history in compact real-time-interval form.

    Tries the whole real-time range first. FRED caps output_type=1 at 2000 vintage
    dates per window. The DAILY policy-target series exceed that cap because every
    business day EXTENDS them with a new observation - NOT because past values are
    revised. When the cap is hit, the series' OWN vintage list is sliced into groups
    of at most 1500 and one window is requested per group, so the number of requests
    is a handful rather than a sweep over calendar time. Content is identical; only
    the request shape differs, and the manifest records which path was taken.
    """
    try:
        return _observations_window(sid, FULL_REALTIME_START, FULL_REALTIME_END), "single"
    except VintageLimit:
        pass
    if not vintages:
        raise SystemExit(f"{sid}: vintage-limit fallback needs a vintage list")
    rows, seen, windows = [], set(), 0
    CHUNK = 1500
    for i in range(0, len(vintages), CHUNK):
        grp = vintages[i:i + CHUNK]
        got = _observations_window(sid, grp[0], grp[-1])
        windows += 1
        for o in got:
            k = (o["date"], o["realtime_start"], o["realtime_end"], o["value"])
            if k not in seen:
                seen.add(k)
                rows.append(o)
    rows.sort(key=lambda o: (o["date"], o["realtime_start"]))
    return rows, f"chunked_by_vintage_list:{windows}_windows"


def fetch_vintage_dates(sid: str) -> list:
    dates, offset = [], 0
    while True:
        doc, _ = _get("series/vintagedates", series_id=sid, limit=10000, offset=offset)
        got = doc.get("vintage_dates", [])
        dates.extend(got)
        total = int(doc.get("count", len(dates)))
        offset += len(got)
        if not got or offset >= total:
            break
    return dates


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    started = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print("CTA-EDGE-04-MMV — S1 RAW MACRO DATA FREEZE")
    print(f"  credential source: {KEY_SOURCE}")
    print(f"  started {started}")
    print("  NO macro feature, composite, position or return is computed here.\n")

    manifest = {
        "schema": {"name": "mmv-raw-macro-manifest", "version": 1},
        "lineage": "CTA-EDGE-04-MMV",
        "purpose": ("S1 data freeze for the sealed MMV-OD-2 inputs under the MMV-OD-1 "
                    "latest-known-as-of information concept"),
        "retrieved_utc": started,
        "source_authority": "Federal Reserve Bank of St. Louis, FRED/ALFRED API",
        "api_base": API,
        "credential_source": KEY_SOURCE,
        "credential_in_manifest": "NEVER - api_key is recorded as <REDACTED>",
        "attribution": ("This product uses the FRED(R) API but is not endorsed or "
                        "certified by the Federal Reserve Bank of St. Louis."),
        "series": {},
    }

    for sid in SERIES:
        print(f"  {sid}")
        meta_doc, _ = _get("series", series_id=sid)
        meta = meta_doc["seriess"][0]

        vds = fetch_vintage_dates(sid)
        obs, fetch_mode = fetch_observations(sid, vds)

        obs_path, obs_hash, obs_bytes = _write(f"{sid}.observations.realtime.json", obs)
        vd_path, vd_hash, vd_bytes = _write(f"{sid}.vintagedates.json", vds)
        meta_path, meta_hash, meta_bytes = _write(f"{sid}.series.json", meta)

        ref_dates = sorted({o["date"] for o in obs})
        rt_starts = sorted({o["realtime_start"] for o in obs})
        # a reference month is "missing" if the API returned the '.' sentinel in EVERY
        # real-time interval for it; recorded structurally, never imputed
        by_date = {}
        for o in obs:
            by_date.setdefault(o["date"], []).append(o["value"])
        missing = sorted(d for d, vs in by_date.items() if all(v == "." for v in vs))

        manifest["series"][sid] = {
            "title": meta["title"],
            "units": meta["units"],
            "frequency": meta["frequency"],
            "seasonal_adjustment": meta["seasonal_adjustment"],
            "observation_start": meta["observation_start"],
            "observation_end": meta["observation_end"],
            "last_updated": meta["last_updated"],
            "notes_present": bool(meta.get("notes")),
            "requests": {
                "series": _redacted_params(series_id=sid),
                "observations": _redacted_params(
                    series_id=sid, realtime_start=FULL_REALTIME_START,
                    realtime_end=FULL_REALTIME_END, output_type=1,
                    limit=100000, offset="0..n", fetch_mode="SEE observations_fetch_mode"),
                "vintagedates": _redacted_params(series_id=sid, limit=10000,
                                                 offset="0..n"),
            },
            "files": {
                "series_metadata": {"path": meta_path.replace("\\", "/"),
                                    "sha256": meta_hash, "bytes": meta_bytes},
                "observations_realtime": {"path": obs_path.replace("\\", "/"),
                                          "sha256": obs_hash, "bytes": obs_bytes,
                                          "rows": len(obs)},
                "vintage_dates": {"path": vd_path.replace("\\", "/"),
                                  "sha256": vd_hash, "bytes": vd_bytes,
                                  "count": len(vds)},
            },
            "observations_fetch_mode": fetch_mode,
            "coverage": {
                "distinct_reference_dates": len(ref_dates),
                "first_reference_date": ref_dates[0] if ref_dates else None,
                "last_reference_date": ref_dates[-1] if ref_dates else None,
                "distinct_realtime_starts": len(rt_starts),
                "first_vintage": vds[0] if vds else None,
                "last_vintage": vds[-1] if vds else None,
                "vintage_count": len(vds),
                "reference_dates_with_no_value_in_any_vintage": missing,
            },
        }
        c = manifest["series"][sid]["coverage"]
        print(f"    obs rows {len(obs):>7} | ref dates {c['distinct_reference_dates']:>5} "
              f"({c['first_reference_date']} -> {c['last_reference_date']})")
        print(f"    vintages {len(vds):>7} | {c['first_vintage']} -> {c['last_vintage']}"
              f" | all-missing ref dates: {len(missing)}")

    manifest["finished_utc"] = _dt.datetime.now(_dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"\n  manifest {MANIFEST}")
    print(f"  manifest sha256 {_sha256(MANIFEST)}")
    print("\n  RAW DATA FREEZE COMPLETE. No feature was computed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
