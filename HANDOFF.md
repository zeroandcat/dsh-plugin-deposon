# HANDOFF — point-in-time handoff (2026-11-27)

**Purpose.** A cold-start handoff for any new session (human or agent). It is
overwritten in place per window; the round ledger is the git history. The
aligned baseline table lives in the "Status" section of `README.md`.

## 1. What changed in the last window (2026-11-26 → 2026-11-27)

- **Plugin.** Release tag `v0.1.0-preview.11` (`5efc158`, CI green). Development
  head `6110448` on `b/organ-v311-preview11` adds the executor-integrated
  experiment driver, its CPU self-test and the horizon slot calculator; verified
  code is untouched.
- **Criteria.** The single open numeric slot of `criteria_v3` v1.2 was backfilled
  (v1.2.1, `horizon.value = 12`, calibrated on the ignition hosts: feasible
  interval [9, 15], four confirmation chains passing).
- **Experiment.** A three-arm run under one frozen manifest was launched on two
  hosts with a stop-loss guard (floor check before each arm, stop on any non-zero
  exit, automatic shutdown after the chain). Arm A has completed on the first
  host; arms C and B follow. Verdicts are not claimed here.
- **Manuscript.** The manuscript chain was published as branch `private/v5preR3`
  of the public repository `zeroandcat/Deposon`, commit hashes preserved; it is
  not merged into that repository's `main`.

## 2. Open items (decisions pending — no action without an order)

1. **Merging the manuscript branch into `main`** of the public repository: the
   two histories are unrelated; a merge would conflict on three root files
   (`.gitignore`, `LICENSE`, `README.md`) and needs an editorial decision.
2. **Plugin release tag for `6110448`** (preview.12): pending; the tag stays at
   preview.11 until then.
3. **After the run**: pull the reading packages, run the readings validator, and
   register the gate verdicts as-is — no gate tuning, no re-run to fill.
4. **dsh update / upgrade compatibility**: design and implementation pending.
5. **Internal identifiers** that ride along with evidence documents on the
   published manuscript branch are tracked for neutralisation in a follow-up
   commit. The repositories contain no credentials.

## 3. How to verify the baseline offline

Fetch the release tag or the development commit — from this repository or from a
bundle — and check the pinned sha256 values listed in `README.md` → Status.
Readings data never enters this repository (artifacts policy).
