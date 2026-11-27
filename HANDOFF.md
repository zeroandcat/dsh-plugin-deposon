# HANDOFF — point-in-time handoff (2026-11-27, morning register)

**Purpose.** A cold-start handoff for any new session (human or agent). It is
overwritten in place per window; the round ledger is the git history. The
aligned baseline table lives in the "Status" section of `README.md`.

## 1. What changed in the last window (2026-11-27 morning)

- **Experiment.** The two-host three-arm chain (A → C → B) completed on both
  hosts (six arms, exit 0, guard v6 0 ALERT, automatic shutdown executed after
  the chain). The morning data pull and the readings-validator pass are done;
  verdicts are registered as-is: main gate G-A2 not passed (probe hits 0/256 on
  both executor arms; zero-count-arm upper bound 0.011634; McNemar p = 1), G-A3
  and G-B not passed, the never-written negative control clean, the structural
  (true dual-binding) positions all pass with the R-observation readings
  bit-identical across hosts; G-C1 out-of-band, registered in parallel to the
  confirmation rounds (re-judgement requires a new criteria freeze, pending).
- **Plugin.** Release tags `v0.1.0-preview.11` (`5efc158`, CI green) and
  `v0.1.0-preview.12` (`dd441be`, tag object `6d66c6ec678f7baf` — P481 C3)
  stay the stable points. The development frontier is `dd441be` on
  `b/organ-v311-preview11` (preview.12 merge `15613c1` with the docs-only
  register commits via ort auto-merge, 0 conflicts, plus the w5 header fix):
  the update/upgrade path, the ledger-era handshake server half, lazy
  executor imports, re-pinned self-tests and the README "Update / upgrade"
  section — merged and pushed 2026-11-27 (the earlier "local-commit-only"
  wording is superseded; see the errata note in item 2).
- **Manuscript.** rev4.17 (`2c8252f`) frozen as FREEZE v13 at the branch tip
  `dea75bc` of branch `private/v5preR3` (public repository
  `zeroandcat/Deposon`, 77 commits, `main` untouched); not merged into `main`
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
| 分支 | `b/organ-v311-preview11` → HEAD `286811e`（preview.12 线：合流 `15613c1`＋w5 头注 `dd441be`＋docs 勘正·内容基 `9219e78` 父 `6110448`） |
| main | `1e27d7c`（origin/main·本分支领先 5） |
| tag | `v0.1.0-preview.12` → `dd441be`（tag 对象 `6d66c6ec678f7baf`·P481 C3 甲 2026-11-27 已打已推·CI 双绿）；`v0.1.0-preview.11` → `5efc158` 沿革 |
| 版本源 | `package.json` `0.1.0-preview.13`（唯一版本源·MCP clientInfo 与升级工具均读它；preview.12 态由 git tag 标记·版本字段自 preview.11 直跳 .13·沿革注） |
| preview.12 主件 | `plugin/update.mjs`（selfcheck/plan/apply/rollback·四支柱）＋ `tests/test_update_path.mjs`（16/16） |
| I-3 era 握手 | MCP `initialize` 自报 `era`（executor｜preview.10）＋`executorConfigDigest`·驱动器/自测件声明期望·不等 fail-loud（防臂串线） |
| I-4 依赖探测 | 执行器 lazy import——E-off 面 0 第三方依赖；执行器态缺 cryptography ⇒ stderr 明示＋exit 3（不静默降级） |
| 自检矩阵 | quickcheck 16/16 · organ 自测 82/82 · 驱动器自检 19/19（18→19·T00 拆 T00a/b） · plugin load 全过 · update 路径 16/16 · selftest_mcp E-off 30/30（执行器态 29/30＝K-out 渲染已知差·D19a/b 覆盖） |
| 重钉链 | selftest_organ_v3 仓现件 `3b19207a5292`→`4a0a51bb4dcce893`（delta2＝D10 判据 stdout 空回退 stderr 尾·防 IndexError）；deepen_r33 `826231fbb9f61f5c`→`335082d86437`（CUDA preflight rc3＋exec_dir_face 报告位）；selftest_p3_driver `5105011f3002fc7b`→`01a11e290d74db79`；manifest driver_sha12 重冻归下窗（点火面钉定副本 62cb86c40a80 全程 0 动） |
| w5 伴件 | `harness/DeposonThermoReconW.lean`（sha12 `daf39e5e3cab`·与在册逐位同·0 改；头注措辞问题候 PI） |
| 兼容注 | preview.12 mcp 面与钉定自测 62cb86c40a80 的 D10 判据**兼容**（D10 只认 `SELFTEST-PASS` 尾·段八新增 5 格在 E-off 显式 env 下全过） |
