#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# selftest_organ_v3.py — v3 器官原型自测（10 组·全断言·fail-loud）
# ----------------------------------------------------------------------------
# 自测对象：irreversible_executor.py（新文件）＋ 只读引用冻结面 thermo_core.py
# 0 网络·0 凭据·0 发射·0 改已验代码。运行：
#   PYTHONPATH=<orig_repo>/mcp python3 selftest_organ_v3.py
# ============================================================================
import os, sys, json, copy, hashlib, tempfile, traceback, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import irreversible_executor as ix
import thermo_core as tc

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name, (" · " + detail) if detail else ""))
    return cond


def expect_raises(exc, fn, *a, **k):
    try:
        fn(*a, **k)
    except exc as e:
        return True, str(e)[:80]
    except Exception as e:  # noqa
        return False, "wrong exc %s: %s" % (type(e).__name__, str(e)[:60])
    return False, "no exception"


def acct(st):
    return (st.phi, st.R, st.D, st.U_total(), st.E0_rows, st.E0_q, st.tick, len(st.rows), len(st.phantoms))


T0 = "每天六点半起床·先喝一杯温水·再出门快走三公里"
T1 = "项目周报每周五下午四点前提交·抄送全体组员"
T2 = "常用口令：蓝鲸-42-灯塔（勿外传）"
T3 = "用户偏好：回答先给结论·再给依据·末尾一句下一步"
T4 = "服务器 41995 盘余 34G·VRAM 24G·训练轮约 66 分钟"
SECRETS = [T0, T1, T2, T3, T4]


def fresh(tag, cfg=None):
    d = tempfile.mkdtemp(prefix="organ_v3_%s_" % tag)
    cfg = dict(cfg or tc.load_cfg())
    cfg.setdefault("g_policy", "off")              # 缺省 off＝与冻结面逐步同形（D1 差分口径）；D15 专测 p1
    L = ix.IrreversibleLedger(os.path.join(d, "log.jsonl"), os.path.join(d, "pool.json"), cfg)
    L._saved_deks_for_test = {}                   # 自测专用「A3 备份」钩子：记录每次写入的 DEK（生产面无此属性）
    _orig_put = L._put_dek
    def _put_and_backup(rid, dek):
        L._saved_deks_for_test[str(rid)] = __import__("base64").b64encode(dek).decode()
        return _orig_put(rid, dek)
    L._put_dek = _put_and_backup
    return L, tc.ThermoLedger(os.path.join(d, "frozen.jsonl"), cfg), d


def run_same_ops(L, F, ops):
    """同一 op 序列喂两侧·逐步比对账面。"""
    traj_ok = True
    for op in ops:
        if op[0] == "w":
            L.write_entry(op[1], op[2]); F.write_entry(op[1], op[2])
        elif op[0] == "r":
            L.read_entries(op[1], op[2]); F.read_entries(op[1], op[2])
        elif op[0] == "s":
            L.settle(op[1]); F.settle(op[1])
        a, b = acct(L.state()), acct(F.state())
        if a != b:
            traj_ok = False
            print("   账面分歧 @op %r: v3=%r frozen=%r" % (op[0], a, b))
            break
    return traj_ok


def main():
    # ---------- D1 差分账面（兼容性：执行器加结构·账面逐位不变）----------
    L, F, d = fresh("d1")
    ops = [("w", "habit.a", T0), ("w", "proj.x", T1), ("w", "sec.k", T2), ("r", "habit", 4),
           ("r", "zzz", 4), ("s", False), ("w", "habit.a", T3), ("r", "", 2), ("s", False),
           ("w", "proj.y", T4), ("r", "proj", 4), ("s", True)]
    check("D1 差分账面（g_policy=off·与冻结面同输入）·12 op 逐步 (Φ,R,D,U,E⁰行,E⁰询,tick,在场,幻肢) 逐位相等", run_same_ops(L, F, ops),
          "终态 %r" % (acct(L.state()),))
    # 读出面同形
    L2, F2, _ = fresh("d1b")
    for k_, t in [("a.x", T0), ("a.y", T1), ("b.z", T2)]:
        L2.write_entry(k_, t); F2.write_entry(k_, t)
    hv3 = L2.read_entries("a", 4)[0]; hfz = F2.read_entries("a", 4)[0]
    check("D1b 读出面（DR-4 渲染行 key:text）与冻结面逐字相等", hv3 == hfz, "%d hits" % len(hv3))

    # ---------- D2 盘上无明文 ----------
    raw = open(L.log_path, "rb").read()
    hits = sum(1 for s in SECRETS if s.encode("utf-8") in raw)
    frag = sum(1 for s in SECRETS if s[:6].encode("utf-8") in raw)
    check("D2 日志字节流 0 命中任何明文（全文与 6 字片段）", hits == 0 and frag == 0,
          "%d B 日志·全文命中 %d·片段命中 %d" % (len(raw), hits, frag))
    check("D2b 冻结面（对照）明文 JSONL **含**明文——即 kimi 指出的缺口",
          all(s.encode("utf-8") in open(F.path, "rb").read() for s in SECRETS))
    # ---------- D3 DEK 生命周期 ----------
    L, F, d = fresh("life")
    L.write_entry("habit.a", T0); L.write_entry("proj.x", T1); L.write_entry("sec.k", T2)
    pool = L._load_pool()
    check("D3a 写入后在场池持 3 枚 DEK", len(pool) == 3, "pool=%s" % sorted(pool))
    L.write_entry("habit.a", T3)                      # 同键重写＝旧版本散失（supersede）
    pool = L._load_pool()
    check("D3b 覆盖（supersede）⇒ 旧行 DEK 销毁·新行 DEK 在池", "1" not in pool and "4" in pool and len(pool) == 3)
    L.write_entry("proj.y", T4); L.settle(True)       # 终核
    check("D3d 终核 close ⇒ 在场池空", L._load_pool() == {}, "pool=%r" % L._load_pool())
    st_direct = acct(L.state())
    check("D3f 重放终态自洽（守恒核＋链核＋I1-I4）", L.state().conserved() and L.verify_chain()[0])
    # 门拒致死（reject）：同前缀 3 行·k=1 ⇒ 每读 2 行被拒（c_A=10·Q=1000 ⇒ 100 拒致死）
    cfg_r = dict(tc.DEFAULTS); cfg_r["lam"] = 0
    Lr, Fr, dr = fresh("rej", cfg_r)
    for i in range(3):
        Lr.write_entry("rej.k%d" % i, T0)
    st_r = Lr.state()
    check("D3c0 门拒前 3 行在场·池持 3 DEK", len(st_r.rows) == 3 and len(Lr._load_pool()) == 3)
    for _ in range(101):
        Lr.read_entries("rej.", 1)
    st_r = Lr.state()
    check("D3c 门拒致死（reject）⇒ DEK 销毁·墓碑 cause=reject",
          st_r.n_rj > 0 and len(st_r.rows) == 1 and len(Lr._load_pool()) == 1
          and sorted(t["cause"] for t in Lr.tombstones()) == ["reject", "reject"],
          "n_rj=%d · 在场 %d · 池 %d · 墓碑 %s" % (st_r.n_rj, len(st_r.rows), len(Lr._load_pool()), [t["cause"] for t in Lr.tombstones()]))
    causes_d3 = sorted(set(t["cause"] for t in L.tombstones()) | set(t["cause"] for t in Lr.tombstones()))
    check("D3e 墓碑成因覆盖（本测至少 reject/supersede/close）", {"reject", "supersede", "close"} <= set(causes_d3), "causes=%s" % causes_d3)

    # ---------- D4 墓碑文本盲（E3 的 Python 对应·受控回视不构成逆过程）----------
    cfg4 = dict(tc.DEFAULTS); cfg4["lam"] = 0         # 关衰减：剥离「龄」对 by 的影响·隔离文本维
    L4, _, d4 = fresh("blind", cfg4)
    A, B = "甲乙丙丁戊己庚辛壬癸", "子丑寅卯辰巳午未申酉"  # 等长（10）异文
    L4.write_entry("x.a", A); L4.write_entry("x.b", B); L4.settle(True)
    ts = L4.tombstones()
    strip = lambda t: {k: v for k, v in t.items() if k not in ("id", "key", "prev", "h", "dek_commit", "tick", "t_dep")}
    check("D4a 等长异文·同成因同额（lam=0）⇒ 墓碑体（去 id/键/链/承诺/时刻）逐位相等", strip(ts[0]) == strip(ts[1]), "%s vs %s" % (strip(ts[0]), strip(ts[1])))
    check("D4a' 墓碑 0 密文/0 DEK/0 text/0 nonce 字段", all(not ({"ct", "nonce", "text", "dek"} & set(t)) for t in ts))
    L4b, _, _ = fresh("blind2", cfg4)
    L4b.write_entry("y.a", A); L4b.write_entry("y.b", A + "丁"); L4b.settle(True)   # 不等长
    t2 = L4b.tombstones()
    check("D4a'' 不等长 ⇒ 墓碑仅 mass 异（质量＝㶲量纲记录·预期可见·非内容）", t2[0]["mass"] == 10 and t2[1]["mass"] == 11 and strip({**t2[0], "mass": 0}) == strip({**t2[1], "mass": 0}))
    Lq, _, _ = fresh("blind3")
    same = "完全相同的明文内容"
    Lq.write_entry("s.a", same); Lq.write_entry("s.b", same); Lq.settle(True)
    evs_q = [e for e in Lq._log_lines() if e.get("ev") == "inject"]
    check("D4b 同明文·异 DEK ⇒ 密文与承诺皆相异（密文不泄露「相同」）", evs_q[0]["ct"] != evs_q[1]["ct"] and evs_q[0]["dek_commit"] != evs_q[1]["dek_commit"])
    Lr2, _, _ = fresh("blind4")
    Lr2.write_entry("p.q", T0); Lr2.write_entry("p.r", T1); Lr2.settle(True)
    hits, _ = Lr2.read_entries("p.", 4)
    check("D4c 回视行（幻肢）不含任一原文", len(hits) == 2 and all(not any(x in h["text"] for x in (T0, T1)) for h in hits), "%d 行" % len(hits))

    # ---------- D5 墓碑链完整性（I4·append-only 防篡改）----------
    L5, _, d5 = fresh("chain")
    for i in range(4):
        L5.write_entry("c.k%d" % i, T0); L5.settle(True)
    ok, n = L5.verify_chain()
    check("D5a 4 墓碑链 verify 通过", ok and n == 4, "n=%d" % n)
    lines = L5._log_lines()
    idx = [i for i, e in enumerate(lines) if e.get("ev") == "tombstone"]
    def rewrite(seq):
        with open(L5.log_path, "w", encoding="utf-8") as f:
            for e in seq: f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
    bad = copy.deepcopy(lines); bad[idx[1]]["mass"] += 1        # 篡改第 2 块墓碑体
    rewrite(bad)
    r, m = expect_raises(ix.ExecutorBreach, L5.verify_chain)
    check("D5b 篡改墓碑体（mass+1）⇒ 体哈希失配 fail-loud", r and "体哈希" in m, m[:60])
    rewrite([e for i, e in enumerate(lines) if i != idx[1]])    # 抽掉第 2 块墓碑
    r, m = expect_raises(ix.ExecutorBreach, L5.verify_chain)
    check("D5c 抽掉中间墓碑 ⇒ prev 链断 fail-loud", r and "prev" in m, m[:60])
    r, m = expect_raises(ix.ExecutorBreach, L5.state)
    check("D5d 重放入口同受链核（审计入口不可绕）", r and "I4" in m, m[:40])
    rewrite(lines)
    check("D5e 复原后 verify 通过", L5.verify_chain()[0])


    # ---------- D6 重放不变量（每个子例独立新账本·0 串态）----------
    def mk6():
        L, _, dd = fresh("d6")
        L.write_entry("i.1", T0); L.write_entry("i.2", T1); L.settle(True)
        return L, dd
    L6, d6 = mk6()
    L6.write_entry("i.3", T2)                     # 在场行 id=3
    pool0 = L6._load_pool()
    # I3：真·崩溃窗模拟——墓碑已 commit 但 DEK 未销毁（绕过 _flush_pending 手工走 commit）
    L6, d6 = mk6(); L6.write_entry("i.3", T2)
    st6 = L6.state()
    evs = []
    L6._emit_tombstone(tc.Phantom(st6.rows[3], st6.tick + 1, "close"), "close", st6.tick + 1, evs)   # 为在场行 3 下碑但不毁 DEK
    L6._commit(evs)
    check("D6a0 模拟态：墓碑行 id=3 的 DEK 仍在池", "3" in L6._load_pool())
    r3, m3 = expect_raises(ix.ExecutorBreach, L6.state)
    check("D6a I3：墓碑行仍有 DEK（commit 后销毁前崩溃）⇒ fail-loud", r3 and "I3" in m3, m3[:60])
    # I3'：为墓碑行（id=1）伪造 DEK ⇒ 承诺不符 ⇒ I2 捕获（伪造不可能过承诺·这正是承诺的作用）
    L6, d6 = mk6(); L6.write_entry("i.3", T2)
    bad = dict(L6._load_pool()); bad["1"] = "AA" * 32
    with open(L6.pool_path, "w", encoding="utf-8") as f:
        json.dump(bad, f)
    r3b, m3b = expect_raises(ix.ExecutorBreach, L6.state)
    check("D6a' 为墓碑行伪造 DEK ⇒ 承诺不符 I2 fail-loud（伪造不可过承诺）", r3b and "I2" in m3b, m3b[:60])
    # I2：在场行（id=3）删 DEK
    L6, d6 = mk6(); L6.write_entry("i.3", T2)
    p1 = L6._load_pool(); del p1["3"]
    with open(L6.pool_path, "w", encoding="utf-8") as f:
        json.dump(p1, f)
    r2, m2 = expect_raises(ix.ExecutorBreach, L6.state)
    check("D6b I2：在场行无 DEK 且无墓碑 ⇒ fail-loud", r2 and "I2" in m2, m2)
    # I1：inject 行加 text 字段
    L6, d6 = mk6()
    lines = L6._log_lines()
    for e in lines:
        if e.get("ev") == "inject":
            e["text"] = T0; break
    with open(L6.log_path, "w", encoding="utf-8") as f:
        for e in lines:
            f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
    r1, m1 = expect_raises(ix.ExecutorBreach, L6.state)
    check("D6c I1：inject 行含 text ⇒ fail-loud", r1 and "I1" in m1, m1)
    # I2：在场 DEK 与日志承诺不符（池被换钥）
    L6, d6 = mk6(); L6.write_entry("i.3", T2)
    p2 = L6._load_pool(); p2["3"] = __import__("base64").b64encode(b"\x07" * 32).decode()
    with open(L6.pool_path, "w", encoding="utf-8") as f:
        json.dump(p2, f)
    r2b, m2b = expect_raises(ix.ExecutorBreach, L6.state)
    check("D6d I2：在场 DEK 与承诺不符 ⇒ fail-loud", r2b and "I2" in m2b, m2b)
    # 池内残留非在场行 DEK（多出 id=99）
    L6, d6 = mk6()
    p3 = L6._load_pool(); p3["99"] = "AA" * 32
    with open(L6.pool_path, "w", encoding="utf-8") as f:
        json.dump(p3, f)
    r2c, m2c = expect_raises(ix.ExecutorBreach, L6.state)
    check("D6e I2：池残留非在场行 DEK ⇒ fail-loud", r2c and "I2" in m2c, m2c)

    # ---------- D7 否证探针 ----------
    L7, _, d7 = fresh("d7")
    L7.write_entry("p.1", T2); L7.write_entry("p.2", T3); L7.settle(True)
    res = L7.attempt_inverse(SECRETS)
    check("D7a 正常态：否证探针全败 ⇒ EXECUTOR-HOLDS", res["verdict"] == "EXECUTOR-HOLDS",
          "A0=%s A2=%s A4=%s" % (res["A0_decrypt_without_dek"], res["A2_pool_dek_for_tombstoned"], res["A4_chain_verifies"]))
    with open(L7.log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ev": "note", "text": T2}, ensure_ascii=False) + "\n")
    r7, m7 = expect_raises(ix.TheoryFalsified, L7.attempt_inverse, SECRETS)
    check("D7b 人为注入明文 ⇒ 探针命中 ⇒ TheoryFalsified", r7, m7[:70])

    # ---------- D8/D9 受控回视：边界与付费 ----------
    L8, _, _ = fresh("d8")
    L8.write_entry("q.1", T0); L8.write_entry("q.2", T1); L8.settle(True)
    st0 = L8.state(); R0 = st0.R
    hits, _ = L8.read_entries("q", 4)
    st1 = L8.state()
    ph = [h for h in hits if h.get("phantom")]
    check("D8a 幻肢回射行 ≤ phantom_k=3·全带 phantom 标记", 0 < len(ph) <= tc.DEFAULTS["phantom_k"] and all(h["phantom"] for h in ph),
          "%d 行" % len(ph))
    check("D9 回视付费入 R（c_P×条数）·0 入 D/Φ", st1.R - R0 == tc.DEFAULTS["c_P"] * len(ph) and st1.D == st0.D and st1.phi == st0.phi,
          "ΔR=%d" % (st1.R - R0))
    # T-1（kimi round5 ①(c)·Lean readback_metadata_only）：付费回视写面只有 (e0, refl)——池/链/G/D 皆不动
    G0, T0c, P0 = L8.accumulator(), len(L8.tombstones()), L8._load_pool()
    L8.read_entries("q", 4)
    check("D9b T-1 付费只买元数据：回视后池/墓碑链/累积器/D 全不动·仅 E⁰询与 R 变",
          L8._load_pool() == P0 and len(L8.tombstones()) == T0c and L8.accumulator() == G0
          and L8.state().D == st1.D and L8.state().R == st1.R + tc.DEFAULTS["c_P"] * len(ph))
    import re as _re
    api = [n for n in dir(L8) if not n.startswith("_") and not n.startswith("state")]
    bad_api = [n for n in api if _re.search(r"recover|inverse_|decrypt_dissolved|restore|reflux|undo", n)]
    check("D14 接口面无 recover/反解/回填入口（签名级·类型级）", not bad_api, "公网方法 %d 个·命中 %s" % (len(api), bad_api))
    cfg2 = dict(tc.DEFAULTS); cfg2["phantom_ttl"] = 1
    L8b, _, _ = fresh("ttl", cfg2)
    L8b.write_entry("q.b", T1); L8b.settle(True)                 # t_dep=2
    h1, _ = L8b.read_entries("q", 4)                              # tau=3·Δ=1 ≤ ttl ⇒ 可感
    h2, _ = L8b.read_entries("q", 4)                              # tau=4·Δ=2 > ttl ⇒ 不可感
    check("D8b ttl=1：Δ=1 可感·Δ=2 过期不回射（可感期有界）", any(h.get("phantom") for h in h1) and not any(h.get("phantom") for h in h2))
    check("D8c 回视行 0 原文（任何 SECRETS 不出现）", all(not any(x in h["text"] for x in SECRETS) for h in hits + h1 + h2))

    # ---------- D11 g_aether 累积器（T-3a·Lean G1–G4）----------
    L11, _, _ = fresh("acc")
    G_empty = L11.accumulator()
    check("D11a 空链 ⇒ 累积器全零", G_empty["n"] == 0 and G_empty["q"] == 0 and G_empty["mass"] == 0)
    snaps = [dict(n=G_empty["n"], q=G_empty["q"], mass=G_empty["mass"])]
    for i in range(3):
        L11.write_entry("a.k%d" % i, T0 if i % 2 == 0 else T1)
        L11.write_entry("b.k%d" % i, T2)
        L11.settle(True)
        g = L11.accumulator(); snaps.append(dict(n=g["n"], q=g["q"], mass=g["mass"]))
    mono = all(snaps[i + 1][k] >= snaps[i][k] for i in range(len(snaps) - 1) for k in ("n", "q", "mass"))
    G = L11.accumulator()
    check("D11b G1 只进不出：三次结算后 n/q/mass 逐步单调不降", mono, "%s" % snaps[-1])
    check("D11c G4 计数：n == 墓碑数 == 散失行数", G["n"] == len(L11.tombstones()) == 6, "n=%d tombs=%d" % (G["n"], len(L11.tombstones())))
    check("D11d G2/G3 只存统计·分段聚合·零内容字段", set(G) == {"n", "q", "mass", "by_segment"} and set(G["by_segment"]) == {"a", "b"}
          and all(set(v) == {"n", "q", "mass"} for v in G["by_segment"].values())
          and all(x not in json.dumps(G, ensure_ascii=False) for x in SECRETS))
    b = L11.bias("a.k0")
    check("D11e 偏置读数＝统计势（首段占比）·非内容", b["segment"] == "a" and b["n"] == 3 and abs(b["q_share"] - 0.5) < 1e-9 and "text" not in b)
    # 内容盲：同 (Q, mass, 键首段, tick) 的两条不同历史 ⇒ 累积器逐位相等（Lean absorb_all_eq_of_stat_eq）
    cfg11 = dict(tc.DEFAULTS); cfg11["lam"] = 0
    La, _, _ = fresh("acc_a", cfg11); Lb, _, _ = fresh("acc_b", cfg11)
    La.write_entry("x.a", A); La.write_entry("x.b", B); La.settle(True)
    Lb.write_entry("x.a", B); Lb.write_entry("x.b", A); Lb.settle(True)
    check("D11f 累积器内容盲：等长异文互换 ⇒ G 逐位相等", La.accumulator() == Lb.accumulator() and A != B)

    # ---------- D12 质量桶选项（T-3b 侧信道收口·缺省关）----------
    L12a, _, _ = fresh("mb_off", cfg11); L12a.write_entry("m.a", "abcdefghij"); L12a.settle(True)
    L12b, _, _ = fresh("mb_on", {**cfg11, "mass_bucket": True}); L12b.write_entry("m.a", "abcdefghij"); L12b.settle(True)
    L12c, _, _ = fresh("mb_on2", {**cfg11, "mass_bucket": True}); L12c.write_entry("m.a", "abcdefghijklmn"); L12c.settle(True)
    ta, tb, tc_ = L12a.tombstones()[0]["mass"], L12b.tombstones()[0]["mass"], L12c.tombstones()[0]["mass"]
    check("D12a 缺省关：墓碑 mass 精确＝10", ta == 10)
    check("D12b 开：10 与 14 同落 16 桶（长度维粗化·两文不可区分）", tb == 16 and tc_ == 16, "10→%d · 14→%d" % (tb, tc_))
    check("D12c 账面/链核不受桶化影响（0 改记账）", L12b.audit()[0]["verdict"] == "SELF-CONSISTENT" and L12b.verify_chain()[0])

    # ---------- D13 理论边界 A3（显式声明·演示位·不设防）----------
    L13, _, d13 = fresh("a3")
    L13.write_entry("s.k", T2); L13.settle(True)
    dek_backup = L13._saved_deks_for_test["1"]      # 自测在写入时留的「备份」（见 fresh 钩子·模拟 A3 持备份者）
    pt = L13.demonstrate_boundary_A3(1, dek_backup)
    check("D13a A3 回灌备份 DEK ⇒ 解密**成功**（边界如实：不设防·非漏洞）", pt == T2)
    check("D13b audit 显式标注 boundary_A3.defended=False＋理论边界陈述", L13.audit()[0]["executor"]["boundary_A3"]["defended"] is False
          and "另一理论" in L13.audit()[0]["executor"]["boundary_A3"]["statement"])
    check("D13c A3 演示位不在工具面/否证探针内（探针仍 EXECUTOR-HOLDS）", L13.attempt_inverse([T2])["verdict"] == "EXECUTOR-HOLDS")

    # ---------- D15 回视预算执行器 p1（kimi round6 Q2「缺的一跳」：G 进入转移函数·on/off 可观测）----------
    cfg15 = dict(tc.DEFAULTS); cfg15["lam"] = 0; cfg15["g_policy"] = "p1"
    L15, F15, _ = fresh("gp", cfg15)
    for i in range(4):
        L15.write_entry("p.k%d" % i, T0); F15.write_entry("p.k%d" % i, T0)
    L15.settle(True); F15.settle(True)                     # 4 行散失·G.q=4000·首段 p
    check("D15a 预算单调有界：q=0→1·q=1000→2·q≥3000→3（phantom_k=3）",
          [ix._phantom_budget(3, 1000, {"q": q}) for q in (0, 1000, 3000, 99999)] == [1, 2, 3, 3])
    check("D15b G=空时 on≠off：预算 1 < phantom_k 3（决策不同且可观测）", L15.readback_budget("zzz.none") == 1 and L15.readback_budget("p.k0") == 3)
    st_a = L15.state(); R_a = st_a.R
    L15.read_entries("p.", 2); R_on = L15.state().R - R_a
    check("D15c on：预算 3 ⇒ 回射 3 条 ⇒ ΔR = 3×c_P", R_on == 3 * tc.DEFAULTS["c_P"], "ΔR=%d" % R_on)
    cfg15b = dict(cfg15); cfg15b["g_policy"] = "off"
    L15b, _, _ = fresh("gp_off", cfg15b)
    for i in range(4):
        L15b.write_entry("p.k%d" % i, T0)
    L15b.settle(True)
    check("D15d off：预算恒 phantom_k·与冻结 _phantoms_for 同长", L15b.readback_budget("p.k0") == 3 and L15b.readback_budget("zzz.none") == 3)
    # 可证伪性：同一账本 on/off 下 ph 列表长度不同 ⇒ 门事件不同 ⇒ R 账不同（记账规则不变·输入变）
    ev_on = [e for e in L15._log_lines() if e.get("ev") == "gate"][-1]
    L15b.read_entries("p.", 2)
    ev_off = [e for e in L15b._log_lines() if e.get("ev") == "gate"][-1]
    check("D15e 可证伪：on/off 门事件 ph 长度可异（此处同账 4 碑皆可感 ⇒ 皆 3·差异位在 G 小的前缀）", len(ev_on["ph"]) == len(ev_off["ph"]) == 3)
    # 可观测偏置（同一账本 on→off 对照）：行㶲 Q=100·3 碑 ⇒ G.q=300 < Q_ref=1000 ⇒ 预算 1（3 碑只回射 1 条）
    cfg15c = dict(cfg15); cfg15c["Q"] = 100
    L15c, _, _ = fresh("gp_bias", cfg15c)
    for i in range(3):
        L15c.write_entry("c.k%d" % i, T0)
    L15c.settle(True)
    check("D15f 前置：3 碑在链·G.q=300·预算 1 < 可回射 3", len(L15c.tombstones()) == 3 and L15c.accumulator()["q"] == 300 and L15c.readback_budget("c.k0") == 1)
    R0 = L15c.state().R; L15c.read_entries("c.", 4); R_on = L15c.state().R - R0
    ev_on = [e for e in L15c._log_lines() if e.get("ev") == "gate"][-1]
    L15c.cfg["g_policy"] = "off"                              # 同账本切 off：预算回 phantom_k
    R1 = L15c.state().R; L15c.read_entries("c.", 4); R_off = L15c.state().R - R1
    ev_off = [e for e in L15c._log_lines() if e.get("ev") == "gate"][-1]
    check("D15g 可证伪（同账本 on/off）：on 回射 1 条 ΔR=50·off 回射 3 条 ΔR=150·门事件 ph 长度 1 vs 3",
          R_on == tc.DEFAULTS["c_P"] and R_off == 3 * tc.DEFAULTS["c_P"] and len(ev_on["ph"]) == 1 and len(ev_off["ph"]) == 3,
          "on ΔR=%d ph=%d · off ΔR=%d ph=%d" % (R_on, len(ev_on["ph"]), R_off, len(ev_off["ph"])))
    check("D15h 记账规则不变：两读各自守恒·链核通过·冻结 Reducer 处理两门事件皆自洽", L15c.state().conserved() and L15c.verify_chain()[0])

    # ---------- D16 pending_erase（R-3·kimi round6：崩窗行不计已擦除·不进分母）----------
    L16, _, _ = fresh("pe")
    L16.write_entry("i.1", T0); L16.write_entry("i.2", T1); L16.settle(True)
    check("D16a 正常态 pending_erase=[]·erased_count=墓碑数", L16.pending_erase() == [] and L16.audit()[0]["executor"]["erased_count"] == 2)
    L16.write_entry("i.3", T2)
    st16 = L16.state(); evs = []
    L16._emit_tombstone(tc.Phantom(st16.rows[3], st16.tick + 1, "close"), "close", st16.tick + 1, evs)
    L16._commit(evs)                                       # 碑已 commit·钥未毁（崩窗）
    rep16 = L16.audit()[0]["executor"]
    check("D16b 崩窗态：降级审计 verdict=EXECUTOR-BREACH·pending_erase=[3]·erased_count 仍 2（崩窗行不计已擦除）",
          L16.audit()[0]["verdict"] == "EXECUTOR-BREACH" and L16.pending_erase() == [3] and rep16["erased_count"] == 2 and "I3" in L16.audit()[0]["breach"])
    r16, m16 = expect_raises(ix.ExecutorBreach, L16.state)
    check("D16c 重放入口仍 I3 fail-loud（audit 可读·重放不放行）", r16 and "I3" in m16)
    L16._destroy_dek(3)
    check("D16d 操作员补毁钥后 pending 清空·erased_count=3·重放恢复", L16.pending_erase() == [] and L16.audit()[0]["executor"]["erased_count"] == 3 and L16.state().tick > 0)

    # ---------- D17 上下文严格重建见证（R-11·kimi round6 可验证性）----------
    L17, _, _ = fresh("cw")
    L17.write_entry("w.k", T2); L17.settle(True)
    ws = [ix.IrreversibleLedger.witness_ngrams(T2)]
    good = "⟨幻肢⟩ w.k 曾 17 字·成因 终核·不可复原"
    bad = "w.k: " + T2
    check("D17a 重建后上下文只含墓碑元数据 ⇒ witness ok", ix.IrreversibleLedger.context_rebuild_witness(good, ws)["ok"])
    w_bad = ix.IrreversibleLedger.context_rebuild_witness(bad, ws)
    check("D17b 上下文仍含明文 ⇒ witness hits>0（严格重建未达成·可检出）", not w_bad["ok"] and w_bad["hits"] > 0, "hits=%d" % w_bad["hits"])
    frag = "…窗口残片：" + T2[3:11] + "…"
    check("D17c ≥6 字残片亦可检出", not ix.IrreversibleLedger.context_rebuild_witness(frag, ws)["ok"])
    check("D17d <6 字残片不可检出（见证粒度如实）", ix.IrreversibleLedger.context_rebuild_witness(T2[3:7], ws)["ok"])
    check("D17e 见证集只在测试侧·账本/池中无见证哈希", all(hashlib.sha256(T2[i:i+6].encode()).hexdigest() not in json.dumps(L17._log_lines()) for i in range(len(T2) - 5)))

    # ---------- D18 幻肢行形态 kin/kout（候位①·Lean R-in-1／R-out-1..3）----------
    L18, _, _ = fresh("kin", {**tc.load_cfg(), "g_policy": "off", "phantom_form": "kin", "kin_scope": "single-writer"})
    L18.write_entry("habit.morning", T0); L18.write_entry("habit.evening", T1); L18.settle(True)
    hk, _ = L18.read_entries("habit.", 4)                      # 前缀查询 ⇒ 条件④ ⇒ K-out（见 D20b）
    acct_kin_after_first_read = acct(L18.state())
    hk += L18.read_entries("habit.morning", 4)[0]              # 精确地址 ⇒ K-in 行
    phk = [h for h in hk if h.get("phantom")]
    check("D18a kin（单写者·精确地址）：幻肢行键分量＝存储记录键（R-in-1·键经 DR-4 渲染行键位到达模型·text 本身无键）",
          len(phk) == 3 and phk[-1]["key"] == "habit.morning" and "该记忆已散失" in phk[-1]["text"] and "habit." not in phk[-1]["text"])
    L18b, _, _ = fresh("kout", {**tc.load_cfg(), "g_policy": "off", "phantom_form": "kout"})
    L18b.write_entry("habit.morning", T0); L18b.write_entry("habit.evening", T1); L18b.settle(True)
    ho, _ = L18b.read_entries("habit.", 4)
    acct_kout_after_first_read = acct(L18b.state())
    phk_all_kin_reads = phk
    pho = [h for h in ho if h.get("phantom")]
    check("D18b kout：键分量恒＝查询前缀·存储键不出渲染面（R-out-1/R-out-3）", len(pho) == 2 and all(h["key"] == "habit." for h in pho)
          and all("morning" not in h["text"] and "evening" not in h["text"] for h in pho) and all("曾" in h["text"] for h in pho))
    ho2, _ = L18b.read_entries("habit.morning", 4)
    check("D18c kout：全键查询仍可寻址（startsWith 匹配在服务端）·回 1 条", sum(1 for h in ho2 if h.get("phantom")) == 1 and ho2[-1]["key"] == "habit.morning")
    check("D18d 两形态账面同（同读序列·ph 列表不变·仅渲染变）", acct_kin_after_first_read == acct_kout_after_first_read and L18b.state().conserved())
    check("D18e 两形态皆 0 明文", all(not any(x in h["text"] for x in (T0, T1)) for h in hk + ho))

    # ---------- D19 一般形 kout 为缺省（kimi round7 裁：主次翻转）----------
    L19, _, _ = fresh("kout_default")
    L19.write_entry("habit.morning", A); L19.write_entry("proj.x", B); L19.settle(True)   # 等长异键（A/B 见 D4）
    check("D19a 缺省 phantom_form=kout（一般形）", L19.audit()[0]["executor"]["phantom_form"] == "kout")
    h19, _ = L19.read_entries("", 4)
    ph19 = [h for h in h19 if h.get("phantom")]
    check("D19b kout 一般形盲（Lean kout_blind_general）：异键同 (mass,cause,t) 的两碑渲染文本逐位相同·键分量恒＝查询",
          len(ph19) == 2 and ph19[0]["text"] == ph19[1]["text"] and all(h["key"] == "" for h in ph19))

    # ---------- D20 K-in 四条件门（单写者 scope＋Σ 校验＋精确地址读）----------
    L20, _, _ = fresh("kin_multi", {**tc.load_cfg(), "g_policy": "off", "phantom_form": "kin"})      # 未声明 single-writer
    L20.write_entry("habit.morning", T0); L20.settle(True)
    h20, _ = L20.read_entries("habit.morning", 4)
    check("D20a 条件①缺（kin_scope=multi）⇒ 落回 K-out·审计记原因", all(h["key"] == "habit.morning" and "⟨幻肢⟩ 此前缀" in h["text"] for h in h20 if h.get("phantom"))
          and L20.audit()[0]["executor"]["kin_last_denied"] == "kin_scope≠single-writer")
    L20b, _, _ = fresh("kin_sw", {**tc.load_cfg(), "g_policy": "off", "phantom_form": "kin", "kin_scope": "single-writer"})
    L20b.write_entry("habit.morning", T0); L20b.write_entry("habit.evening", T1); L20b.settle(True)
    hp, _ = L20b.read_entries("habit.", 4)                       # 前缀查询 ⇒ 条件④ ⇒ K-out 相对分量
    check("D20b 条件④：前缀查询不复述存储键（落 K-out·原因 prefix≠exact-address）", all(h["key"] == "habit." for h in hp if h.get("phantom"))
          and L20b.audit()[0]["executor"]["kin_last_denied"] == "prefix≠exact-address" and all("morning" not in h["text"] for h in hp))
    hx, _ = L20b.read_entries("habit.morning", 4)                 # 精确地址 ⇒ K-in 行
    phx = [h for h in hx if h.get("phantom")]
    check("D20c 条件④满足：精确地址查询 ⇒ 渲染记录键（K-in 同址·R-in-1）", len(phx) == 1 and phx[0]["key"] == "habit.morning" and "该记忆已散失" in phx[0]["text"])
    L20c, _, _ = fresh("sigma", {**tc.load_cfg(), "g_policy": "off"})
    r20, e20 = ix.IrreversibleLedger.write_entry(L20c, "bad key/with slash", T0)
    check("D20d 条件②：地址不在 Σ（含 / 与空格）⇒ 写入口 fail-loud·0 落盘", e20 is not None and "aux-CI_key" in e20 and L20c._log_lines() == [])
    r20b, e20b = ix.IrreversibleLedger.write_entry(L20c, "habit.ok_key.v2", T0)
    check("D20e Σ 合法地址（点分标识符）放行", e20b is None and len(L20c._log_lines()) == 1)
    check("D20f 同址重写键不变（Lean addr_invariant_under_rewrite）", L20c.state().rows[1].key == "habit.ok_key.v2")

    # ---------- D21 principal 分区（kimi round7 Q4 结构性修法）----------
    cfgA = {**tc.load_cfg(), "g_policy": "off", "principal": "alice"}
    cfgB = {**tc.load_cfg(), "g_policy": "off", "principal": "bob"}
    LA, _, dA = fresh("pa", cfgA); LA.write_entry("habit.morning", T0); LA.settle(True)
    LB = ix.IrreversibleLedger(os.path.join(dA, "log.jsonl"), os.path.join(dA, "pool.json"), cfgB)   # 同账本·异 principal 读
    hb, _ = LB.read_entries("", 8)
    check("D21a 跨分区不可见：bob 读同账本 0 命中 0 幻肢（枚举 oracle 关闭）", hb == [])
    ha, _ = LA.read_entries("habit.", 4)
    check("D21b 本分区可寻址·渲染 local 分量（无 principal 前缀）", all(h["key"].startswith("habit.") and "alice/" not in h["key"] for h in ha) and len(ha) == 1)
    check("D21c 存储键带分区前缀（Σ 禁 / ⇒ 无碰撞）·账面守恒", all(e.get("key", "").startswith("alice/") for e in LA._log_lines() if e.get("ev") == "inject") and LA.state().conserved())

    # ---------- D10 冻结核心自检仍 PASS（0 改已验代码旁证）----------
    # 冻结面 selftest_mcp.py 断言 preview.10 账面语义（碑行键＝存储键·「p.b: ⟨幻肢⟩」）；
    # v3.1.1 执行器态缺省 K-out——碑行键＝查询（盲名·D19a/b 设计行为），故冻结面须在
    # DEPOSON_EXECUTOR=0（回 preview.10 账面）下跑＝验「已验代码自身仍过其自检」，
    # 冻结面文件 0 字节不动；执行器态渲染差由 D19a/D19b 覆盖。执行器态段六复现实测
    # （14:5x 手工探针）：账面 Φ=20/R=5/D=150/E⁰=225 与 preview.10 逐位同·0 原文泄漏·
    # 碑行 `p.: ⟨幻肢⟩ 此前缀下曾有 1 条散失·曾 1 字·成因 视界·不可复原`。
    mcp_dir = os.path.dirname(tc.__file__)
    _d10_env = dict(os.environ); _d10_env["DEPOSON_EXECUTOR"] = "0"
    r = subprocess.run([sys.executable, os.path.join(mcp_dir, "selftest_mcp.py")], capture_output=True, text=True, timeout=60, env=_d10_env)
    # 判据取尾行展示（preview.12 防崩）：stdout 空时回退 stderr 尾——子进程早夭（如
    # ImportError/exit 3）不再 IndexError 崩在断言展示位·"SELFTEST-PASS" 判定语义不变（fail-loud）
    _d10_tail = (r.stdout + r.stderr).strip().splitlines()[-1][:70] if (r.stdout + r.stderr).strip() else '(子进程无输出·exit=%s)' % r.returncode
    check("D10 冻结面 selftest_mcp.py SELFTEST-PASS", "SELFTEST-PASS" in r.stdout, _d10_tail)

    print("\n%s · %d/%d 断言通过" % ("ORGAN-V3.1.1-SELFTEST-PASS" if not FAIL else "ORGAN-V3.1.1-SELFTEST-FAIL",
                                    len(PASS), len(PASS) + len(FAIL)))
    if FAIL:
        print("失败项：%s" % FAIL)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
