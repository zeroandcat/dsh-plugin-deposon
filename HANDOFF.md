# HANDOFF — point-in-time handoff (2026-11-27 morning — 2026-11-28 noon register)

**Purpose.** A cold-start handoff for any new session (human or agent). It is
overwritten in place per window; the round ledger is the git history. The
aligned baseline table lives in the "Status" section of `README.md`.

## 1. What changed in the last window (2026-11-27 morning + 2026-11-28 noon)

**2026-11-28 noon additions (T1/T2 register, PI 12:52 five-order window):**

- **Experiment (sweepB pull-back, C5 caliber).** The 11-point sweepB chain
  completed on both hosts (17068 done 05:59:41, 41995 done 06:14:17, all 11
  `arm_rc = 0`, SWEEP-B-DONE tail lines, wall ≈ 6.5 h per host); both hosts
  idled ≈ 6.3–6.5 h GPU-billed before the PI switched them to disk-only at
  12:33 — root cause registered as a single-layer fault on the Alice seat:
  the sweepB ignition string carried no idle-shutdown gate (the 00:56 guard
  belonged to the 11-27→28 night chain, which did trigger correctly: SHUTDOWN
  04:51:11 / 05:11:30). Readings pulled read-only, per-file sha256-identical
  across hosts (41995 tar `02ec1eb1a8cb4b01` / 17068 tar `cb6ef76ecbb85443`,
  package `shared/爱丽丝_sweepB两机读数拉回包_20261128/`); ledger semantics
  read-only (disagreements countersigned, accounts never edited in place);
  `frozen_ts` differs across hosts by design (compare on digests, never on
  timestamps); four-step verification belongs to Bob, verdicts belong to the
  PI.
- **Orchestration (idle-shutdown gate, C4 verdict-A code drop).**
  `deepen_sweep_v1.2.1_idle.py` (199 lines, sha16 `276aff0439885cea`) — the
  in-service `c3e328f5390c4875` stays untouched; the idle variant adds
  `--idle-shutdown-min` (default 0 = bit-compatible) with a unified
  `idle_shutdown()` exit on all four chain outcomes (DONE / budget over-run /
  manifest fail / arm fail; FAIL paths also power off to stop the bleed).
  Validated three layers: py_compile, AST per-function comparison (5
  functions bit-identical, 4 call sites), unit tests 4/4. **Activation waits
  for the next ignition window** (append `--idle-shutdown-min 5` to the
  ignition string); Bob's independent re-run cross-check rides the same
  window.
- **Plugin (B1 package-level visibility closed).** The earlier 401 face was
  GHCR **package-level** settings orthogonal to the repository body —
  digests bit-identical via both pull paths, baseline
  `sha256:6f561244…111c0f`; after the owner flipped the GHCR package public
  (PI console), anonymized pulls verified. The digest anchor above is the
  pull face; publish-image for preview.14 remains a separate trigger (see
  the re-fire paths note below).
- **Discipline (C8).** In-place edits to registered files are patch-style
  with AST per-function comparison only — no hand-written full-file
  rewrites (this morning's first idle-gate draft silently dropped three
  functions; py_compile passed while runtime would NameError; self-caught
  and disclosed on the Alice seat ledger).

- **Experiment.** The two-host three-arm chain (A → C → B) completed on both
  hosts (six arms, exit 0, guard v6 0 ALERT, automatic shutdown executed after
  the chain). The morning data pull and the readings-validator pass are done;
  verdicts are registered as-is: main gate G-A2 not passed (probe hits 0/256 on
  both executor arms; zero-count-arm upper bound 0.011634; McNemar p = 1), G-A3
  and G-B not passed, the never-written negative control clean, the structural
  (true dual-binding) positions all pass with the R-observation readings
  bit-identical across hosts; G-C1 out-of-band, registered in parallel to the
  confirmation rounds (re-judgement requires a new criteria freeze, pending).
- **Plugin.** Release tags `v0.1.0-preview.11` (`5efc158`, CI green),
  `v0.1.0-preview.12` (`dd441be`, tag object `6d66c6ec678f7baf` — P481 C3) and
  `v0.1.0-preview.13` (`e8fe281`, tag object `012a0d0888e7c768` — pushed
  2026-11-27 22:08, single FF 0 force, three refs aligned, CI three triggers
  all success) and `v0.1.0-preview.14` (`535b433`, tag object
  `3c790d3c16f7fa80` — docs-only clearance round, stamped 2026-11-28 under
  the PI plugin-continuation order, Dave four-anchor gate all-pass) stay the
  stable points. The development frontier is `535b433`
  on `b/organ-v311-preview11` (preview.14 docs-only clearance; the G4-A driver
  upgrade `fc74e10` — `deepen_r33 --train-steps`, PI 23:04 verdict A — and the
  preview.14 docs bump were pushed 2026-11-28, single FF 0 force, `main`
  untouched; preview.13 chain `368cc7d`+`e8fe281` precedes them). GHCR runtime image remains `preview.12` (`sha256:de0701a9…`):
  publish-image did not fire on preview.13 because the change face missed the
  `paths: ['docker/**', '.github/workflows/publish.yml']` trigger — re-fire
  paths = commit marker `[image:<tag>]`, workflow_dispatch `image_tag`, or
  touching `docker/**`.
- **Manuscript.** Current verified base = rev4.18 (FREEZE v14 `7926a4c`,
  frozen block `24288e1f900ac743`, branch `private/v5preR3`, public
  repository `zeroandcat/Deposon`, `main` untouched); the r1 stage draft
  (真双绑重制本, 2026-11-28, Charlie seat) is on the table **pending the PI's
  r1-verdict — do not pre-write r1 as current**; not merged into `main`
  (unrelated histories — editorial decision pending).
- **Docs.** The three repositories' README/handoff are aligned to this
  baseline; the companion-plugin sections follow the compatibility draft
  (draft blob `72b8a1f8e85e0d7c`).

## 2. Open items (decisions pending — no action without an order)

1. **Merging the manuscript branch into `main`** of the public repository: the
   two histories are unrelated; a merge would conflict on three root files
   (`.gitignore`, `LICENSE`, `README.md`) and needs an editorial decision.
2. **Plugin**: pushing the development frontier and any tag movement —
   resolved 2026-11-27 (P481 C3): preview.12 merged (ort auto-merge,
   0 conflicts = `15613c1`) and the w5 header fix `dd441be` pushed; tag
   `v0.1.0-preview.12` stamped at `dd441be`. The docs-only register commits
   above `6110448` were merged into the same branch; wording errata (P482
   C1): an earlier register claimed the merge "touches disjoint files" —
   inaccurate: both lines touch README/README.zh in different regions
   (merge verified 0 conflicts), not whole-file disjointness.
3. **G-C1 re-judgement** requires a new criteria freeze event (v1.3) —
   pending; the current verdicts are registered as-is, no gate tuning.
4. **Internal identifiers** that ride along with evidence documents on the
   published manuscript branch are tracked for neutralisation in a follow-up
   commit. The repositories contain no credentials.

## 3. How to verify the baseline offline

Fetch the release tag or the development frontier — from the plugin repository
or from a bundle — and check the pinned sha256 values listed in `README.md` →
Status. Readings data never enters this repository (artifacts policy).

## 4. Plugin surface state (from the compatibility draft, blob `72b8a1f8e85e0d7c`, 2026-11-27)

| 位 | 值 |
|---|---|
| 仓址 | `github.com/zeroandcat/dsh-plugin-deposon` |
| 分支 | `b/organ-v311-preview11` → HEAD `535b433`（preview.14 docs-only 尖：preview.13 线 docs/version bump `368cc7d`＋Lean 伴件 `e8fe281`＋G4-A 驱动器升版 `fc74e10`＋四锚清位 `535b433`·2026-11-28 已推·FF 0 force；码基 `9219e78` 父 `6110448`） |
| main | `e8fe281`（origin/main·preview.13 推送时 FF·本分支领先 2） |
| tag | `v0.1.0-preview.14` → `535b433`（tag 对象 `3c790d3c16f7fa80`·docs-only 四锚清位·2026-11-28 已打·戴夫四锚门全过·PI 插件续推令授权链）；`v0.1.0-preview.13` → `e8fe281`（tag 对象 `012a0d0888e7c768`·2026-11-27 22:08 已推·CI 三触发全 success）；`v0.1.0-preview.12` → `dd441be`（tag 对象 `6d66c6ec678f7baf`·P481 C3 甲 2026-11-27 已打已推·CI 双绿）；`v0.1.0-preview.11` → `5efc158` 沿革 |
| 版本源 | `package.json` `0.1.0-preview.14`（唯一版本源·MCP clientInfo 与升级工具均读它；preview.12/13/14 态由 git tag 标记·docs-only 轮 bump .13→.14·沿革注） |
| preview.12 主件 | `plugin/update.mjs`（selfcheck/plan/apply/rollback·四支柱）＋ `tests/test_update_path.mjs`（16/16） |
| I-3 era 握手 | MCP `initialize` 自报 `era`（executor｜preview.10）＋`executorConfigDigest`·驱动器/自测件声明期望·不等 fail-loud（防臂串线） |
| I-4 依赖探测 | 执行器 lazy import——E-off 面 0 第三方依赖；执行器态缺 cryptography ⇒ stderr 明示＋exit 3（不静默降级） |
| 自检矩阵 | quickcheck 16/16 · organ 自测 82/82 · 驱动器自检 19/19（18→19·T00 拆 T00a/b） · plugin load 全过 · update 路径 16/16 · selftest_mcp E-off 30/30（执行器态 29/30＝K-out 渲染已知差·D19a/b 覆盖） |
| 重钉链 | selftest_organ_v3 仓现件 `3b19207a5292`→`4a0a51bb4dcce893`（delta2＝D10 判据 stdout 空回退 stderr 尾·防 IndexError）；deepen_r33 `826231fbb9f61f5c`→`335082d86437`（CUDA preflight rc3＋exec_dir_face 报告位）；selftest_p3_driver `5105011f3002fc7b`→`01a11e290d74db79`；manifest driver_sha12 重冻归下窗（点火面钉定副本 62cb86c40a80 全程 0 动） |
| w5 伴件 | `harness/DeposonThermoReconW.lean`（sha12 `daf39e5e3cab`·与在册逐位同·0 改；头注措辞问题候 PI） |
| 兼容注 | preview.12 mcp 面与钉定自测 62cb86c40a80 的 D10 判据**兼容**（D10 只认 `SELFTEST-PASS` 尾·段八新增 5 格在 E-off 显式 env 下全过） |

## 5. Experiment / orchestration plane register (2026-11-28 noon)

The orchestration-plane files circulate as fingerprinted artifacts (no
dedicated git repository); this section is their docs face. All values are
in-register, 0 estimated; verdicts belong to the PI.

- **In-service orchestration pair**: `sweep1_readings` `c50d2b8e86adeaba` +
  `deepen_sweep` v1.2.1 `c3e328f5390c4875` (deployed on both hosts,
  17068 pw-path / 41995 key-path). Candidate next-in-service:
  `deepen_sweep_v1.2.1_idle.py` `276aff0439885cea` (C4 above; activates at
  the next ignition window, current pair untouched until then).
- **sweepB readings (C5)**: 11 points × 2 hosts, pre-registered
  criteria/digest expectations chain `c50d2b8e86adeaba`-era; pull-back
  package `shared/爱丽丝_sweepB两机读数拉回包_20261128/` (tars sha-identical
  across hosts: `02ec1eb1a8cb4b01` / `cb6ef76ecbb85443`); per-point light
  verification face ≈ 1.3 MB (criteria 20K + manifest + batch_plan +
  reading_pkg_A + probe_ledger + train_ev_stats), heavy ckpt artifacts
  (~1.5–2.3 GB/point) stay on host disks (AutoDL power-off keeps disks).
  Verification checklist (Bob): ① manifest frozen_ts cross-host per the
  digest-face caliber ② sweep_ledger.jsonl + sweepB.log SWEEP-B-DONE
  cross-read ③ 11-point arm_rc + criteria/digest expectations vs the
  pre-registered base ④ verification package to the group. Verdicts: PI.
- **r33 arm-level anchor (sweepB pt, 41995 log tail)**: DEEPEN-R33-DONE
  round=R3.3-criteria_v3, to=200, wall 2103.7 s, best_step 190, viol_total 0,
  nan_free true, lost_set_sha12 `bf5c1197646d`, manifest_sha12 `e7cefc4673bb`,
  reading_pkg_sha12 `243801d4…`, face4a three true, r_obs util_A 0.9875 /
  r_share 0.666667; cross-arm node PENDING_VALIDATOR (validator candidate
  `bc1a9f3247537a78` v0.1 input).
- **H2 interface anchors (Bob morning re-check, no drift)**: N3 scan floor
  0.011719 (readings `c50d2b8e86adeaba`, det re-run digest
  `7c074aebae6bded5`, 43/43 points hit) — directly citable for the R2 P-iii
  noise-floor cross-check, no recompute needed; N7 six-variant ablation =
  GPU item awaiting a card window; N8 untouched (v1.2 case-file register) —
  both ride the R3 four-round carrier.
