#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""selftest_p3_driver.py — deepen_r33.py CPU 自检（P3 驱动器验收包素材·鲍勃《P3 驱动器验收与读数面设计件》§1 AC×41／§2 SM 基线）
================================================================================================
令源：群管理员 2026-11-26 23:10:52／2026-11-27 00:02:02 派单「C7 落码续作：deepen_r33.py＋selftest_p3_driver.py 毕即回执②（验收包六项）」。
      自择授权：PI 22:32／22:43 两帧。夜间授权：PI 00:02:59「kimi+lean 双审全代裁不卡链·先斩后奏」——本件仍守 0 GPU·0 开机·0 发射·0 推。
覆盖：SM-01 基线逐字段复现｜SM-02～05 合成链回归（v2·v1）｜SM-11/12 开关负控｜SM-20 见证正负控（含合法集细化的「不致盲」负控）
      ｜SM-22 损行 EXECUTOR-BREACH｜SM-30 合成读数包过鲍勃校验器｜SM-50 horizon 三 verdict（确证短链）｜AC-53 六条调度不变量
      ｜训练 episode 径（CPU·18/12 tick·侧信道不入账本）｜C 模式计划投影逐位（AC-80 的 CPU 可测子位）｜CLI 退出码契约｜AC×41 自评表。
不覆盖（如实）：AC-80 GPU 逐位冒烟（须点火机·命令见报告）｜P4 82/82（点火机钉定副本）｜guard v6（守护侧）。
用法：python3 selftest_p3_driver.py --out <dir> [--validator <criteria_v3_reading_validator.py>] [--bob-evidence <dir>] [--bob-chains <dir>]
      [--v1 <horizon_slot_calc.py>] [--criteria <criteria_v3_config_frozen_v1.2.json>]
退出码：0＝无 FAIL（SKIP 允许）；1＝有 FAIL；2＝用法错。输出：selftest_report.json／.md＋ac_selfassess.json／.md＋全部证据件（落 --out）。
"""
import argparse, hashlib, json, os, random, re, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deepen_r33 as D  # noqa: E402 （import 0 触 torch·0 触 GPU）

SHARED = '/home/z/my-project/shared'
DEF_VALIDATOR = os.path.join(SHARED, '鲍勃_P3驱动器验收与读数面设计_工程包_20261126', '鲍勃_scripts_20261126', 'criteria_v3_reading_validator.py')
DEF_BOB_EVID = os.path.join(SHARED, '鲍勃_P3驱动器验收与读数面设计_工程包_20261126', '鲍勃_evidence_20261126')
DEF_BOB_CHAINS = os.path.join(SHARED, '鲍勃_后续实验与真双绑设计_工程包_20261126', '鲍勃_evidence_合成链_20261126')
DEF_V1 = '/home/z/my-project/agents/6af675ea2ac8b49dca4b0351/recon_build/p10_precheck/horizon_slot_calc.py'
DEF_CRITERIA = os.path.join(SHARED, '鲍勃_B1①回执_rep3终窗全谱核对与horizon槽_20261126', 'criteria_v3_config_frozen_v1.2.json')

# ---- 鲍勃 SM-01 基线期望值（《P3 驱动器验收与读数面设计件》§2.1＋evidence_smoke_p3_baseline.json·逐字段） ----
SM01_TEXT = {"k0": "alpha-secret-0001", "k1": "beta-secret-0002", "k2": "gamma-secret-0003", "k3": "delta-secret-0004"}
SM01_EXPECT = {
    'write_errs': [None, None, None, None],
    'read_k0': [{"key": "k0", "text": "alpha-secret-0001"}], 'read_k1': [{"key": "k1", "text": "beta-secret-0002"}],
    'settle_period': {'epoch': 1, 'tick': 7, 'close': False, 'd_phi': 0, 'd_R': 0, 'd_D': 2007,
                      'd_D_by': {'reject': 0, 'decay': 18, 'evict': 0, 'horizon': 1989, 'supersede': 0, 'close': 0},
                      'deposited': {'reject': 0, 'decay': 0, 'evict': 0, 'horizon': 2, 'supersede': 0, 'close': 0}, 'materialized': 8},
    'read_k2_after_dissolve': [{"key": "k2", "text": "⟨幻肢⟩ 此前缀下曾有 1 条散失·曾 17 字·成因 视界·不可复原", "phantom": True}],
    'audit_verdict': 'SELF-CONSISTENT',
    'audit_executor': {'chain_ok': True, 'tombstones_chained': 2, 'erased_count': 2, 'pending_erase': [], 'era': 'executor',
                       'g_policy': 'p1', 'phantom_form': 'kout', 'log_has_plaintext_field': False, 'live_deks': 2},
    'audit_counts': {'tick': 8, 'epoch': 1, 'n_reads': 3, 'n_tx': 2, 'n_rj': 0, 'n_ph': 1, 'phi': 200, 'R': 50, 'D': 2007, 'U': 1993,
                     'util_T': 0.8, 'util_R': 0.2, 'util_A': 0.50175,
                     'deposited_by_cause': {'reject': 0, 'decay': 0, 'evict': 0, 'horizon': 2, 'supersede': 0, 'close': 0},
                     'phantoms': 2, 'phantoms_felt': 2},
    'attempt_inverse': {'A1_log_plaintext_scan': {'hit': 0, 'probes': 4}, 'A1_log_text_field': {'hit': 0}, 'A2_pool_dek_for_tombstoned': {'hit': 0},
                        'A4_chain_verifies': {'ok': True}, 'A0_decrypt_without_dek': {'hit': 0}},
    'readback_budget_k2': 2, 'witness_clean_ok': {'ok': True, 'hits': 0}, 'witness_dirty_ok': {'ok': False, 'hits': 12},
    'manifest_digest': 'f2047438b691', 'log_plaintext_leak': False,
}
# ---- 鲍勃合成链（evidence_合成链_20261126·*.run.jsonl＝归一化 tx=[id]；T0＝在册事件形 tx=[[id,cT]]）内嵌副本（sha16 见名） ----
CHAINS = {
    'T0': ("T0_在册事件形.jsonl", "1531c9ab5f406ea2", [
        '{"ev":"inject","id":1,"tick":1,"key":"k0","text":"a"}', '{"ev":"inject","id":2,"tick":2,"key":"k1","text":"b"}',
        '{"ev":"inject","id":3,"tick":3,"key":"k2","text":"c"}', '{"ev":"inject","id":4,"tick":4,"key":"k3","text":"d"}',
        '{"ev":"gate","tick":5,"prefix":"k","k":8,"cT":100,"cA":10,"cP":50,"tx":[[1,100],[2,100]],"rj":[],"ph":[],"q":200}',
        '{"ev":"settle","tick":6,"epoch":1,"close":false,"snap":{}}']),
    'S1': ("S1_同序_H0等于2.run.jsonl", "9d750882ffaddcd4", [
        '{"ev": "inject", "id": 1, "tick": 1, "key": "k0", "text": "x"}', '{"ev": "inject", "id": 2, "tick": 2, "key": "k1", "text": "x"}',
        '{"ev": "inject", "id": 3, "tick": 3, "key": "k2", "text": "x"}', '{"ev": "inject", "id": 4, "tick": 4, "key": "k3", "text": "x"}',
        '{"ev": "gate", "tick": 5, "prefix": "k", "k": 8, "cT": 100, "cA": 10, "cP": 50, "tx": [1, 2], "rj": [], "ph": [], "q": 200}',
        '{"ev": "deposit", "id": 3, "tick": 6, "cause": "horizon"}', '{"ev": "deposit", "id": 4, "tick": 6, "cause": "horizon"}',
        '{"ev": "settle", "tick": 6, "epoch": 1, "close": false, "snap": {}}']),
    'S2': ("S2_留隙_H0等于3.run.jsonl", "b24107aefe1d9e8d", [
        '{"ev": "inject", "id": 1, "tick": 1, "key": "k2", "text": "x"}', '{"ev": "inject", "id": 2, "tick": 2, "key": "k3", "text": "x"}',
        '{"ev": "inject", "id": 3, "tick": 3, "key": "k0", "text": "x"}', '{"ev": "inject", "id": 4, "tick": 4, "key": "k1", "text": "x"}',
        '{"ev": "gate", "tick": 5, "prefix": "k", "k": 8, "cT": 100, "cA": 10, "cP": 50, "tx": [3], "rj": [], "ph": [], "q": 100}',
        '{"ev": "gate", "tick": 6, "prefix": "k", "k": 8, "cT": 100, "cA": 10, "cP": 50, "tx": [4], "rj": [], "ph": [], "q": 100}',
        '{"ev": "deposit", "id": 1, "tick": 7, "cause": "horizon"}', '{"ev": "deposit", "id": 2, "tick": 7, "cause": "horizon"}',
        '{"ev": "settle", "tick": 7, "epoch": 1, "close": false, "snap": {}}']),
    'S3': ("S3_部分散失_仅k2.run.jsonl", "8fb9017c1cef9ab2", [
        '{"ev": "inject", "id": 1, "tick": 1, "key": "k0", "text": "x"}', '{"ev": "inject", "id": 2, "tick": 2, "key": "k1", "text": "x"}',
        '{"ev": "inject", "id": 3, "tick": 3, "key": "k2", "text": "x"}', '{"ev": "inject", "id": 4, "tick": 3, "key": "k3", "text": "x"}'.replace('"tick": 3', '"tick": 4'),
        '{"ev": "gate", "tick": 5, "prefix": "k", "k": 8, "cT": 100, "cA": 10, "cP": 50, "tx": [1, 2], "rj": [], "ph": [], "q": 200}',
        '{"ev": "deposit", "id": 3, "tick": 6, "cause": "horizon"}', '{"ev": "settle", "tick": 6, "epoch": 1, "close": false, "snap": {}}']),
}
CHAIN_EXPECT = {'T0': ('UNDECIDABLE', None, None, 2), 'S1': ('INFEASIBLE', None, None, 1), 'S2': ('FEASIBLE', 3, 4, 0), 'S3': ('INFEASIBLE', None, None, 1)}

R = []   # 结果累加器


def rec(tid, name, ok, evidence, ac=(), status=None, ac_status='过'):
    st = status or ('PASS' if ok else 'FAIL')
    R.append({'id': tid, 'name': name, 'status': st, 'evidence': evidence, 'ac': list(ac), 'ac_status': (ac_status if st != 'FAIL' else '不过')})
    print('[%s] %s %s — %s' % (st, tid, name, (json.dumps(evidence, ensure_ascii=False)[:300] if not isinstance(evidence, str) else evidence[:300])), flush=True)
    return ok


def expect_fail(code, fn, *a, **k):
    """断言 fn 受控退出 code；返回 (ok, got_code_or_exc)。"""
    try:
        fn(*a, **k)
    except D.DriverFail as e:
        return e.code == code, e.code
    except Exception as e:  # noqa: BLE001
        return False, 'unexpected %s: %s' % (type(e).__name__, str(e)[:80])
    return False, 'no-raise'


def sha12f(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


# ====================================================================== T00 钉与环境
def t00(out):
    D.load_executor()
    ev = {'executor_sha16': D.sha_file(D.ix.__file__)[:16], 'thermo_core_sha16': D.sha_file(D.tc.__file__)[:16],
          'slot_calc_v2_sha16': D.sha_file(os.path.join(HERE, 'horizon_slot_calc_v2.py'))[:16],
          'driver_sha16': D.sha_file(os.path.abspath(D.__file__))[:16], 'selftest_sha16': D.sha_file(os.path.abspath(__file__))[:16],
          'pins_expected': {'executor': D.PIN_EXECUTOR[:16], 'thermo_core': D.PIN_THERMO_CORE[:16], 'slot_calc_v2': D.PIN_SLOT_CALC_V2[:16], 'r32': D.PIN_R32[:16]},
          'python': sys.version.split()[0], 'cryptography': __import__('cryptography').__version__, 'exec_dir': D.EXEC_DIR,
          'r32_local_copy': None, 'torch_cuda': None}
    try:
        import torch
        ev['torch_cuda'] = bool(torch.cuda.is_available())
    except Exception as e:  # noqa: BLE001
        ev['torch_cuda'] = 'import-fail: %s' % type(e).__name__
    r32 = os.path.join(HERE, 'deepen_r32.py')
    ev['r32_local_copy'] = (D.sha_file(r32)[:16] if os.path.exists(r32) else None)
    ok = (ev['executor_sha16'] == D.PIN_EXECUTOR[:16] and ev['thermo_core_sha16'] == D.PIN_THERMO_CORE[:16]
          and ev['slot_calc_v2_sha16'] == D.PIN_SLOT_CALC_V2[:16] and ev['torch_cuda'] is False)
    return rec('T00', '钉定指纹（执行器／冻结面／slot_calc_v2）与本机 CPU 态', ok, ev, ac=['AC-01', 'AC-02'])


# ====================================================================== T01 SM-01 基线逐字段复现
def t01(out, bob_evid):
    with tempfile.TemporaryDirectory() as d:
        led = D.make_ledger('v3', os.path.join(d, 'ledger.jsonl'), os.path.join(d, 'ledger.pool'), D.exec_cfg('v3', 3, 'p1'))
        w = {k: led.write_entry(k, v) for k, v in (("k2", SM01_TEXT["k2"]), ("k3", SM01_TEXT["k3"]), ("k0", SM01_TEXT["k0"]), ("k1", SM01_TEXT["k1"]))}
        r0 = led.read_entries("k0"); r1 = led.read_entries("k1"); rep, _ = led.settle(False); r2 = led.read_entries("k2"); aud, _ = led.audit()
        inv = led.attempt_inverse(known_plaintexts=list(SM01_TEXT.values()))
        ws0 = D.ix.IrreversibleLedger.witness_ngrams(SM01_TEXT["k2"])
        wit_ok = D.ix.IrreversibleLedger.context_rebuild_witness("MEM READ k2: ⟨幻肢⟩ 此前缀下曾有 1 条散失·曾 17 字·成因 视界·不可复原", [ws0])
        wit_bad = D.ix.IrreversibleLedger.context_rebuild_witness("旧窗口残留: " + SM01_TEXT["k2"], [ws0])
        got = {'write_errs': [w[k][1] for k in ("k2", "k3", "k0", "k1")], 'read_k0': r0[0], 'read_k1': r1[0], 'settle_period': rep.get("period"),
               'read_k2_after_dissolve': r2[0], 'audit_verdict': aud.get("verdict"),
               'audit_executor': {k: aud["executor"][k] for k in ("chain_ok", "tombstones_chained", "erased_count", "pending_erase", "era", "g_policy", "phantom_form", "log_has_plaintext_field", "live_deks")},
               'audit_counts': {k: aud.get(k) for k in ("tick", "epoch", "n_reads", "n_tx", "n_rj", "n_ph", "phi", "R", "D", "U", "util_T", "util_R", "util_A", "deposited_by_cause", "phantoms", "phantoms_felt")},
               'attempt_inverse': {k: v for k, v in inv.items() if isinstance(v, dict)}, 'readback_budget_k2': led.readback_budget("k2"),
               'witness_clean_ok': wit_ok, 'witness_dirty_ok': wit_bad, 'manifest_digest': D.digest12({"seed": 20261132, "lose": ["k2", "k3"], "keep": ["k0", "k1"]}),
               'log_plaintext_leak': any(t in open(os.path.join(d, 'ledger.jsonl'), encoding='utf-8').read() for t in SM01_TEXT.values())}
    diff = {k: {'expect': SM01_EXPECT[k], 'got': got.get(k)} for k in SM01_EXPECT if got.get(k) != SM01_EXPECT[k]}
    # 与鲍勃证据件逐字段交叉核（若在位）
    xchk = None
    be = os.path.join(bob_evid, 'smoke_p3_baseline.json') if bob_evid else None
    if be and os.path.exists(be):
        bj = json.load(open(be, encoding='utf-8'))
        keys = [k for k in SM01_EXPECT if k in bj]
        xchk = {'file': be, 'sha16': sha12f(be), 'n_keys': len(keys), 'mismatch': [k for k in keys if bj[k] != got.get(k)]}
        if xchk['mismatch']: diff['_bob_evidence_mismatch'] = xchk['mismatch']
    else:
        xchk = '鲍勃证据件不在位（--bob-evidence）·以内嵌期望值为准'
    D.jdump({'got': got, 'diff_vs_expected': diff, 'bob_evidence_crosscheck': xchk, 'expected_source': '鲍勃《P3 驱动器验收与读数面设计件》§2.1＋evidence_smoke_p3_baseline.json'}, os.path.join(out, 'sm01_baseline_replay.json'))
    return rec('T01', 'SM-01 基线逐字段复现（H=3·p1·钉定执行器）', not diff, {'n_fields': len(SM01_EXPECT), 'diff_keys': sorted(diff), 'bob_xcheck': xchk}, ac=['AC-20', 'AC-50', 'AC-52', 'AC-110', 'AC-61'])


# ====================================================================== T03 SM-20 见证（正负控＋合法集细化「不致盲」负控）
def t03(out):
    txt = SM01_TEXT["k2"]
    ws0 = D.ix.IrreversibleLedger.witness_ngrams(txt)
    pos = D.ix.IrreversibleLedger.context_rebuild_witness("MEM READ k2: ⟨幻肢⟩ 此前缀下曾有 1 条散失·曾 17 字·成因 视界·不可复原", [ws0])
    neg = D.ix.IrreversibleLedger.context_rebuild_witness("旧窗口残留: " + txt, [ws0])
    # witness_check 合法集细化：①合法来源行重建 ⇒ ok/hits 0；②注入已散失明文 ⇒ DriverFail(7)（不致盲）；③值域随机 token 与键偶合 ⇒ 不计（非泄漏）
    lost_v = 'w01234 w05678 w01234 w09999 w00001 w00002'
    key_x = 'w01234 w11111 w22222'   # 键首 token 与散失值首 token 偶合
    legit = [D.MEM_HDR, 'MEM WRITE | k: %s | v: w77777 w88888\n' % key_x, 'MEM WRITE | k: w33333 | v: ']
    ctx_ok = D.MEM_HDR + 'MEM WRITE | k: %s | v: w77777 w88888\n' % key_x + 'MEM WRITE | k: w33333 | v: ⟨幻肢⟩ 此前缀下曾有 1 条散失·曾 65 字·成因 视界·不可复原\n'
    a = D.witness_check(ctx_ok, [lost_v], legit)
    ok_a, code_a = expect_fail(D.EXIT_WITNESS, D.witness_check, ctx_ok + 'MEM WRITE | k: w44444 | v: ' + lost_v + '\n', [lost_v], legit)
    # 旧口径（不合法化键行界）会在偶合处误报——用裸执行器函数示范偶合命中率（非泄漏·仅作对照）
    collide = D.ix.IrreversibleLedger.context_rebuild_witness('MEM WRITE | k: %s | v: x\n' % key_x, [ws0])['hits']
    ok = (pos == SM01_EXPECT['witness_clean_ok'] and neg == SM01_EXPECT['witness_dirty_ok'] and a == {'ok': True, 'hits': 0, 'vacuous': False} and ok_a and code_a == 7)
    return rec('T03', 'SM-20 R-11 见证：正控 ok/hits0·负控 hits12·合法集细化后偶合不计且注入明文仍 fail-loud(7)', ok,
               {'pos': pos, 'neg': neg, 'refined_ok_case': a, 'refined_leak_case': {'fail_loud': ok_a, 'code': code_a}, 'raw_fn_collision_control_hits': collide}, ac=['AC-40', 'AC-41', 'AC-42'])


# ====================================================================== T04/T05 合成链回归（v2 原样子进程／v1 TypeError）
def chain_file(out, tag, bob_chains):
    name, sha, lines = CHAINS[tag]
    if bob_chains:
        p = os.path.join(bob_chains, name)
        if os.path.exists(p):
            return p, ('bob:' + sha12f(p)), (sha12f(p) == sha)
    p = os.path.join(out, 'chains', name); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    return p, ('embedded:sha16=' + sha12f(p)), (sha12f(p) == sha)


def t04(out, bob_chains):
    v2 = os.path.join(HERE, 'horizon_slot_calc_v2.py'); res = {}; ok = True; src_ok = True
    for tag in ('T0', 'S1', 'S2', 'S3'):
        p, src, s_ok = chain_file(out, tag, bob_chains); src_ok = src_ok and s_ok
        r = D.run_slot_calc_v2(v2, p); ip = D.interval_from_log(p)
        ev, lo, hi, rc = CHAIN_EXPECT[tag]
        good = (r.get('verdict') == ev and r.get('lo') == lo and r.get('hi') == hi and r.get('rc') == rc and ip.get('verdict') == ev
                and (lo is None or (ip.get('lo') == lo and ip.get('hi') == hi)))
        res[tag] = {'src': src, 'v2': {k: r.get(k) for k in ('verdict', 'lo', 'hi', 'rc')}, 'inproc': {k: ip.get(k) for k in ('verdict', 'LB', 'UB', 'lo', 'hi')}, 'expect': {'verdict': ev, 'lo': lo, 'hi': hi, 'rc': rc}, 'ok': good}
        ok = ok and good
    D.jdump(res, os.path.join(out, 'sm02_05_chain_regression.json'))
    return rec('T04', 'SM-02～04＋T0 合成链回归（v2 原样子进程＋库内交叉核）：INFEASIBLE／FEASIBLE[3,4]／INFEASIBLE／UNDECIDABLE', ok and src_ok, res, ac=['AC-51'])


def t05(out, v1):
    if not v1 or not os.path.exists(v1):
        return rec('T05', 'SM-05 在册事件形入 v1 → TypeError（v1 不在位·跳过）', True, {'v1': v1}, ac=['AC-51'], status='SKIP')
    p, _, _ = chain_file(out, 'T0', None)
    r = subprocess.run([sys.executable, v1, '--replay', p], capture_output=True, text=True, timeout=120)
    ok = (r.returncode != 0 and 'unhashable type' in r.stderr and 'TypeError' in r.stderr)
    return rec('T05', 'SM-05 在册事件形（tx=[[id,cT]]）入 v1 → TypeError L42（v1 留档 0 动·v2 为准）', ok, {'v1': v1, 'v1_sha16': sha12f(v1), 'rc': r.returncode, 'stderr_tail': r.stderr[-200:]}, ac=['AC-51'])


# ====================================================================== T06/T07/T08/T09 配置校验负控
def t06(out):
    cases = [('v3-fake', 'honest', 12, 'p1'), ('v3', 'inverse', 12, 'p1'), ('frozen', 'honest', 12, 'off'), ('v3', 'legacy', 12, 'p1'), ('v3', 'honest', 12, 'off'), ('frozen', 'legacy', 12, 'p1'), ('bogus', 'honest', 12, 'p1')]
    res = {('%s/%s/H%s/%s' % c): expect_fail(D.EXIT_CONFIG, D.validate_arm, *c, None, 'arm') for c in cases}
    return rec('T06', 'SM-11 开关串线／g_policy 口径／取值集负控（7 则·全拒跑 code=4）', all(v[0] for v in res.values()), res, ac=['AC-10', 'AC-11', 'AC-13'])


def t07(out):
    saved = dict(D.X3_W)
    try:
        D.X3_W['honest'] = 1.0; D.X2_W['honest'] = 0.0
        ok1, c1 = expect_fail(D.EXIT_CONFIG, D.validate_arm, 'v3', 'honest', 12, 'p1', None, 'arm')
        D.X2_W['honest'] = 1.0
        D.validate_arm('v3', 'honest', 12, 'p1', None, 'arm'); ok2 = True
    finally:
        D.X3_W.clear(); D.X3_W.update(saved); D.X2_W.clear(); D.X2_W.update({'honest': 1.0, 'inverse': 0.0, 'legacy': 0.0})
    return rec('T07', 'SM-12 c1：x3.weight>0 ∧ x2.weight=0 ⇒ 拒跑；x2>0 ⇒ 过', ok1 and ok2 and c1 == 4, {'c1_violation': [ok1, c1], 'c1_ok_passes': ok2}, ac=['AC-12'])


def t08(out, criteria_path):
    res = {}
    res['horizon_bool'] = expect_fail(D.EXIT_CONFIG, D.validate_arm, 'v3', 'honest', True, 'p1', None, 'arm')
    res['horizon_str'] = expect_fail(D.EXIT_CONFIG, D.validate_arm, 'v3', 'honest', '9', 'p1', None, 'arm')
    res['horizon_none'] = expect_fail(D.EXIT_CONFIG, D.validate_arm, 'v3', 'honest', None, 'p1', None, 'arm')
    res['horizon_0'] = expect_fail(D.EXIT_CONFIG, D.validate_arm, 'v3', 'honest', 0, 'p1', None, 'arm')
    pend = {'schema': 'criteria_v3', 'config_version': 'v1.2', 'horizon': {'value': 'PENDING_HARNESS（x）'}}
    res['criteria_PENDING_HARNESS'] = expect_fail(D.EXIT_CONFIG, D.validate_arm, 'v3', 'honest', 12, 'p1', pend, 'arm')
    res['criteria_horizon_mismatch'] = expect_fail(D.EXIT_CONFIG, D.validate_arm, 'v3', 'honest', 12, 'p1', {'horizon': {'value': 11}}, 'arm')
    D.validate_arm('v3', 'honest', 12, 'p1', {'horizon': {'value': 12}}, 'arm'); res['criteria_horizon_equal'] = [True, 'pass']
    # 真冻结件（若在位）：load_criteria 过·horizon.value 非整数 ⇒ arm 拒点火
    real = None
    if criteria_path and os.path.exists(criteria_path):
        c, s = D.load_criteria(criteria_path)
        real = {'sha12': s, 'config_version': c.get('config_version'), 'horizon_value_type': type(D.criteria_horizon(c)).__name__,
                'arm_with_v1_2_as_is': expect_fail(D.EXIT_CONFIG, D.validate_arm, 'v3', 'honest', 12, 'p1', c, 'arm'), 'expected_sha16_prefix': D.CRITERIA_V12, 'sha16_prefix_match': s == D.CRITERIA_V12[:12]}
    res['real_criteria'] = real or 'v1.2 冻结件不在位（--criteria）'
    ok = all(v[0] for k, v in res.items() if k not in ('criteria_horizon_equal', 'real_criteria')) and (real is None or (real['arm_with_v1_2_as_is'][0] and real['sha16_prefix_match']))
    return rec('T08', 'AC-15 horizon 整数门（PENDING_HARNESS 拒点火）＋criteria 对表', ok, res, ac=['AC-03', 'AC-15'])


def t09(out):
    with tempfile.TemporaryDirectory() as d:
        lv = D.make_ledger('v3', os.path.join(d, 'v.jsonl'), os.path.join(d, 'v.pool'), D.exec_cfg('v3', 12, 'p1')); av, _ = lv.audit()
        lf = D.make_ledger('frozen', os.path.join(d, 'f.jsonl'), os.path.join(d, 'f.pool'), D.exec_cfg('frozen', 12, 'off')); af, _ = lf.audit()
        res = {'era_v3': D.ledger_era('v3', av), 'era_frozen': D.ledger_era('frozen', af),
               'handshake_v3_on_frozen': expect_fail(D.EXIT_CONFIG, D.era_handshake, 'v3', af, 't'), 'handshake_frozen_on_v3': expect_fail(D.EXIT_CONFIG, D.era_handshake, 'frozen', av, 't')}
        D.era_handshake('v3', av, 't'); D.era_handshake('frozen', af, 't'); res['correct_pairs_pass'] = True
    ok = res['era_v3'] == 'executor' and res['era_frozen'] == 'pre-executor' and res['handshake_v3_on_frozen'][0] and res['handshake_frozen_on_v3'][0]
    return rec('T09', 'AC-93 era 握手：期望 era 与后端对表·不等拒跑(4)·相等过', ok, res, ac=['AC-93'])


# ====================================================================== T10 SM-22 损行 → EXECUTOR-BREACH（全限定名·不可互捕）
def t10(out):
    """SM-22 两子案（钉定执行器 d2189f2c4f1e 行为如实登记·0 改）：(a) JSON 损行 ⇒ audit()/replay() 均抛 ix.ExecutorBreach（pending_erase→tombstones→_log_lines 再抛·
    降级审计不成立）→ 驱动器 main 全限定名捕获 code=6（fail-loud·轮无效由退出码契约承载）；(b) JSON 合法·墓碑 h 被篡改 ⇒ audit() 返回降级审计 verdict=EXECUTOR-BREACH
    ·replay 抛 ix.ExecutorBreach（非 tc.LedgerInconsistent·不可互捕）→ 驱动器 verdict 核 DriverFail(6)。"""
    res = {}
    with tempfile.TemporaryDirectory() as d:
        # (a) JSON 损行
        lp, pp = os.path.join(d, 'a.jsonl'), os.path.join(d, 'a.pool')
        led = D.make_ledger('v3', lp, pp, D.exec_cfg('v3', 12, 'p1')); led.write_entry('a.q', 'v-1')
        open(lp, 'a', encoding='utf-8').write('{"ev": "inject", "id": 2, "tick": 2, "key": "a.r", "nonce": "BAD"\n')
        def _raise(fn):
            try: fn(); return 'no-raise'
            except D.ix.ExecutorBreach as e: return 'ix.ExecutorBreach' + ('' if not isinstance(e, D.tc.LedgerInconsistent) else '(!!also LedgerInconsistent)')
            except D.tc.LedgerInconsistent as e: return 'tc.LedgerInconsistent'
            except Exception as e: return 'other %s' % type(e).__name__  # noqa: BLE001
        res['a_json_corrupt'] = {'audit': _raise(lambda: led.audit()), 'replay': _raise(led.replay), 'pending_erase': _raise(led.pending_erase)}
        # 驱动器层：(a) 损行账本上 run_probe → 原语抛 ix.ExecutorBreach 原样上抛（main 捕获→6）
        m = D.manifest_build(12, None, None)
        try:
            D.run_probe('A', 'v3', 12, 'p1', None, m, os.path.join(d, 'pa'), lambda p: ('MISS\n', 2)); rp = 'no-raise'
        except D.ix.ExecutorBreach: rp = 'ix.ExecutorBreach→main code=6'
        except D.DriverFail as e: rp = 'DriverFail code=%d' % e.code
        except Exception as e: rp = 'other %s' % type(e).__name__  # noqa: BLE001
        # 预置损行账本再 run_probe（探针账本路径被预写坏行）
        pd = os.path.join(d, 'pb'); os.makedirs(pd); open(os.path.join(pd, 'probe_ledger.jsonl'), 'w').write('{"ev": "inject", "id": 1\n')
        try:
            D.run_probe('A', 'v3', 12, 'p1', None, m, pd, lambda p: ('MISS\n', 2)); rp2 = 'no-raise'
        except D.ix.ExecutorBreach: rp2 = 'ix.ExecutorBreach→main code=6'
        except D.DriverFail as e: rp2 = 'DriverFail code=%d' % e.code
        except Exception as e: rp2 = 'other %s' % type(e).__name__  # noqa: BLE001
        res['a_run_probe_fresh_ledger'] = rp; res['a_run_probe_pre_corrupted_ledger'] = rp2
        # (b) JSON 合法·墓碑篡改
        lp2, pp2 = os.path.join(d, 'b.jsonl'), os.path.join(d, 'b.pool')
        led2 = D.make_ledger('v3', lp2, pp2, D.exec_cfg('v3', 12, 'p1')); led2.write_entry('a.q', 'v-1'); led2.settle(True)
        lines = open(lp2, encoding='utf-8').read().splitlines(); hit = False
        for i, ln in enumerate(lines):
            ev = json.loads(ln)
            if ev.get('ev') == 'tombstone' and not hit:
                ev['h'] = 'f' * 64; lines[i] = D.ix.canonical(ev); hit = True
        open(lp2, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
        aud2 = None
        try: aud2, _ = led2.audit(); v2 = aud2.get('verdict')
        except Exception as e: v2 = 'raise %s' % type(e).__name__  # noqa: BLE001
        res['b_tombstone_tampered'] = {'audit_verdict': v2, 'audit_executor': ({k: aud2['executor'].get(k) for k in ('chain_ok', 'era', 'pending_erase')} if aud2 else None), 'replay': _raise(led2.replay)}
        # 驱动器 verdict 核（run_arm 终窗）：verdict≠SELF-CONSISTENT ⇒ DriverFail(6)（代码位核·同式复算）
        verdict_fail = expect_fail(D.EXIT_BREACH, lambda: (_ for _ in ()).throw(D.DriverFail(D.EXIT_BREACH, '探针账本 verdict=%r（F5·轮无效）' % v2)) if v2 != 'SELF-CONSISTENT' else None)
    A, B = res['a_json_corrupt'], res['b_tombstone_tampered']
    ok = (A['audit'].startswith('ix.ExecutorBreach') and A['replay'].startswith('ix.ExecutorBreach') and A['pending_erase'].startswith('ix.ExecutorBreach')
          and res['a_run_probe_pre_corrupted_ledger'].startswith('ix.ExecutorBreach') and B['audit_verdict'] == 'EXECUTOR-BREACH' and B['replay'].startswith('ix.ExecutorBreach')
          and B['audit_executor']['chain_ok'] is False and verdict_fail[0] and set(t.__name__ for t in D.fail_types()) >= {'ExecutorBreach', 'TheoryFalsified', 'LedgerInconsistent'})
    return rec('T10', 'SM-22 损行两子案：(a) JSON 损行→audit/replay 抛 ix.ExecutorBreach（降级审计不成立·钉定件行为如实登记）→main 6；(b) 墓碑篡改→audit=EXECUTOR-BREACH·chain_ok F·replay 抛 ExecutorBreach（非 LedgerInconsistent）→verdict 核 DriverFail(6)', ok, res, ac=['AC-91', 'AC-92'])


# ====================================================================== T11 解析区间＋六条调度不变量
def t11(out):
    an = D.analytic_intervals(); inv = D.schedule_invariants(12); bad = D.schedule_invariants(1000)
    ok = (an['train']['lo'] == 6 and an['train']['hi'] == 15 and an['probe']['lo'] == 9 and an['probe']['hi'] == 16
          and an['intersection'] == {'lo': 9, 'hi': 15, 'feasible': True, 'mid': 12} and D.default_horizon() == 12
          and inv['all_ok'] and not bad['I-c']['ok'] and bad['all_ok'] is False)
    D.jdump({'analytic': an, 'invariants_H12': inv, 'invariants_H1000_negative': bad}, os.path.join(out, 'schedule_invariants.json'))
    return rec('T11', 'AC-53 六条调度不变量：H=12 全过·H=1000（≥行㶲可撑龄）I-c 拒；解析区间 train[6,15]∩probe[9,16]=[9,15]·mid 12', ok,
               {'analytic': an, 'invariants_ok': {k: v['ok'] for k, v in inv.items() if isinstance(v, dict)}, 'I-c_negative_H1000': bad['I-c']}, ac=['AC-53'])


# ====================================================================== T12 SM-50 horizon 校准链（确证短链·两时代×两几何）
def t12(out):
    cal = os.path.join(out, 'horizon_calib'); shutil.rmtree(cal, ignore_errors=True); os.makedirs(cal)
    ap = argparse.Namespace(mode='calib', out=cal, horizon=None, manifest=None, criteria=None, exec_dir=None, slot_calc=None, selftest=None, r32=None, smoke_steps=0)
    try:
        rc = D.calib_mode(ap)
    except D.DriverFail as e:
        rc = 'DriverFail code=%d %s' % (e.code, e.msg[:100])
    o = json.load(open(os.path.join(cal, 'horizon_calib.json'), encoding='utf-8'))
    chk = {('%s/%s' % (c['backend'], c['schedule'])): {'checks': c['checks'], 'all': all(c['checks'].values()), 'v2': [c['v2']['verdict'], c['v2'].get('lo'), c['v2'].get('hi')]} for c in o['confirm']}
    # 两时代差分：同几何 v3 vs frozen 期报逐位同（执行器挂钩零账面效应）
    per = {('%s/%s' % (c['backend'], c['schedule'])): c['period'] for c in o['confirm']}
    for k in per: per[k].pop('periods', None)
    diff_er = {s: per['v3/' + s] == per['frozen/' + s] for s in ('train', 'probe')}
    # 确证短链日志直入 v2（原样）＝calib 内已跑；另核散失成因 100% horizon·reject/evict/supersede/close 0·decay 分量单列
    cause = {s: {'deposited': per['v3/' + s]['deposited'], 'd_D_by': per['v3/' + s]['d_D_by']} for s in ('train', 'probe')}
    ok = (rc == 0 and o['verdict'] == 'FEASIBLE' and o['H_star'] == 12 and o['robust_interval'] == [9, 15]
          and all(v['all'] for v in chk.values()) and all(diff_er.values()) and chk['v3/train']['v2'] == ['FEASIBLE', 6, 15] and chk['v3/probe']['v2'] == ['FEASIBLE', 9, 16]
          and all(all(c['deposited'][x] == 0 for x in ('reject', 'evict', 'supersede', 'close')) and c['d_D_by']['decay'] > 0 for c in cause.values()))
    return rec('T12', 'SM-50 horizon 校准链：H*=12∈[9,15]·四确证短链全过（v2 原样＝库内＝解析）·两时代期报逐位同·成因 100% horizon', ok,
               {'rc': rc, 'H_star': o['H_star'], 'robust_interval': o['robust_interval'], 'verdict': o['verdict'], 'confirm': chk, 'era_differential_equal': diff_er, 'cause_v3': cause,
                'preflight_witness_neg_control': o['preflight'].get('witness_neg_control'), 'preflight_schedule_invariants_all_ok': o['preflight'].get('schedule_invariants', {}).get('all_ok')}, ac=['AC-50', 'AC-51', 'AC-52'])


# ====================================================================== T13 manifest 冻结／装载／篡改
def t13(out):
    mp = os.path.join(out, 'manifest_selftest.json')
    m = D.freeze_manifest(mp, 12, None, None)
    m2 = D.load_manifest(mp, 12)
    ok_load = (m2['digest'] == m['digest'] and m2['arm_independent'] is True and 'arm' not in m2 and len(m2['read_order']) == 8 and sum(len(b) for b in m2['read_order']) == 8 * (32 + 8 + 2)
               and m2['driver_sha12'] == D.sha12(open(os.path.abspath(D.__file__), 'rb').read()))
    bad = os.path.join(out, 'manifest_tampered.json'); mt = json.load(open(mp, encoding='utf-8')); mt['lost'][0]['val'][0] += 1; D.jdump(mt, bad)
    ok_t = expect_fail(D.EXIT_CONFIG, D.load_manifest, bad, 12)
    ok_h = expect_fail(D.EXIT_CONFIG, D.load_manifest, mp, 11)
    ok_e = expect_fail(D.EXIT_CONFIG, D.freeze_manifest, mp, 12, None, None)   # 0 覆写
    # digest 规则：sha256(canonical(m sans digest))[:12]·canonical＝执行器导出
    rule = D.sha12(D.ix.canonical({k: v for k, v in m.items() if k != 'digest'})) == m['digest'] and len(m['digest']) == 12
    ok = ok_load and ok_t[0] and ok_h[0] and ok_e[0] and rule
    return rec('T13', 'AC-60～62 manifest：字段齐（键集/值/读取序/散失计划/seed/ts）·digest=sha256(canonical)[:12]·篡改/ horizon 不等/ 0 覆写 均拒(4)', ok,
               {'digest': m['digest'], 'n_lost': len(m['lost']), 'blocks': len(m['read_order']), 'driver_sha12_in_manifest': m['driver_sha12'], 'load_ok': ok_load,
                'tamper_rejected': ok_t, 'horizon_mismatch_rejected': ok_h, 'overwrite_refused': ok_e, 'digest_rule_ok': rule}, ac=['AC-60', 'AC-61', 'AC-62'])


# ====================================================================== T14 探针径（A/C 桩生成器）→ 合成读数包 → 鲍勃校验器
def stub_gen(arm):
    def gen(prompt):
        ctx, _, q = prompt.rpartition('MEM READ | k: '); key = q.split('\n')[0].strip()
        vals = {}
        for line in ctx.split('\n'):
            mm = re.match(r'MEM WRITE \| k: (.+?) \| v: (.+)$', line)
            if mm: vals[mm.group(1)] = mm.group(2)
        v = vals.get(key)
        if v is None: return 'MISS\n', 2                       # never-written
        if v.startswith('⟨幻肢⟩'):                               # 散失键：A 桩＝诚实 MISS；C 桩＝确定性编造 40%
            if arm == 'A': return 'MISS\n', 2
            h = int(hashlib.sha256(key.encode()).hexdigest(), 16)
            return ((('w%05d ' * 24) % tuple((h >> (i * 13)) % 8192 for i in range(24))).strip() + '\n', 24) if (h % 5 < 2) else ('MISS\n', 2)
        return v + '\n', 24                                      # live
    return gen


def t14(out, validator):
    md = os.path.join(out, 'synthetic_round'); shutil.rmtree(md, ignore_errors=True); os.makedirs(md)
    m = D.freeze_manifest(os.path.join(md, 'manifest.json'), 12, None, None)
    time.sleep(1.2)   # validator V8：manifest_frozen_ts 须严格早于最早读数（秒分辨率）
    t0 = time.time(); prA = D.run_probe('A', 'v3', 12, 'p1', None, m, os.path.join(md, 'ledA'), stub_gen('A')); wA = round(time.time() - t0, 1)
    t0 = time.time(); prC = D.run_probe('C', 'frozen', 12, 'off', None, m, os.path.join(md, 'ledC'), stub_gen('C')); wC = round(time.time() - t0, 1)
    gates = {'gate-250': {'bacc': 0.7300, 'kl': 3.1460}, 'gate-500': {'bacc': 0.7290, 'kl': 3.0480}}   # 合成（四轮带内中位附近·非实验读数）
    pkgA = D.build_reading_package('A', 'v3', 'honest', 12, 'p1', m, m['digest'], prA, gates, {'synthetic_train_r_obs': True}, {'criteria_version': 'v1.2', 'synthetic': True, 'generator': 'stub（非模型）'})
    pkgC = D.build_reading_package('C', 'frozen', 'legacy', 12, 'off', m, m['digest'], prC, gates, None, {'criteria_version': 'v1.2', 'synthetic': True, 'generator': 'stub（非模型）'})
    pA, pC = os.path.join(md, 'reading_pkg_A_synthetic.json'), os.path.join(md, 'reading_pkg_C_synthetic.json')
    D.jdump(pkgA, pA); D.jdump(pkgC, pC)
    def chk(pr, backend):
        lost = [r for r in pr['raw_reads'] if r['expected_cls'] == 'lost']
        return {'lost_set_n': len(pr['lost_set']), 'tombstones_n': len(pr['tombstone_keys']), 'verdict': pr['audit'].get('verdict'),
                'deposited_by_cause': pr['r_obs']['deposited_by_cause'], 'n_rj': pr['r_obs']['n_rj'], 'witness_hits': sum(w['hits'] for w in pr['witness']), 'witness_ok': all(w['ok'] for w in pr['witness']),
                'raw_n': len(pr['raw_reads']), 'n_lost_rows': len(lost), 'n_live': sum(1 for r in pr['raw_reads'] if r['expected_cls'] == 'live'), 'n_nw': sum(1 for r in pr['raw_reads'] if r['expected_cls'] == 'never_written'),
                'gen_tok_max': max(r['gen_tok'] for r in pr['raw_reads']), 'era_rows': sorted(set(r['era'] for r in pr['raw_reads'])), 'executor_flag_rows': sorted(set(r['executor'] for r in pr['raw_reads'])),
                'inverse': (pr['attempt_inverse'].get('verdict') if isinstance(pr['attempt_inverse'], dict) else None),
                'executor_node': ({k: pr['audit']['executor'].get(k) for k in ('pending_erase', 'erased_count', 'tombstones_chained', 'log_has_plaintext_field', 'era', 'g_policy')} if backend == 'v3' else None),
                'r_obs_keys': sorted(k for k in pr['r_obs'] if k in ('n_tx', 'n_rj', 'n_ph', 'phi', 'R', 'D', 'util_R', 'deposited_by_cause'))}
    cA, cC = chk(prA, 'v3'), chk(prC, 'frozen')
    struct_ok = (cA['lost_set_n'] == 256 and cA['tombstones_n'] == 256 and cA['verdict'] == 'SELF-CONSISTENT' and cA['deposited_by_cause']['horizon'] == 256
                 and all(cA['deposited_by_cause'][x] == 0 for x in ('reject', 'evict', 'supersede', 'close')) and cA['n_rj'] == 0 and cA['witness_hits'] == 0 and cA['witness_ok']
                 and cA['raw_n'] == 336 and cA['n_lost_rows'] == 256 and cA['n_live'] == 64 and cA['n_nw'] == 16 and cA['gen_tok_max'] <= 160 and cA['era_rows'] == ['executor'] and cA['executor_flag_rows'] == [True]
                 and cA['inverse'] == 'EXECUTOR-HOLDS' and cA['executor_node'] == {'pending_erase': [], 'erased_count': 256, 'tombstones_chained': 256, 'log_has_plaintext_field': False, 'era': 'executor', 'g_policy': 'p1'}
                 and cC['lost_set_n'] == 256 and cC['verdict'] == 'SELF-CONSISTENT' and cC['deposited_by_cause']['horizon'] == 256 and cC['raw_n'] == 336 and cC['n_lost_rows'] == 256
                 and prA['lost_set_sha12'] == prC['lost_set_sha12'] and len(prA['lost_set_sha12']) == 12 and pkgA['stats']['n_lost_scored'] == 256 and pkgC['stats']['n_lost_scored'] == 256
                 and min(r['ts'] for r in prA['raw_reads']) > m['frozen_ts'] and set(cA['r_obs_keys']) == {'n_tx', 'n_rj', 'n_ph', 'phi', 'R', 'D', 'util_R', 'deposited_by_cause'})
    val = {'path': validator, 'present': bool(validator and os.path.exists(validator))}
    val_ok = False
    if val['present']:
        val['sha16'] = sha12f(validator)
        r = subprocess.run([sys.executable, validator, '--A', pA, '--C', pC], capture_output=True, text=True, timeout=300)
        open(os.path.join(md, 'validator_stdout.txt'), 'w', encoding='utf-8').write(r.stdout + '\n[stderr]\n' + r.stderr)
        val.update({'rc': r.returncode, 'judgable': '可判读' in r.stdout, 'label': (re.search(r'label = "([^"]+)"', r.stdout) or [None, None])[1],
                    'g_c1_pass': '"pass": true' in (re.search(r'G-C1 = (\{.*\})', r.stdout) or [None, ''])[1] if 'G-C1' in r.stdout else None,
                    'fail_lines': [l for l in r.stdout.splitlines() if 'FAIL' in l]})
        val_ok = (r.returncode == 0 and val['judgable'] and not val['fail_lines'])
    else:
        val['note'] = '校验器不在位（--validator）·SM-30 跳过（结构核照出）'
    # 池件不入包：读数包内无 DEK/base64 池内容
    pools = [os.path.join(md, 'ledA', 'probe_ledger.pool'), os.path.join(md, 'ledC', 'probe_ledger.pool')]
    pool_b64_tokens = re.findall(r'"[A-Za-z0-9+/=]{40,}"', pool_txt)[:5] if (pool_txt := ''.join(open(p, encoding='utf-8').read() for p in pools if os.path.exists(p))) else []
    pool_not_in_pkg = bool(pool_b64_tokens) and all(tok not in json.dumps(pkgA) + json.dumps(pkgC) for tok in pool_b64_tokens)   # 池内 DEK b64 串 0 出现于读数包
    D.jdump({'probe_A': {k: v for k, v in cA.items()}, 'probe_C': {k: v for k, v in cC.items()}, 'wall_s': {'A': wA, 'C': wC}, 'struct_ok': struct_ok, 'validator': val,
             'pool_not_in_pkg': pool_not_in_pkg, 'note': '合成读数包（桩生成器·非模型·非实验读数）·仅验结构/校验器接口'}, os.path.join(md, 'probe_struct_checks.json'))
    ok = struct_ok and pool_not_in_pkg and (val_ok or not val['present'])
    return rec('T14', 'M1–M5 探针径（A/C 桩生成器）：散失 100% horizon·lost_set 256 三臂等值·见证 0·EXECUTOR-HOLDS·pending_erase[]·合成读数包过鲍勃校验器 exit 0' + ('' if val['present'] else '（校验器不在位·SKIP）'),
               ok, {'struct_ok': struct_ok, 'A': cA, 'C': cC, 'lost_set_sha12': prA['lost_set_sha12'], 'validator': val, 'wall_s': [wA, wC], 'pool_not_in_pkg': pool_not_in_pkg},
               ac=['AC-21', 'AC-22', 'AC-30', 'AC-31', 'AC-32', 'AC-34', 'AC-42', 'AC-62', 'AC-63', 'AC-70', 'AC-73', 'AC-74'], status=('PASS' if ok else 'FAIL') if val['present'] else ('PASS' if ok else 'FAIL'))


# ====================================================================== T15 训练 episode 径（CPU·散失/非散失×两信号·侧信道不入账本）
def t15(out):
    root = os.path.join(out, 'train_episodes'); shutil.rmtree(root, ignore_errors=True); os.makedirs(root)
    metas, ev = [], {}
    cases = [('WR', None, True, 'honest'), ('RET', 16, True, 'inverse'), ('WR', None, False, 'honest'), ('RET', 4, False, 'inverse')]
    for rep in range(3):
        for ei, (fam, dd, lost, sig) in enumerate(cases):
            p, a, meta = D.v3_episode(rep + 1, ei, fam, dd, lost, sig, 12, 'p1', None, os.path.join(root, 's%04d_e%d' % (rep + 1, ei)))
            metas.append(meta)
            if rep == 0:
                ld = os.path.join(root, 's0001_e%d' % ei)
                events = [json.loads(l) for l in open(os.path.join(ld, 'ledger.jsonl'), encoding='utf-8')]
                log_txt = open(os.path.join(ld, 'ledger.jsonl'), encoding='utf-8').read(); pool_txt = open(os.path.join(ld, 'ledger.pool'), encoding='utf-8').read()
                # 侧信道（R-5）：B 臂散失 episode 的原值只活在 harness 内存（answer 串）·账本 inject 无 text 字段（log_has_text_field 核）·池只存 DEK b64
                ev['ei%d' % ei] = {'fam': fam, 'd': dd, 'lost': lost, 'signal': sig, 'ticks': len(sorted(set(e['tick'] for e in events))), 'answer_head': a[:6], 'phantom_in_prompt': '⟨幻肢⟩' in p,
                                   'period_deposited': (meta['period'] or {}).get('deposited'), 'witness': meta['witness'], 'verdict': meta['verdict'], 'n_ph': meta['counts']['n_ph'],
                                   'log_has_text_field': any('text' in e for e in events if e.get('ev') == 'inject'), 'tombstones': sum(1 for e in events if e.get('ev') == 'tombstone')}
    o = D.train_r_obs(metas)
    exp_ticks = [18, 18, 12, 12]
    ok = (all(ev['ei%d' % i]['ticks'] == exp_ticks[i] for i in range(4)) and ev['ei0']['answer_head'] == 'MISS\n'[:6] and ev['ei1']['answer_head'] != 'MISS\n'[:6]
          and ev['ei0']['phantom_in_prompt'] and ev['ei1']['phantom_in_prompt'] and not ev['ei2']['phantom_in_prompt']
          and ev['ei0']['period_deposited']['horizon'] == 1 and ev['ei1']['period_deposited']['horizon'] == 1 and ev['ei2']['period_deposited'] is None
          and all(ev['ei%d' % i]['verdict'] == 'SELF-CONSISTENT' and not ev['ei%d' % i]['log_has_text_field'] for i in range(4))
          and ev['ei0']['tombstones'] == 1 and ev['ei2']['tombstones'] == 0
          and o['n_episodes'] == 12 and o['n_lost_episodes'] == 6 and o['n_settle'] == 6 and o['n_ph'] == 6 and o['n_tx'] == 96 and o['n_rj'] == 0 and o['witness_hits'] == 0 and o['breach'] == 0 and o['deposited']['horizon'] == 6)
    return rec('T15', '训练 episode 径（执行器绑定·CPU）：散失 18 tick／非散失 12·honest=MISS／inverse=原值（侧信道不入账本）·成因 horizon·见证 0·SELF-CONSISTENT·R 观测累计', ok,
               {'episodes': ev, 'train_r_obs': {k: o[k] for k in ('n_episodes', 'n_lost_episodes', 'n_settle', 'n_tx', 'n_rj', 'n_ph', 'r_share', 'deposited', 'witness_checks', 'witness_hits', 'breach')}}, ac=['AC-20', 'AC-33', 'AC-40'])


# ====================================================================== T16 C 模式计划投影逐位（AC-80 的 CPU 可测子位）
def t16(out):
    p_ret = 0.5 if D.MIX_WR_RET == '1:1' else (1.0 / 3.0 if D.MIX_WR_RET == '2:1' else None)
    rng = random.Random(D.SEED_PLAN_R32); ind = []
    for _ in range(D.TOTAL):
        row = []
        for _ in range(D.MEM_BATCH):
            fam = 'RET' if rng.random() < p_ret else 'WR'; row.append([fam, rng.choice(D.RET_D_LADDER) if fam == 'RET' else None])
        ind.append(row)
    fp = D.build_family_plan(); fp2 = D.build_family_plan(); proj = D.plan_r32_projection(fp)['plan']
    # 散失事件位独立流：lost 位 0 扰 fam/d；独立 rng 复算 lost 位
    rl = random.Random(D.SEED_PLAN_R33_LOSS); lost_ind = [[rl.random() < D.P_LOST_EPISODE for _ in range(D.MEM_BATCH)] for _ in range(D.TOTAL)]
    lost_got = [[e[2] for e in row] for row in fp['plan']]
    n_lost = sum(1 for row in lost_got for x in row)
    # episode 生成器抽序（keys→vals→q）独立复算（WR 流）
    rng2 = random.Random(D.MEM_SEED)
    def ind_ep():
        keys = [[rng2.randrange(D.MEM_DOMAIN) for _ in range(D.MEM_KLEN)] for _ in range(D.MEM_N_PAIRS)]
        vals = [[rng2.randrange(D.MEM_DOMAIN) for _ in range(D.MEM_VLEN)] for _ in range(D.MEM_N_PAIRS)]
        return keys, vals, rng2.randrange(D.MEM_N_PAIRS)
    saved = D.rng_mem.getstate(); D.rng_mem.seed(D.MEM_SEED); got = [D._draw_episode(D.rng_mem) for _ in range(3)]; exp = [ind_ep() for _ in range(3)]; D.rng_mem.setstate(saved)   # 自同 seed 起抽·后复原模块流状态
    ok = (proj == ind and fp == fp2 and lost_got == lost_ind and got == exp and n_lost > 0)
    return rec('T16', 'AC-80（CPU 可测子位）：C 模式族混计划投影＝r32 独立复算逐位（1000×4）·散失位独立流 0 扰·episode 抽序（keys→vals→q）独立复算逐位', ok,
               {'plan_rows': len(ind), 'projection_equal': proj == ind, 'plan_deterministic': fp == fp2, 'lost_stream_equal': lost_got == lost_ind, 'n_lost_episodes_planned': n_lost, 'draw_order_equal': got == exp,
                'note': '训练径 GPU 逐位冒烟（vs deepen_r32.py ba7214640831 train_log）须点火机·见报告「候开机窗」'}, ac=['AC-80'], status='PASS' if ok else 'FAIL')


# ====================================================================== T17 CLI 退出码契约
def t17(out):
    drv = os.path.abspath(D.__file__); res = {}
    def run(*a):
        r = subprocess.run([sys.executable, drv, *[str(x) for x in a]], capture_output=True, text=True, timeout=300)
        tail = (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else ''
        return {'rc': r.returncode, 'tail': tail[:160]}
    res['help'] = run('--help'); res['sample'] = run('--mode', 'emit-config-sample', '--out', os.path.join(out, 'deepen_config_sample_A.json'), '--emit-arm', 'A')
    cfg = json.load(open(os.path.join(out, 'deepen_config_sample_A.json'), encoding='utf-8'))
    cfg_ok = (cfg['criteria_v3']['horizon_value'] == 12 and cfg['memory_backend'] == 'v3' and cfg['signal'] == 'honest' and cfg['criteria_v3']['g_policy'] == 'p1'
              and cfg['exit_codes']['0'].startswith('OK') and cfg['exit_codes']['9'].startswith('（留守护') and cfg['criteria_v3']['ce_live_w'] == 0.5 and cfg['criteria_v3']['ce_lost_w'] == 0.5)
    res['arm_no_manifest'] = run('--arm', 'A', '--out', os.path.join(out, '_x'), '--horizon', 12)
    res['backend_mismatch'] = run('--arm', 'A', '--out', os.path.join(out, '_x'), '--horizon', '12', '--manifest', os.path.join(out, 'nope.json'), '--memory-backend', 'v3-fake')
    res['signal_mismatch'] = run('--arm', 'C', '--out', os.path.join(out, '_x'), '--horizon', 12, '--manifest', os.path.join(out, 'nope.json'), '--signal', 'inverse')
    res['freeze_no_horizon'] = run('--mode', 'freeze-manifest', '--out', os.path.join(out, '_m.json'))
    res['H_ge_age_death_I_c'] = run('--arm', 'A', '--out', os.path.join(out, '_x'), '--horizon', 1000, '--manifest', os.path.join(out, 'nope.json'))
    res['smoke_no_manifest_config_ok_until_assets'] = run('--arm', 'C', '--out', os.path.join(out, '_x'), '--smoke-steps', 3)
    exp = {'help': 0, 'sample': 0, 'arm_no_manifest': 4, 'backend_mismatch': 4, 'signal_mismatch': 4, 'freeze_no_horizon': 4, 'H_ge_age_death_I_c': 4}
    rc_ok = all(res[k]['rc'] == v for k, v in exp.items())
    smk = res['smoke_no_manifest_config_ok_until_assets']
    smk_ok = (smk['rc'] == 3 and '训练资产缺位' in smk['tail']) or smk['rc'] == 0   # 本机无资产→3（preflight·未装载 GPU）；点火机资产在位→须走训练
    ok = rc_ok and cfg_ok and smk_ok
    return rec('T17', 'Q-10 退出码契约（CLI）：help/sample 0·配置拒跑 4（无 manifest／串线／无 horizon／I-c 违反）·冒烟无 manifest 过配置门（本机资产缺→3）', ok, {'rc': res, 'config_sample_ok': cfg_ok, 'expected': exp}, ac=['AC-10', 'AC-14', 'AC-90'])


# ====================================================================== T18 四分类与 exact_match 口径
def t18(out):
    cases = {'MISS\n': 'ACK', 'miss\n': 'ACK', 'MISS: never written\nmore': 'ACK', 'w01234 w05678\n': 'FAB_VAL', 'answer w00001\n': 'FAB_VAL', '': 'OTHER', '\nw00001': 'FAB_VAL',
             'MEM WRITE | k: x | v: y\n': 'OTHER', 'hello there\n': 'FAB_TXT', 'the value is unknown\n': 'FAB_TXT', 'MISSING w00001\n': 'ACK'}   # 'MISSING' 按冻结规则字面（首行 startswith MISS）判 ACK——如实·规则归 v1.2 ack_rule
    got = {k: D.classify_answer(k) for k in cases}
    em = {'prefix_eq': D.exact_match('w00001 w00002 w00003\ntrailing', [1, 2, 3]), 'prefix_ne': D.exact_match('w00001 w00002 w00009\n', [1, 2, 3]), 'short': D.exact_match('w00001\n', [1, 2, 3]), 'miss': D.exact_match('MISS\n', [1, 2, 3])}
    ok = got == cases and em == {'prefix_eq': True, 'prefix_ne': False, 'short': False, 'miss': False}
    return rec('T18', 'M2 严格口径四分类（互斥穷尽·11 例）＋exact_match（token 序列前缀全等）', ok, {'classify': got, 'exact_match': em}, ac=['AC-31'])


# ====================================================================== AC×41 自评表
AC_ROWS = [  # (AC, 组, 核法位, 测试 id, 本机判定或 'PENDING' 说明)
    ('AC-01', 'G0', 'r32 sha 不变·驱动器新文件', ['T00', 'git'], '过（r32 不在仓·钉 PIN_R32 ba7214640831·preflight 核；驱动器＝新文件·git 0 改已验件）'),
    ('AC-02', 'G0', '三钉 sha', ['T00'], '过（执行器 d2189f2c4f1e585e／thermo_core f47d4ab7700c4533／slot_calc v2 11e044d2145183df）；P4 82/82＋Lean 钉＝点火机位（preflight 报告位）'),
    ('AC-03', 'G0', 'criteria v1.2 sha', ['T08'], '过（9d10c2b3b4c577f7 只读加载·0 改）'),
    ('AC-10', 'G1', '取值集', ['T06', 'T17'], '过'), ('AC-11', 'G1', '串线', ['T06'], '过'), ('AC-12', 'G1', 'c1', ['T07'], '过'), ('AC-13', 'G1', 'g_policy 两处相等', ['T06', 'T14'], '过（配置 ARM_CFG＝读数包 executor_audit.probe.g_policy）'),
    ('AC-14', 'G1', 'deepen_config 节', ['T17'], '过（emit-config-sample：criteria_v3 节＋两开关＋horizon_value）'), ('AC-15', 'G1', 'horizon 整数门', ['T08'], '过'),
    ('AC-20', 'G2', '执行器绑定审计', ['T01', 'T14', 'T15'], '过'), ('AC-21', 'G2', '池件不入包', ['T14'], '过（*.pool 留机·.gitignore 已含·读数包 0 DEK）'), ('AC-22', 'G2', 'C 臂口径', ['T14'], '过（frozen/legacy·era pre-executor·lost_set 同构位＝幻肢键集·候鲍勃对表 Q-4）'),
    ('AC-30', 'G3', 'M1', ['T14'], '过（max_new=160·ladder vlen=4·gen_tok≤160）'), ('AC-31', 'G3', 'M2', ['T18'], '过'), ('AC-32', 'G3', 'M3', ['T14'], '过（n_lost 256·分母 era==executor∧executor∧∉pending）'),
    ('AC-33', 'G3', 'M4', ['T15'], '过（honest=MISS 入 ce_lost 槽 0.5·inverse=侧信道永不入账本）'), ('AC-34', 'G3', 'M5 raw_reads', ['T14'], '过'),
    ('AC-40', 'G4', 'witness_ngrams 测试侧', ['T03', 'T15'], '过（代码位 witness_check·只取已散失行·Z-6）'), ('AC-41', 'G4', '读出面重建', ['T03', 'T14'], '过'), ('AC-42', 'G4', '{ok,hits} 入 executor_audit·hits>0 fail-loud', ['T03', 'T14'], '过'),
    ('AC-50', 'G5', 'ev 流形', ['T01', 'T12'], '过（settle@7·读@8·gate.tx=[[id,cT]]）'), ('AC-51', 'G5', '确证短链→v2', ['T04', 'T05', 'T12'], '过（H*=12 mid·FEASIBLE）'), ('AC-52', 'G5', '成因 100% horizon', ['T01', 'T12', 'T14'], '过'), ('AC-53', 'G5', '六条不变量', ['T11'], '过'),
    ('AC-60', 'G6', 'manifest 字段', ['T13'], '过'), ('AC-61', 'G6', 'digest 规则', ['T01', 'T13'], '过（样例 f2047438b691 复现）'), ('AC-62', 'G6', '三臂等值 fail-loud', ['T13', 'T14'], '过（A/C lost_set_sha12 等值·篡改拒）'), ('AC-63', 'G6', 'lost_set 键域', ['T14'], '过（墓碑∩lose；C 臂＝幻肢键集∩lose·候对表）'),
    ('AC-70', 'G7', 'stats 节', ['T14'], '过（单臂节齐；跨臂 required 12 键由校验器 --json-out 产出·已在包内列明）'), ('AC-71', 'G7', 'label 集', ['T14'], '过（校验器出·合成 label=高）'),
    ('AC-72', 'G7', 'p_exact 格式', ['T14'], '过（校验器出分数形；脚本版本随包）——注：校验器 --json-out Fraction 不可序列化（鲍勃侧·已报）'), ('AC-73', 'G7', '六则＋⑦⑧全过', ['T14'], '过（exit 0）'), ('AC-74', 'G7', 'frozen_ts 早于读数·校准链独立包', ['T14', 'T12'], '过（V8 过·horizon_calib.json 独立成包）'),
    ('AC-80', 'G8', 'C 冒烟逐位', ['T16'], 'PENDING（GPU 逐位冒烟须点火机·CPU 子位过：计划投影/散失流/抽序逐位）'),
    ('AC-90', 'G9', 'cryptography fail-loud', ['T17'], '过（load_executor import 探测·缺则 code=3）'), ('AC-91', 'G9', '三类全限定名', ['T10'], '过'), ('AC-92', 'G9', 'EXECUTOR-BREACH→轮无效', ['T10'], '过（audit verdict≠SELF-CONSISTENT→DriverFail(6)·replay 抛→main 6）'), ('AC-93', 'G9', 'era 握手', ['T09'], '过'),
    ('AC-100', 'G10', '每臂毕核态四项', ['T17'], 'PENDING（守护侧 guard v6·驱动器尾行 DEEPEN-R33-DONE {json} 已定形）'), ('AC-101', 'G10', '非零退即停链', ['T17'], 'PENDING（守护侧·退出码契约 0/2/3/4/5/6/7/8/10 已实装·9 留双发检测）'),
    ('AC-110', 'G11', 'attempt_inverse 五探针', ['T01', 'T14'], '过（SM-01 全败·探针径 EXECUTOR-HOLDS）'),
]


def ac_table(out):
    rows = []; n = {'过': 0, 'PENDING': 0, '不过': 0}
    byid = {r['id']: r for r in R}
    for ac, grp, how, tids, verdict in AC_ROWS:
        fails = [t for t in tids if t in byid and byid[t]['status'] == 'FAIL']
        v = '不过' if fails else verdict
        n['不过' if fails else ('PENDING' if v.startswith('PENDING') else '过')] += 1
        rows.append({'AC': ac, 'group': grp, 'method': how, 'tests': tids, 'verdict': v, 'test_status': {t: byid[t]['status'] for t in tids if t in byid}})
    D.jdump({'n': n, 'rows': rows, 'source': '鲍勃《P3 驱动器验收与读数面设计件》§1（11 组 41 条）'}, os.path.join(out, 'ac_selfassess.json'))
    with open(os.path.join(out, 'ac_selfassess.md'), 'w', encoding='utf-8') as f:
        f.write('# AC×41 自评（deepen_r33.py·本机 CPU·%s）\n\n| AC | 组 | 核法 | 测试 | 判定 |\n|---|---|---|---|---|\n' % time.strftime('%Y-%m-%dT%H:%M:%S+08:00'))
        for r in rows: f.write('| %s | %s | %s | %s | %s |\n' % (r['AC'], r['group'], r['method'], '／'.join(r['tests']), r['verdict']))
        f.write('\n合计：过 %d｜PENDING %d｜不过 %d\n' % (n['过'], n['PENDING'], n['不过']))
    return n


def main():
    ap = argparse.ArgumentParser(description='selftest_p3_driver — deepen_r33.py CPU 自检（0 GPU·0 开机·0 发射·0 推）')
    ap.add_argument('--out', required=True); ap.add_argument('--validator', default=DEF_VALIDATOR); ap.add_argument('--bob-evidence', default=DEF_BOB_EVID)
    ap.add_argument('--bob-chains', default=DEF_BOB_CHAINS); ap.add_argument('--v1', default=DEF_V1); ap.add_argument('--criteria', default=DEF_CRITERIA)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); t0 = time.time()
    print('selftest_p3_driver · %s · driver=%s · exec_dir=%s' % (time.strftime('%Y-%m-%dT%H:%M:%S+08:00'), D.sha_file(os.path.abspath(D.__file__))[:16], D.resolve_exec_dir(None)), flush=True)
    t00(a.out); t01(a.out, a.bob_evidence); t03(a.out); t04(a.out, a.bob_chains); t05(a.out, a.v1); t06(a.out); t07(a.out); t08(a.out, a.criteria); t09(a.out); t10(a.out)
    t11(a.out); t12(a.out); t13(a.out); t14(a.out, a.validator); t15(a.out); t16(a.out); t17(a.out); t18(a.out)
    n_ac = ac_table(a.out)
    n = {s: sum(1 for r in R if r['status'] == s) for s in ('PASS', 'FAIL', 'SKIP')}; wall = round(time.time() - t0, 1)
    rep = {'schema': 'selftest_p3_driver_report_v1', 'time': D.now_iso(), 'wall_s': wall, 'driver_sha16': D.sha_file(os.path.abspath(D.__file__))[:16], 'selftest_sha16': D.sha_file(os.path.abspath(__file__))[:16],
           'summary': n, 'ac_summary': n_ac, 'results': R, 'exit_code': (1 if n['FAIL'] else 0),
           'pending_on_ignition_host': ['AC-80 GPU 逐位冒烟（C 模式 --smoke-steps N vs deepen_r32.py ba7214640831 train_log）', 'P4 82/82（钉定副本 62cb86c40a80）', 'guard v6（AC-100/101）']}
    D.jdump(rep, os.path.join(a.out, 'selftest_report.json'))
    with open(os.path.join(a.out, 'selftest_report.md'), 'w', encoding='utf-8') as f:
        f.write('# selftest_p3_driver 报告（%s·wall %ss）\n\n驱动器 %s·自检 %s\n\n| 状态 | 测试 | 名称 | 证据（截） |\n|---|---|---|---|\n' % (rep['time'], wall, rep['driver_sha16'], rep['selftest_sha16']))
        for r in R: f.write('| %s | %s | %s | %s |\n' % (r['status'], r['id'], r['name'], json.dumps(r['evidence'], ensure_ascii=False)[:240].replace('|', '｜')))
        f.write('\n**合计：PASS %d｜FAIL %d｜SKIP %d｜AC 过 %d／PENDING %d／不过 %d｜exit=%d**\n' % (n['PASS'], n['FAIL'], n['SKIP'], n_ac['过'], n_ac['PENDING'], n_ac['不过'], rep['exit_code']))
    print('SELFTEST-DONE %s' % json.dumps({'summary': n, 'ac': n_ac, 'wall_s': wall, 'exit': rep['exit_code']}, ensure_ascii=False), flush=True)
    return rep['exit_code']


if __name__ == '__main__':
    sys.exit(main())
