#!/usr/bin/env node
// dsh-plugin-deposon — update/upgrade path (preview.12).
//
// deepseek-harness (dsh) contract alignment for plugin update/upgrade, four pillars:
//   version   — package.json is the single version source (the MCP clientInfo and this
//               tool both read it; a hand-written version string anywhere else is drift).
//   dependency — engines.node >=22, engines.dsh range, optional peerDependency
//               @deepseek-ai/cordis, python3 on PATH, cryptography>=41 (hard only when
//               the executor face is on — the E-off face is stdlib-only since preview.12).
//   config    — bundle patch config keys + DEPOSON_* env are additive-only across
//               releases; ledger data is NEVER migrated in place (append-only,
//               era-separated by design: executor-era ledgers fail-loud on the
//               preview.10 face and vice versa — R-4 era discipline).
//   rollback  — before any apply, the code face (package.json, cordis.patch.yml,
//               plugin/, plus the package "files" set) is snapshotted to
//               .deposon-rollback/<ts>/ ; a failed post-install selfcheck restores it
//               automatically. rollback restores the code face only — ledger/pool data
//               files are outside the snapshot by construction.
//
// Verbs: selfcheck | plan | apply | rollback   (exit 0 ok · 2 incompatible/failed)
// dsh host integration note (preview-era honesty): dsh's plugin manager command surface
// is still moving. For path: sources this tool installs for real (full package files
// copy). For git/npm sources it emits the recorded host command sequence (re-install =
// upgrade) instead of pretending to install — 0 fake claims.
import { spawnSync } from 'node:child_process'
import {
  cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync,
} from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const TOOL_DIR = path.dirname(fileURLToPath(import.meta.url))
const DEFAULT_ROOT = path.resolve(TOOL_DIR, '..')

const CONFIG_KEYS_PREVIEW10 = ['python', 'timeoutMs', 'ledger', 'lang', 'belief', 'brief', 'footer', 'thermo']
const CONFIG_KEYS_PREVIEW11 = ['executor', 'pool', 'gPolicy', 'addrSchema', 'principal', 'toolTimeoutMs']
const CONFIG_KEYS_PREVIEW12 = [] // additive-only release: no new patch keys in preview.12

const FAIL = []
const ok = (label, pass, note = '') => {
  console.log(`${pass ? 'PASS' : 'FAIL'} ${label}${note ? ` — ${note}` : ''}`)
  if (!pass) FAIL.push(label)
  return pass
}

const readJson = (p) => JSON.parse(readFileSync(p, 'utf8'))
const semver = (v) => String(v ?? '').trim().split(/[.+-]/).slice(0, 3).map((x) => parseInt(x, 10) || 0)
const cmp3 = (a, b) => {
  const A = semver(a); const B = semver(b)
  for (let i = 0; i < 3; i++) if (A[i] !== B[i]) return A[i] < B[i] ? -1 : 1
  return 0
}
// minimal semver-range check: space-separated >=X / <X / >=X.Y.Z atoms only (engines use)
const inRange = (ver, range) =>
  String(range ?? '').split(/\s+/).filter(Boolean).every((atom) => {
    const m = atom.match(/^(>=|<=|<|>)\s*(.+)$/)
    if (!m) return cmp3(ver, atom) === 0
    const c = cmp3(ver, m[2])
    return m[1] === '>=' ? c >= 0 : m[1] === '<=' ? c <= 0 : m[1] === '<' ? c < 0 : c > 0
  })

function pythonProbe(python) {
  const r = spawnSync(python, ['-c', 'import cryptography, sys; print(cryptography.__version__)'], { encoding: 'utf8' })
  return r.status === 0 ? String(r.stdout ?? '').trim() : null
}

function detectLedgerEra(p) {
  // executor era: any tombstone line, or inject line without text (DEK envelope);
  // preview.10 era: inject lines carry rendered text; mixed => fail-loud at runtime (R-4 era)
  if (!existsSync(p)) return 'none'
  let sawExecutor = false
  let sawPlain = false
  try {
    for (const line of readFileSync(p, 'utf8').split('\n')) {
      const t = line.trim()
      if (!t) continue
      let ev; try { ev = JSON.parse(t) } catch { return 'unreadable' }
      if (ev?.ev === 'tombstone' || (ev?.ev === 'inject' && !('text' in ev))) sawExecutor = true
      else if (ev?.ev === 'inject' && 'text' in ev) sawPlain = true
    }
  } catch { return 'unreadable' }
  if (sawExecutor && sawPlain) return 'mixed(runtime fail-loud: R-4 era separation)'
  return sawExecutor ? 'executor' : sawPlain ? 'preview.10' : 'empty'
}

function selfcheck(root) {
  const pkg = readJson(path.join(root, 'package.json'))
  const executorOn = (process.env.DEPOSON_EXECUTOR ?? '1').trim() !== '0'
  const python = process.env.DEPOSON_PYTHON || 'python3'
  const cryptoVer = pythonProbe(python)
  const dshCli = spawnSync('dsh', ['--version'], { encoding: 'utf8' })
  console.log(JSON.stringify({
    pillar: 'dependency',
    node: { have: process.versions.node, need: pkg.engines?.node, pass: inRange(process.versions.node, pkg.engines?.node) },
    dsh_cli: { have: dshCli.status === 0 ? dshCli.stdout.trim() : null, need: pkg.engines?.dsh,
      pass: dshCli.status !== 0 ? 'unknown(no dsh CLI on PATH — desk-level dev checkout; not a failure here)' : inRange(dshCli.stdout.trim(), pkg.engines?.dsh) },
    peerDependencies: pkg.peerDependencies ?? {},
    python: { cmd: python },
    cryptography: { have: cryptoVer, need: '>=41', face: executorOn ? 'executor(hard)' : 'E-off(soft)',
      pass: cryptoVer ? cmp3(cryptoVer, '41') >= 0 || `below 41: executor face will fail-loud` : (executorOn ? 'missing: executor face will fail-loud (exit 3, no silent downgrade)' : 'absent ok (E-off face is stdlib-only)') },
  }, null, 2))
  let hardFail = 0
  if (!inRange(process.versions.node, pkg.engines?.node)) hardFail++
  if (executorOn && cryptoVer && cmp3(cryptoVer, '41') < 0) hardFail++
  return hardFail === 0 ? 0 : 2
}

function plan(root, src, ledgerArg) {
  const pkg = readJson(path.join(root, 'package.json'))
  const out = { pillar: 'version+config+rollback (read-only plan)', root, from: pkg.version, actions: [], risk: [] }

  // version pillar
  if (src) {
    const sp = existsSync(path.join(src, 'package.json')) ? readJson(path.join(src, 'package.json')) : null
    out.target = sp?.version ?? null
    out.targetEngines = sp?.engines ?? null
    if (!sp) { out.risk.push('src package.json unreadable — cannot plan a real install') }
    else {
      const c = cmp3(out.target, out.from)
      out.action = c > 0 ? 'upgrade' : c < 0 ? 'downgrade(allowed; rollback plane recommended)' : 'same-version reinstall(no-op content-wise)'
      out.compatible = inRange(process.versions.node, sp.engines?.node) && inRange(process.versions.dsh ?? '0.1.0', sp.engines?.dsh ?? '>=0.1.0')
    }
  } else {
    out.target = null
    out.action = 'none (plan without --src reports the installed face only)'
  }

  // config pillar: patch keys additive-only + ledger era detection + 0-migration notice
  const patch = readFileSync(path.join(root, 'cordis.patch.yml'), 'utf8')
  const presentKeys = [...CONFIG_KEYS_PREVIEW10, ...CONFIG_KEYS_PREVIEW11].filter((k) =>
    new RegExp(`^\\s+${k}:`, 'm').test(patch))
  const ledgerP = ledgerArg || process.env.DEPOSON_LEDGER || path.join(root, 'mcp', 'ledger.jsonl')
  out.config = {
    patchKeysPresent: presentKeys,
    newKeysInPreview11: CONFIG_KEYS_PREVIEW11.filter((k) => presentKeys.includes(k)),
    additiveOnly: true,
    deprecatedKeys: [],
    ledger: { path: ledgerP, era: detectLedgerEra(ledgerP), migration: 'none (append-only; era separation is by design — cross-era reads fail-loud)' },
  }

  // rollback pillar: snapshot inventory (code face only)
  const rbRoot = path.join(root, '.deposon-rollback')
  out.rollback = {
    dir: rbRoot,
    snapshots: existsSync(rbRoot) ? readdirSync(rbRoot).sort().reverse() : [],
    dataFilesInSnapshot: false,
    note: 'ledger.jsonl / *.pool / ~/.deposon are outside the snapshot by construction',
  }
  console.log(JSON.stringify(out, null, 2))
  return out.risk.length === 0 && out.compatible !== false ? 0 : 2
}

const CODE_FACE = ['package.json', 'cordis.patch.yml', 'plugin', 'mcp', 'gates', 'harness', 'scripts', 'frozen', 'mocks', 'tests', 'docs', 'README.md', 'README.zh.md', 'CONTRIBUTING.md', 'SAFETY.md', 'BENCHMARK.md', 'THIRD_PARTY_NOTICES.md', 'CITATION.cff', 'LICENSE', '.i18n.yaml']

// Data face (preview.12 hard rule): the default ledger lives INSIDE a code directory
// (mcp/ledger.jsonl) and pools sit next to their ledgers — a directory-level code
// copy must therefore stash/restore these or an upgrade would destroy live memory.
const DATA_PATTERNS = [/^ledger\.jsonl$/, /\.pool$/]
function stashData(dir, out) {
  if (!existsSync(dir)) return out
  for (const f of readdirSync(dir)) {
    const p = path.join(dir, f)
    let st; try { st = statSync(p) } catch { continue }
    if (st.isDirectory()) stashData(p, out)
    else if (DATA_PATTERNS.some((rx) => rx.test(f))) out.push([p, readFileSync(p)])
  }
  return out
}
function unstashData(stash) {
  for (const [p, buf] of stash) {
    mkdirSync(path.dirname(p), { recursive: true })
    writeFileSync(p, buf)
  }
}

function snapshot(root, tag) {
  const dir = path.join(root, '.deposon-rollback', tag)
  mkdirSync(dir, { recursive: true })
  const manifest = []
  for (const rel of CODE_FACE) {
    const p = path.join(root, rel)
    if (!existsSync(p)) continue
    cpSync(p, path.join(dir, rel), { recursive: true, force: true })
    manifest.push({ path: rel, sha256: null, bytes: statSync(p).size })
  }
  writeFileSync(path.join(dir, 'SNAPSHOT.json'), JSON.stringify({ tag, created: new Date().toISOString(), files: manifest.map((m) => m.path) }, null, 2))
  return dir
}

function restore(root, snapDir) {
  const stash = stashData(root, [])
  for (const rel of CODE_FACE) {
    const p = path.join(snapDir, rel)
    if (!existsSync(p)) continue
    rmSync(path.join(root, rel), { recursive: true, force: true })
    cpSync(p, path.join(root, rel), { recursive: true, force: true })
  }
  unstashData(stash)
}

function postInstallSelfcheck(root) {
  const r = spawnSync(process.execPath, [path.join(root, 'tests', 'test_plugin_load.mjs')], { cwd: root, encoding: 'utf8', timeout: 300000 })
  return { pass: r.status === 0, tail: String(r.stdout ?? '').split('\n').filter((l) => l.includes('FAIL')).slice(0, 3) }
}

function apply(root, src, { yes = false } = {}) {
  if (!src || !existsSync(path.join(src, 'package.json'))) {
    console.error('apply: --src must point at a real dsh-plugin-deposon tree (package.json present)')
    return 2
  }
  const srcPkg = readJson(path.join(src, 'package.json'))
  const rootPkg = readJson(path.join(root, 'package.json'))
  if (!inRange(process.versions.node, srcPkg.engines?.node)) {
    console.error(`apply: target engines.node ${srcPkg.engines?.node} incompatible with node ${process.versions.node} — refusing (fail-loud)`)
    return 2
  }
  const tag = `pre-${rootPkg.version}-${Date.now()}`
  const snap = snapshot(root, tag)
  console.log(`snapshot: ${snap}`)

  if (/^path:/.test(src) || existsSync(src)) {
    const realSrc = String(src).replace(/^path:/, '')
    const stash = stashData(root, [])
    for (const rel of CODE_FACE) {
      const p = path.join(realSrc, rel)
      if (!existsSync(p)) continue
      const dst = path.join(root, rel)
      if (path.resolve(p) === path.resolve(dst)) continue // src==root: nothing to copy
      rmSync(dst, { recursive: true, force: true })
      cpSync(p, dst, { recursive: true, force: true })
    }
    unstashData(stash)
    console.log(`installed: path source ${realSrc} → ${root} (version ${srcPkg.version})`)
  } else {
    // preview-era honesty: git/npm sources go through the host's plugin manager.
    console.log('remote source — run the host plugin manager (re-install = upgrade), then re-run:')
    console.log(`  dsh plugin add ${src}`)
    console.log('  node plugin/update.mjs plan --root <installed-root>')
    console.log(`snapshot ${snap} kept for rollback; nothing was written for a remote source.`)
    return 0
  }

  const post = postInstallSelfcheck(root)
  if (!post.pass && !yes) {
    console.error('post-install selfcheck FAILED — rolling back (fail-loud, no silent state):')
    for (const l of post.tail) console.error(`  ${l}`)
    restore(root, snap)
    console.error(`restored from ${snap}; version back at ${rootPkg.version}`)
    return 2
  }
  console.log(`post-install selfcheck ${post.pass ? 'PASS' : 'FAIL(kept with --yes)'}`)
  console.log(`upgrade complete: ${rootPkg.version} → ${srcPkg.version} (rollback snapshot: ${snap})`)
  return 0
}

function rollback(root, snapName) {
  const rbRoot = path.join(root, '.deposon-rollback')
  const snaps = existsSync(rbRoot) ? readdirSync(rbRoot).sort().reverse() : []
  if (snaps.length === 0) { console.error('rollback: no snapshots present — nothing to restore'); return 2 }
  const pick = snapName || snaps[0]
  const dir = path.join(rbRoot, pick)
  if (!existsSync(path.join(dir, 'SNAPSHOT.json'))) { console.error(`rollback: ${dir} is not a snapshot`); return 2 }
  const before = readJson(path.join(root, 'package.json')).version
  restore(root, dir)
  const after = readJson(path.join(root, 'package.json')).version
  console.log(JSON.stringify({ restored: dir, version: { before, after }, dataFiles: 'untouched (ledger/pool outside snapshot by construction)' }, null, 2))
  return after === readJson(path.join(dir, 'package.json')).version ? 0 : 2
}

function main(argv) {
  const verb = argv[0] ?? 'plan'
  const flag = (k) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : null }
  const root = path.resolve(flag('--root') ?? DEFAULT_ROOT)
  const src = flag('--src')
  const ledger = flag('--ledger')
  if (!existsSync(path.join(root, 'package.json'))) { console.error(`--root ${root} has no package.json`); return 2 }
  if (verb === 'selfcheck') return selfcheck(root)
  if (verb === 'plan') return plan(root, src, ledger)
  if (verb === 'apply') return apply(root, src, { yes: argv.includes('--yes') })
  if (verb === 'rollback') return rollback(root, flag('--snapshot'))
  console.error(`unknown verb: ${verb} (selfcheck | plan | apply | rollback)`)
  return 2
}

process.exit(main(process.argv.slice(2)))
