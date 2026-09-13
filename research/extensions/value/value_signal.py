# -*- coding: utf-8 -*-
"""Value signal engine: causal expanding normalisation, sign-only primary,
and the deterministic valuation-episode grammar.

No return series is read here and no performance quantity is produced.
"""
import math

from value_contract import K_EPISODES, UNIVERSE, WARMUP_MONTHS
from value_data import m_key


def expanding_z(values):
    """z_i(t) over the object's OWN expanding history, causal, ddof = 1.

    `values` is an ordered list of (month, value_or_None). At each t the mean and
    sd use every non-missing observation from the object's first month through t
    INCLUSIVE — never later. Fewer than WARMUP_MONTHS observations, or zero
    dispersion, yields None (the signal then becomes 0).
    """
    out, hist = [], []
    for month, v in values:
        if v is None:
            out.append((month, None))
            continue
        hist.append(v)
        n = len(hist)
        if n < WARMUP_MONTHS:
            out.append((month, None))
            continue
        mu = sum(hist) / n
        var = sum((x - mu) ** 2 for x in hist) / (n - 1)
        if var <= 0.0:
            out.append((month, None))
            continue
        out.append((month, (v - mu) / math.sqrt(var)))
    return out


def sign_signal(z_series):
    """Sign-only primary signal. sign(0) = 0; an unavailable z gives 0."""
    out = []
    for month, z in z_series:
        if z is None:
            out.append((month, 0))
        elif z > 0:
            out.append((month, 1))
        elif z < 0:
            out.append((month, -1))
        else:
            out.append((month, 0))
    return out


def build_signals(objects, months):
    """{instrument: [(month, sign)]} for the sealed universe."""
    sig = {}
    for inst in UNIVERSE:
        series = [(t, objects[inst].get(t)) for t in months]
        sig[inst] = sign_signal(expanding_z(series))
    return sig


# --------------------------------------------------------------------------- #
# valuation episodes  (§11) — defined from the SIGNAL PATH only
# --------------------------------------------------------------------------- #
class Episode(object):
    __slots__ = ("instrument", "start", "end", "months", "sign")

    def __init__(self, instrument, months, sign):
        self.instrument = instrument
        self.months = list(months)
        self.start = self.months[0]
        self.end = self.months[-1]
        self.sign = sign

    def __len__(self):
        return len(self.months)

    def __repr__(self):
        return "Episode(%s, %s..%s, n=%d, sign=%+d)" % (
            self.instrument, self.start, self.end, len(self.months), self.sign)


def episodes_for(instrument, signal):
    """Maximal runs of constant sign(z). Uses no return data whatsoever."""
    out, run, cur = [], [], None
    for month, s in signal:
        if cur is None or s == cur:
            run.append(month)
            cur = s
        else:
            out.append(Episode(instrument, run, cur))
            run, cur = [month], s
    if run:
        out.append(Episode(instrument, run, cur))
    return out


_INSTRUMENT_ORDER = {name: i for i, name in enumerate(UNIVERSE)}


def rank_episodes(all_episodes):
    """Total order: month count DESC, then earlier start, then fixed instrument
    order. Totality is what makes 'the three largest' unique."""
    return sorted(all_episodes,
                  key=lambda e: (-len(e), m_key(e.start),
                                 _INSTRUMENT_ORDER[e.instrument]))


def select_episodes(signals, k=K_EPISODES):
    """Pool across instruments, rank deterministically, take the top k."""
    pooled = []
    for inst in UNIVERSE:
        if inst in signals:
            pooled.extend(episodes_for(inst, signals[inst]))
    return rank_episodes(pooled)[:k]


def delete_months(sample_months, episode):
    """SUPERSEDED by VALUE_S1_EPISODE_REACHABILITY_AMENDMENT_003 — NOT the
    sealed C3 operator any more.

    Whole-calendar deletion: drop the episode's calendar months from the entire
    paired sample. On the real signal path this removed 129-143 of 143 months
    and left C3 unadjudicable, which is why the operator was amended. Retained
    only as a plain utility; the sealed operator is
    `value_sleeve.ablate` driven by `value_inference.run_c3_ablation`."""
    drop = set(episode.months)
    return [m for m in sample_months if m not in drop]
