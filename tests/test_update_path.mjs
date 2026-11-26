// update/upgrade path test (preview.12) — plain Node, no dependencies.
// Four pillars under test: version / dependency / config (incl. ledger era
// detection) / rollback (snapshot → apply → selfcheck → restore, data files
// byte-untouched). Exit 0 only if every check passes.
import { spawnSync } from 'node:child_process'
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const UPDATE = path.join(HERE, 'plugin', 'update.mjs')
let failures = 0
const check = (label, cond) => {
  console.log(`${cond ? 'PASS' : 'FAIL'} ${label}`)
  if (!cond) failures++
}
const run = (args, env = {}) =>
  spawnSync(process.execPath, [UPDATE, ...args], { encoding: 'utf8', timeout: 300000, env: { ...process.env, ...env } })
const sha = (p) => undefined ?? null // placeholder (crypto via node:crypto below)
import { createHash } from 'node:crypto'
const sha256 = (p) => createHash('sha256').update(readFileSync(p)).digest('hex')

// --- 1. selfcheck (dependency pillar) --------------------------------------
const sc = run(['selfcheck'])
check('selfcheck exit 0 + JSON parses', sc.status === 0 && (() => { try { JSON.parse(sc.stdout); return true } catch { return false } })())

// --- 2. plan baseline (version+config+rollback pillars) ---------------------
const plan0 = run(['plan'])
let p0 = null
try { p0 = JSON.parse(plan0.stdout) } catch {}
check('plan exit 0 · current version matches package.json', plan0.status === 0 && p0?.from === JSON.parse(readFileSync(path.join(HERE, 'package.json'), 'utf8')).version)
check('plan lists preview.10+11 config keys (additive-only face)', p0?.config?.patchKeysPresent?.length >= 14)
check('plan declares 0 data migration', String(p0?.config?.ledger?.migration).includes('none'))

// --- 3. ledger era detection (config pillar, R-4 era) ------------------------
const tmp0 = mkdtempSync(path.join(os.tmpdir(), 'deposon-update-'))
const plainLed = path.join(tmp0, 'plain.jsonl')
const execLed = path.join(tmp0, 'exec.jsonl')
const mixedLed = path.join(tmp0, 'mixed.jsonl')
writeFileSync(plainLed, JSON.stringify({ ev: 'inject', id: 'k', key: 'a.b', text: 'x', ts: 1 }) + '\n')
writeFileSync(execLed, JSON.stringify({ ev: 'inject', id: 'k', key: 'a.b', dek: 'envelope' }) + '\n' + JSON.stringify({ ev: 'tombstone', id: 't', tick: 2 }) + '\n')
writeFileSync(mixedLed, JSON.stringify({ ev: 'inject', id: 'k', key: 'a.b', text: 'x' }) + '\n' + JSON.stringify({ ev: 'tombstone', id: 't', tick: 2 }) + '\n')
const eraOf = (p) => JSON.parse(run(['plan', '--ledger', p]).stdout).config.ledger.era
check('plain ledger → preview.10 era', eraOf(plainLed) === 'preview.10')
check('executor ledger → executor era', eraOf(execLed) === 'executor')
check('mixed ledger → runtime fail-loud label', String(eraOf(mixedLed)).includes('fail-loud'))

// --- 4. sandbox install/rollback cycle (version+rollback pillars) ------------
const root = path.join(tmp0, 'root')
mkdirSync(root, { recursive: true })
for (const rel of ['package.json', 'cordis.patch.yml', 'plugin', 'tests', 'mcp', 'gates', 'harness', 'scripts']) {
  const s = path.join(HERE, rel)
  if (existsSync(s)) cpSync(s, path.join(root, rel), { recursive: true, force: true })
}
// old sandbox face: fake older version + a data file that must survive untouched
const sandboxPkgPath = path.join(root, 'package.json')
const oldPkg = JSON.parse(readFileSync(sandboxPkgPath, 'utf8'))
oldPkg.version = '0.0.1-oldface'
writeFileSync(sandboxPkgPath, JSON.stringify(oldPkg, null, 2))
const dataLed = path.join(root, 'mcp', 'ledger.jsonl')
writeFileSync(dataLed, 'data-line-must-not-move\n')
const dataShaBefore = sha256(dataLed)
const patchShaBefore = sha256(path.join(root, 'cordis.patch.yml'))

const ap = run(['apply', '--src', HERE, '--root', root])
const apOut = ap.stdout
check('apply exit 0 · version upgraded', ap.status === 0 && JSON.parse(readFileSync(sandboxPkgPath, 'utf8')).version === JSON.parse(readFileSync(path.join(HERE, 'package.json'), 'utf8')).version)
check('apply made a pre-install snapshot', /snapshot: .*\.deposon-rollback[/\\]pre-/.test(apOut))
check('apply post-install selfcheck ran', apOut.includes('post-install selfcheck PASS'))
check('apply left the ledger data file byte-untouched', sha256(dataLed) === dataShaBefore)

const rb = run(['rollback', '--root', root])
check('rollback restores old package.json version', rb.status === 0 && JSON.parse(readFileSync(sandboxPkgPath, 'utf8')).version === '0.0.1-oldface')
check('rollback restores cordis.patch.yml byte-identical', sha256(path.join(root, 'cordis.patch.yml')) === patchShaBefore)
check('rollback leaves ledger data byte-identical', sha256(dataLed) === dataShaBefore)

// --- 5. incompatibility is fail-loud (version pillar) ------------------------
const badPkg = path.join(tmp0, 'badface', 'package.json')
mkdirSync(path.dirname(badPkg), { recursive: true })
const bp = JSON.parse(readFileSync(path.join(HERE, 'package.json'), 'utf8'))
bp.engines = { ...bp.engines, node: '>=99' }
writeFileSync(badPkg, JSON.stringify(bp, null, 2))
const ap2 = run(['apply', '--src', path.dirname(badPkg), '--root', root])
check('apply refuses incompatible engines.node (exit 2 · no install)', ap2.status === 2 && ap2.stderr.includes('refusing'))
check('refused apply still restored the code face (rollback on fail)', JSON.parse(readFileSync(sandboxPkgPath, 'utf8')).version === '0.0.1-oldface')

rmSync(tmp0, { recursive: true, force: true })
console.log(`\nupdate/upgrade path: ${failures === 0 ? 'ALL PASS' : failures + ' check(s) failed'}`)
process.exit(failures === 0 ? 0 : 1)
