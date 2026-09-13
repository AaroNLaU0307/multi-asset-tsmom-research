# -*- coding: utf-8 -*-
"""Render the Value standalone Sharpe interval against the sealed thresholds.

Documentation only. Every number is READ from the already-authoritative stored
artifact and the sealed contract constants -- nothing is recomputed, no backtest
is invoked, and no S3/S4 machinery is touched.

    python research/extensions/value/make_value_ci_figure.py
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (_REPO, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import value_contract as C          # noqa: E402

EVIDENCE = os.path.join(HERE, "VALUE_EVIDENCE.json")
OUT = os.path.join(HERE, "value_sharpe_ci.svg")

W, H = 760, 250
L, R = 90, 710                      # plot x-range in pixels
BAR_Y = 118                         # the interval's baseline
AXIS_Y = 186
LO, HI = -1.8, 0.5                  # Sharpe axis limits


def x(v):
    return L + (v - LO) / (HI - LO) * (R - L)


def main():
    ev = json.load(io.open(EVIDENCE, encoding="utf-8"))
    point = float(ev["VALUE_STANDALONE_STATISTICS"]["point_estimate"])
    lo = float(ev["VALUE_STANDALONE_CI"]["lower"])
    hi = float(ev["VALUE_STANDALONE_CI"]["upper"])
    state = ev["VALUE_STANDALONE_STATE"]
    n = int(ev["N"])
    adverse, positive = -C.F_ADVERSE, C.E_POSITIVE

    p = []
    a = p.append
    a('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
      'viewBox="0 0 %d %d" font-family="-apple-system,Segoe UI,Helvetica,Arial,'
      'sans-serif">' % (W, H, W, H))
    a('<rect width="%d" height="%d" fill="#ffffff"/>' % (W, H))

    a('<text x="%d" y="30" font-size="15" font-weight="600" fill="#111">'
      'Time-Series Value - standalone annualised net Sharpe</text>' % L)
    a('<text x="%d" y="50" font-size="12" fill="#555">Sealed evaluation window '
      '%s to %s, N = %d months. 95%% stationary-bootstrap percentile interval.'
      '</text>' % (L, ev["EVALUATION_START"], ev["EVALUATION_END"], n))

    # region below the adverse floor
    a('<rect x="%.1f" y="66" width="%.1f" height="%d" fill="#fdeeee"/>'
      % (x(LO), x(adverse) - x(LO), AXIS_Y - 66))
    a('<text x="%.1f" y="80" font-size="10.5" fill="#b03030">materially '
      'adverse region</text>' % (x(LO) + 8))

    # threshold lines
    for v, label, col in ((adverse, "adverse floor  %.2f" % adverse, "#c0392b"),
                          (positive, "positive edge  +%.2f" % positive,
                           "#1e7a46")):
        a('<line x1="%.1f" y1="66" x2="%.1f" y2="%d" stroke="%s" '
          'stroke-width="1.6" stroke-dasharray="5,4"/>'
          % (x(v), x(v), AXIS_Y, col))
        a('<text x="%.1f" y="62" font-size="11" fill="%s" '
          'text-anchor="middle">%s</text>' % (x(v), col, label))

    # the interval
    a('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#2c3e6b" '
      'stroke-width="4" stroke-linecap="round"/>'
      % (x(lo), BAR_Y, x(hi), BAR_Y))
    for v in (lo, hi):
        a('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#2c3e6b" '
          'stroke-width="2.5"/>' % (x(v), BAR_Y - 11, x(v), BAR_Y + 11))
    a('<circle cx="%.1f" cy="%d" r="6" fill="#2c3e6b"/>' % (x(point), BAR_Y))

    a('<text x="%.1f" y="%d" font-size="11" fill="#2c3e6b" '
      'text-anchor="middle">%.6f</text>' % (x(lo), BAR_Y - 20, lo))
    a('<text x="%.1f" y="%d" font-size="11" fill="#2c3e6b" '
      'text-anchor="middle">%.6f</text>' % (x(hi), BAR_Y - 20, hi))
    a('<text x="%.1f" y="%d" font-size="12.5" font-weight="600" fill="#2c3e6b" '
      'text-anchor="middle">%.6f</text>' % (x(point), BAR_Y + 30, point))

    # axis
    a('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#888" stroke-width="1"/>'
      % (L, AXIS_Y, R, AXIS_Y))
    v = -1.75
    while v <= HI + 1e-9:
        tick = round(v, 2)
        a('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#888"/>'
          % (x(tick), AXIS_Y, x(tick), AXIS_Y + 5))
        a('<text x="%.1f" y="%d" font-size="10.5" fill="#666" '
          'text-anchor="middle">%.1f</text>' % (x(tick), AXIS_Y + 18, tick))
        v += 0.25
    a('<text x="%d" y="%d" font-size="11" fill="#666">annualised Sharpe</text>'
      % (R - 96, AXIS_Y + 34))

    a('<text x="%d" y="%d" font-size="12" fill="#b03030" font-weight="600">'
      'The entire interval lies below the %.2f adverse floor -&gt; %s</text>'
      % (L, H - 14, adverse, state))
    a('</svg>')

    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(p) + "\n")
    print("wrote %s" % os.path.relpath(OUT, _REPO).replace("\\", "/"))
    print("  point  %.6f   CI [%.6f, %.6f]   state %s" % (point, lo, hi, state))
    print("  thresholds read from the sealed contract: %.2f / +%.2f"
          % (adverse, positive))


if __name__ == "__main__":
    main()
