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
