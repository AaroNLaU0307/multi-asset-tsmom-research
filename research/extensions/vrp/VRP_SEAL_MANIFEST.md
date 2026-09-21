# TSMOM-VRP-01 — S1 SEAL MANIFEST (clean lineage base)

```
LINEAGE                          = TSMOM-VRP-01
CONTRACT_ID                      = TSMOM-VRP-01-PREREG-01
SEAL_ACT                         = S1 DESIGN + SEAL performed by Claude Fable 5.1 under Aaron's explicit S1 authorisation of 2026-09-14;
                                   RE-SEALED on a clean lineage base under the S1 bounded repository-base repair (ChatGPT acceptance found one
                                   governance blocker: wrong lineage base; the scientific S1 contract was accepted unchanged)
UTC_SEAL_TIMESTAMP               = 2026-09-14T08:04:09Z
CANONICAL_BASE_BRANCH            = main
CANONICAL_BASE_COMMIT            = d232d3361b23a9f64182c2ec8881284f0fc3b36e   ("ops: C-A off-machine key backup CLOSED — S3 ready for passive accrual";
                                                                              read from local git at repair time; unchanged since the previous inspection)
REPOSITORY_HEAD_BEFORE_SEAL      = d232d3361b23a9f64182c2ec8881284f0fc3b36e   (= CANONICAL_BASE_COMMIT; worktree clean before the package was written)
SEAL_BRANCH                      = vrp/s1-seal-clean   (created from main; contains the canonical base + ONLY the TSMOM-VRP-01 S1 package; inherits
                                                        no C-D-only commit; the C-D branch was not merged and no unrelated commit was cherry-picked)
SEAL_COMMIT                      = recorded in the S1 return block and in PROJECT_STATE at S2 acceptance (a manifest cannot contain the hash of
                                   the commit that contains it)
```

## Prior seal attempt — preserved as provenance, NOT authority

```
PRIOR_ATTEMPT_COMMIT             = d19264af85f45c17f655493e02f71a653bfbdd86   (branch vrp/s1-seal, created from 083268d16accb736a22bcba23b9f64f4df4cb0d2
                                                                              on cd-independent-verification)
PRIOR_ATTEMPT_STATUS             = NON_AUTHORITATIVE_S1_SEAL_ATTEMPT
REASON                           = WRONG_LINEAGE_BASE  (although main was an ancestor, the attempt inherited the unmerged C-D lineage)
DISPOSITION                      = preserved unmodified as provenance; never S2 authority; not rewritten, not deleted
SCIENTIFIC_CONTENT_VS_THIS_SEAL  = byte-identical for VRP_PREREGISTRATION.md, VRP_IMPLEMENTATION_ACCEPTANCE_CONTRACT.md,
                                   VRP_EXPOSURE_DISCLOSURE.md and vrp_prereg_validate.py (hashes below); only this manifest's repository-base
                                   metadata and timestamp differ
```

## Authoritative input hashes (recomputed by `vrp_prereg_validate.py` at the re-seal — all matched)

| Input | Location | SHA256 |
|---|---|---|
| Repaired S0 frame (authoritative) | workspace root `2026-09-14-tsmom-vrp-01-s0-frame-fable-02-repaired.md` | `53f2d094d6fa06358869dda88e77daa80e0feba22c7f9253f2649e622a70d03a` |
| Owner Decision Record (delegated Owner decisions VRP-OD-2 … VRP-OD-9) | workspace root `2026-09-14-tsmom-vrp-01-owner-decision-record.md` | `76232d6c29980c79ece2ba6ead744c203fcf6fa15a70b6045cca91c1d40b9be3` |
| Original S0-01 (historical only) | workspace root `2026-09-14-tsmom-vrp-01-s0-frame-fable-01.md` | `622e85cfdd0f31bbf3bd16f815be6565c433b68bb46556f93fd63fe7878e6859` |
| Frozen ETF panel (Stage-B comparator inputs; already pinned by the programme) | `data/close_prices_raw.csv` (git-ignored) | `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` |

```
OWNER_DECISIONS_HASH             = 76232d6c29980c79ece2ba6ead744c203fcf6fa15a70b6045cca91c1d40b9be3
OWNER_DECISIONS_AUTHORITY        = OWNER_DELEGATED_TO_FABLE_BY_AARON (VRP-OD-2 … VRP-OD-9); VRP-OD-1 resolved by the accepted S0 challenge
OWNER_VALUES_CHANGED             = NO
SCIENTIFIC_DESIGN_CHANGED        = NO
```

## S1 artifact hashes (working-copy bytes = git blob bytes; every file is LF-only under `.gitattributes`)

| Artifact | SHA256 | Versus the prior attempt |
|---|---|---|
| `research/extensions/vrp/VRP_PREREGISTRATION.md` — the sealed contract | `dd5822440bedbe58f49940651bddf656f4dbb593295b59c4eff2b45b89cf53e6` | identical |
| `research/extensions/vrp/VRP_IMPLEMENTATION_ACCEPTANCE_CONTRACT.md` | `4fad50df6ef0c031cdb67e8100034718f49382ce0dd4e6df8e93f29afecb7dbb` | identical |
| `research/extensions/vrp/VRP_EXPOSURE_DISCLOSURE.md` | `afae108d6e894c3822c783d45d77b85e09838578e5e7bf8040ad6dac6a3788c1` | identical |
| `research/extensions/vrp/vrp_prereg_validate.py` — mechanical validator (RESULT: PASS at the re-seal, exit 0) | `4684ecb2c9a633a9d17413a067aa0987a110718518954579a87ffd6122667876` | identical |
| `research/extensions/vrp/VRP_SEAL_MANIFEST.md` — this file | recorded in the S1 return block (a file cannot contain its own hash) | changed: repository-base metadata and timestamp only |

## Sealed seed protocol (constants only; computed with NumPy 2.5.0; no data)

`numpy.random.SeedSequence(7).spawn(4)` in the fixed order **[Stage A historical, Stage B historical, VRP-A-PROSPECTIVE, VRP-B-PROSPECTIVE]** yields children `SeedSequence(entropy=7, spawn_key=(0,))`, `(1,)`, `(2,)`, `(3,)` respectively; each drives `numpy.random.Generator(numpy.random.PCG64(child))`. The seed is a fixed constant of the programme and is derived from nothing.

## Boundaries sealed (unchanged)

```
FORWARD / PROSPECTIVE START RULE = VRP-A-PROSPECTIVE starts at the first VX month-end settlement AFTER this seal (position established at that
                                   settlement, entry cost charged); the first scored month is the following calendar month; N_A = 120 complete
                                   eligible non-invalidated scored months; single terminal reveal. VRP-B-PROSPECTIVE: N_B = 120 calendar months
                                   from the first prospective sleeve month, window frozen there; n_T_min_prosp = 10; conditional on VRP-A =
                                   SUPPORTED; evaluated once only when the core's forward months are legitimately readable
                                   (DEFERRED_EVALUATION_FROZEN_WINDOW / NOT_EVALUABLE otherwise).
HISTORICAL CUTOFF (Stage A)      = 2026-09-01; last Stage-A month = 2026-08; first month mechanical (§F.6); gap months 2026-09 → the month
                                   containing this seal are GAP_MONTHS_EXCLUDED
STAGE-B BOUNDARY                 = complete overlap months only; ends 2026-05-31 under the frozen core boundary 2026-06-12 (June 1–12 2026 is
                                   not an observation); first month = later of the canonical first full-universe scored month (expected
                                   2008-05, determined mechanically) and the first eligible complete VIX-futures month
```

## Prohibited outcome access — statement of record

At S1 and at this re-seal **no** historical VIX-futures settlement value, price history, index return history, candidate-return series, carry statistic, Stage-A or Stage-B outcome was read, downloaded, computed or inspected; **no** VIX-futures file exists in the repository; **no** external page was opened; the protected C-A store, key, position and return layers were **not** touched; **no** canonical quantity was computed for any month; **no** strategy code exists in the package; **no** outcome data exists anywhere for this lineage. Outcome-bearing acquisition begins only after ChatGPT / Aaron acceptance of this seal **and** a separate Owner data-acquisition authorisation; any real run needs a separate single-use Owner execution authorisation; any reveal a separate single-use Owner reveal authorisation.

## Design-contributor disclosure — binding

- **Claude Fable 5.1** — `MATERIAL_DESIGN_CONTRIBUTOR` (Phase-C map, final adjudication, S0-01, S0-02-repaired, the delegated Owner decisions under Aaron's explicit delegation, this S1 package and its re-seal). Never a blind certifier of this design or its results.
- **GPT-6 Astra** — `MATERIAL_DESIGN_CONTRIBUTOR` (independent Phase-C map; the accepted S0 challenge). Never a blind certifier of this design or its results.
- **ChatGPT (Aaron-side)** — programme controller / acceptance checker.
- **Aaron** — Owner; every gate after this seal is Aaron's.
- Canonical TSMOM remains FROZEN; C-A remains LIVE / S3 PASSIVE ACCRUAL; C-D remains CLOSED AT HOLD; nothing in this package upgrades canonical TSMOM evidence.

## Pre-seal checks performed at the re-seal

1. Repository state verified: local `main` HEAD read from git = `d232d33…`, identical to the previously inspected canonical base (zero new commits); `origin/main` is an ancestor of `main`; worktree clean before the package was written.
2. Lineage-base verification, mechanical, on the staged tree against `main` and re-verified on the seal commit (results in the S1 return block): **A** `main` is an ancestor of the seal commit; **B** `git log main..vrp/s1-seal-clean` contains only the seal commit and none of the five C-D-only commits (`3369ce6`, `fa52efd`, `85c831c`, `6234adf`, `083268d`) is an ancestor; **C** `git diff --name-only main` is exactly the five package files; **D** `research/extensions/ca/` is byte-identical to `main`; **E** no VIX outcome-bearing file present (tracked-file name search; no `data/vix`); **F** no strategy implementation exists (the package contains four Markdown files and one validator); **G** Owner values exact (validator section OWNER VALUES); **H** `vrp_prereg_validate.py` RESULT: PASS, exit 0.
3. No unresolved consequential choice remains (contract §T.3, ten questions, all NO). No generated result exists.

```
OLD_SEAL_AUTHORITY               = REJECTED_FOR_LINEAGE_BASE_ONLY  (d19264af85f45c17f655493e02f71a653bfbdd86, preserved)
NEW_SEAL_AUTHORITY               = AUTHORITATIVE_PENDING_CHATGPT_ACCEPTANCE
NEXT_AUTHORIZED_GATE             = CHATGPT FINAL S1 ACCEPTANCE → S2 BUILD / DATA ACQUISITION AUTHORIZATION
S2_AUTHORIZED                    = NO
REAL_RUN_AUTHORIZED              = NO
DATA_ACQUISITION_AUTHORIZED      = NO
NOTHING_PUSHED                   = YES
MAIN_MODIFIED                    = NO
```

*Any receiver recomputes every hash above before use; chat-carried bytes are never a source of truth.*
