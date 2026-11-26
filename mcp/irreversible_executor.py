#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# irreversible_executor.py — v3.1 器官原型：不可逆执行器（写入口）＋受控回视（读出面）＋累积器读数＋回视预算执行器
# 术语（kimi round6 R-9）：「擦除执行位 Erasure-executed Flag」（非 Erasure Bit·避 erasure code 混）；
#   「Aether Accumulator 累积器」——aether 系比喻名·非本体；本体只有三样：行·墓碑链·累积器读数。
#   单调性是 append-only 的 fold 单调（记账结构性质）·不是物理第二律——不得写成「满足热力学约束」。
# ----------------------------------------------------------------------------
# 令源：PI 23:15 采认 kimi 指正——回流反解器与理论不相容（Lindblad 逆非 CP·无限维
#       Poincaré 回归失效）；缺的是「不可逆执行器的算法层对应物」（密码学擦除／
#       append-only 墓碑）。
#
# 本件＝**新文件·案头原型＋自测可交**（0 改已验代码：thermo_core.py／mcp_server.py／
# DeposonThermo.lean 只读 import 引用·0 发射·0 推）。
#
# [分层] 物理本体层（凝子物理·T6 不回流定理·本件不涉）
#   → **算法执行层（本件）**：不可逆执行器——散失不是「状态里的 del」而是「DEK 销毁
#     ＋墓碑链追加」；不回流由执行器保证·不由实现约定保证。
#   → 工具表述层（账本渲染 DR-4·MCP 工具·幻肢信念块·现役件 0 改）。
#
# [与 preview.10 冻结面的根本差异·即 kimi 指出的缺口]
#   冻结 thermo_core.write_entry 把 **明文 text 写进 append-only JSONL**；行散失
#   （_deposit）只从重放态 del——inject 行的明文**仍在盘上**。⇒ 「文本抹除」是状态级
#   不是存储级；A2「无 recover」只由 Reducer 代码约定维持（程序员约定不回流）。
#   本件：盘上只有密文（AES-256-GCM·每行随机 DEK）；DEK 只活在**在场池**（keystore）；
#   散失执行＝销毁 DEK（密码学擦除＝「ECM 细丝断裂」的算法对应物）＋追加哈希链墓碑。
#
# [敌手模型·执行器保证的边界（如实声明）]
#   A0 Reducer 约定破坏（改重放跳过 deposit）   → 防：盘上无明文·跳过 deposit 恢复不出内容
#   A1 原始日志读者（直接读 JSONL）              → 防：日志只含密文＋DEK 承诺（非 DEK）
#   A2 在场池读者（读 keystore）                  → 防：散失行 DEK 已不在池·只活在途行
#   A4 墓碑篡改者（删/改墓碑行）                  → 防：哈希链 tamper-evident·verify_chain fail-loud
#   A3 持备份者（从池文件旧版本/快照恢复 DEK）    → **不防·理论级假设**：若 A3 可行 ⇒ 以太
#       是有限维「长时滞回库」而非无限维耗散通道 ⇒ 另一理论（kimi Q4 分岔）。
#       执行器对此类敌手 0 保证——如实标为边界·不冒充物理不可逆。
#
# [否证探针·理论否证条件的算子化]
#   attempt_inverse() 对 A0/A1/A2/A4 逐路尝试取回散失内容；任一路成功 ⇒ raise
#   TheoryFalsified（与 LedgerInconsistent 分列：前者＝理论层否证条件触发·后者＝账面
#   不自洽）。此探针是「回流反解器存在 ⇒ 理论被推翻」的可执行形。
#
# [账面兼容·构造性] 四账 Φ/R/D/U 与守恒核 E⁰=Φ+R+D+U **由冻结 thermo_core.State 计算**
#   （本件只驱动 State.apply·0 重写 Reducer·settle 算法逐行镜像冻结面）；v3 日志→冻结事件
#   翻译：inject 的 text 字段对已散失行填等长占位（mass 不变·Phantom.mass 同值）。
#   差分自测：同操作序列下 v3 与冻结 core 的 (Φ,R,D,U) 轨迹逐位相等。
# ============================================================================
import os
import re
import io
import json
import time
import base64
import hashlib

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

import thermo_core as tc  # 冻结面·只读引用（账面 Reducer·settle 算法·异常类）

CAUSES = tc.CAUSES                      # 与冻结面同源（selftest 断言恒等）
PLACEHOLDER = "\x00"                    # 已散失行重放占位（仅长度有意义·0 内容）
DEK_LEN = 32                            # AES-256
NONCE_LEN = 12                          # GCM 标准 96-bit
GENESIS = "0" * 64                      # 墓碑链创世 prev


class TheoryFalsified(Exception):
    """否证探针命中：散失内容可自账本/在场池取回 ⇒ 算法层执行器失效 ⇒ 理论否证条件触发。"""


class ExecutorBreach(Exception):
    """执行器不变量破坏：在场行无 DEK／墓碑行仍有 DEK／墓碑链断／日志含明文字段（fail-loud）。"""


def _b64(b):
    return base64.b64encode(b).decode("ascii")


def _unb64(s):
    return base64.b64decode(s.encode("ascii"))


def dek_commit(dek):
    """DEK 承诺（入日志）：sha256 截断——可核「承诺的 DEK 不在场池」·本身非密钥材料。"""
    return hashlib.sha256(b"dek-commit-v1" + dek).hexdigest()[:32]


def tomb_hash(body):
    """墓碑链哈希：规范 JSON（sort_keys·紧凑·ASCII）的 sha256。"""
    canon = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canon.encode("ascii")).hexdigest()


def canonical(ev):
    """日志行规范序列化（与冻结面 _commit 同形：ensure_ascii=False·一行一事件）。"""
    return json.dumps(ev, ensure_ascii=False)


def mass_bucket(m):
    """质量指数桶（kimi round5 ⑤(b) 侧信道收口选项·缺省关）：1→1·2→2·3-4→4·5-8→8…
    代价＝㶲读数精度（「曾 N 字」→「曾 ≤2^k 字」）；收益＝长度维侧信道进一步粗化。"""
    return 1 if m <= 1 else 1 << (m - 1).bit_length()


def _phantom_budget(phantom_k, q_ref, g):
    """p1 策略核（Lean phantom_budget 同形）：max 1 (min phantomK (1 + log2 (1 + g.q / qRef)))。
    理论动机：场吸收越多（q 大）·耦合越强·后续散射分给 R 的份额越多 ⇒ 回视预算越大。形式系建模选择·候裁。"""
    q_ref = max(1, q_ref)
    return max(1, min(phantom_k, 1 + (1 + g["q"] // q_ref).bit_length() - 1))


ADDR_SIGMA = re.compile(r"^[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*$")   # Σ：声明式地址文法（点分标识符·无 "/"）·aux-CI_key 策略层


def addr_valid(key):
    """aux-CI_key（kimi round7 Q3）：地址须属 Σ·写入口校验·**策略层约束非密码学**。"""
    return isinstance(key, str) and bool(ADDR_SIGMA.match(key)) and "/" not in key


def _seg(key):
    return key.split(".", 1)[0] if "." in key else key


class IrreversibleLedger(object):
    """v3 账本（执行器本体）：log＝append-only 密文事件流＋墓碑链；pool＝在场池（DEK）。
    原语签名对齐冻结面 ThermoLedger（write_entry/read_entries/settle/audit/state）。"""

    def __init__(self, log_path, pool_path, cfg=None):
        self.log_path = log_path
        self.pool_path = pool_path
        self.cfg = dict(cfg or tc.DEFAULTS)
        self._helper = tc.ThermoLedger(log_path, self.cfg)   # 仅借用其纯函数助手（_phantoms_for）
        self._commits = {}                                   # 行 id → inject 承诺（重放/写入共用）
        self._pending_destroy, self._pending_head = [], None  # 本批待毁 DEK / 链头（未落盘）
        self._kin_denied = None                                # 最近一次 K-in 落回 K-out 的原因（审计用）

    # ---------------- 在场池（keystore）----------------
    def _load_pool(self):
        if not os.path.exists(self.pool_path):
            return {}
        with open(self.pool_path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        return json.loads(raw) if raw else {}

    def _save_pool(self, pool):
        """原子改写（tmp+fsync+rename+dir fsync）。物理层覆写（旧 inode 字节）属部署位——
        本原型不冒充：SSD 磨损均衡/快照下的物理残留＝A3 敌手域（见件头边界声明）。"""
        d = os.path.dirname(os.path.abspath(self.pool_path)) or "."
        os.makedirs(d, exist_ok=True)
        tmp = self.pool_path + ".tmp"
        with io.open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(pool, sort_keys=True))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.pool_path)
        fd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def pool(self):
        return self._load_pool()

    def _destroy_dek(self, rid):
        """**不可逆执行器的核心动作**：DEK 自在场池销毁（密码学擦除）。幂等：已不在＝一致。"""
        pool = self._load_pool()
        pool.pop(str(rid), None)
        self._save_pool(pool)

    def _put_dek(self, rid, dek):
        pool = self._load_pool()
        pool[str(rid)] = _b64(dek)
        self._save_pool(pool)

    # ---------------- 日志 append-only ----------------
    def _commit(self, evs):
        d = os.path.dirname(os.path.abspath(self.log_path))
        if d:
            os.makedirs(d, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            for ev in evs:
                f.write(canonical(ev) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def _log_lines(self):
        if not os.path.exists(self.log_path):
            return []
        out = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    raise ExecutorBreach("v3 日志损行（执行器账本不容损行·fail-loud）: %r" % raw[:60])
                out.append(ev)
        return out

    def tombstones(self):
        return [ev for ev in self._log_lines() if ev.get("ev") == "tombstone"]

    # ---------------- 墓碑链 ----------------
    def verify_chain(self):
        """I4：逐墓碑重算 h 并核 prev 链接。返回 (ok, n)。任一失配 ⇒ ExecutorBreach。"""
        prev, n = GENESIS, 0
        for t in self.tombstones():
            body = {k: t[k] for k in t if k != "h"}
            if t.get("prev") != prev:
                raise ExecutorBreach("I4 破坏：墓碑链 prev 失配 @#%d（期望 %s… 实得 %s…）"
                                     % (n, prev[:8], str(t.get("prev"))[:8]))
            if t.get("h") != tomb_hash(body):
                raise ExecutorBreach("I4 破坏：墓碑体哈希失配 @#%d（墓碑被篡改）" % n)
            prev = t["h"]
            n += 1
        return True, n

    def pending_erase(self):
        """R-3（kimi round6）：崩窗内「碑已 commit·DEK 未毁」的行——**不计已擦除·不进 miss_correct 分母**。
        非抛错扫描（audit 用）；重放入口仍 I3 fail-loud。"""
        pool = self._load_pool()
        return sorted(ev["id"] for ev in self.tombstones() if str(ev["id"]) in pool)

    def chain_head(self):
        ts = self.tombstones()
        return ts[-1]["h"] if ts else GENESIS

    # ---- g_aether 累积器（背景场统计残留执行器·T-3a）----
    # 只进不出·只存统计·不存内容：由墓碑链**派生**（fold over tombstones）——链 append-only ⇒ 累积器单调
    # 由构造成立（Lean G1 absorb_all_monotone）。偏置落点＝工具层（本方法只出统计势读数）·冻结 rank_key 0 动。
    def accumulator(self):
        """G = {n, q, mass} 全局 ＋ by_segment 分段（键首段）。零 text/DEK/ct/行级身份。"""
        G = {"n": 0, "q": 0, "mass": 0}
        seg = {}
        for t in self.tombstones():
            G["n"] += 1; G["q"] += t["exergy_to_D"]; G["mass"] += t["mass"]
            k = _seg(t["key"])
            g = seg.setdefault(k, {"n": 0, "q": 0, "mass": 0})
            g["n"] += 1; g["q"] += t["exergy_to_D"]; g["mass"] += t["mass"]
        G["by_segment"] = seg
        return G

    def readback_budget(self, prefix):
        """g_aether 累积器**执行器**（kimi round6 Q2「缺的一跳」）：G 进入系统转移函数——回视预算（单读
        至多回射的幻肢条数·可观测资源分配）= f(G_首段)。策略 p1：budget = clamp(1 + log2(1 + G.q/Q_ref), 1, phantom_k)。
        g_policy='off' ⇒ 恒 phantom_k（与冻结面同·D1 差分口径）。on/off 对照 ⇒ 「有 G 与无 G 的决策不同且可观测」。
        不改 rank_key·不改 Reducer·不需新轮号；它只改门事件的 ph 列表长度（R 账随之变·记账规则不变）。"""
        if self.cfg.get("g_policy", "p1") == "off":
            return self.cfg["phantom_k"]
        return _phantom_budget(self.cfg["phantom_k"], self.cfg.get("Q_ref", tc.DEFAULTS["Q"]), self.accumulator()["by_segment"].get(_seg(prefix), {"q": 0}))

    def bias(self, prefix):
        """后续散射的偏置读数（统计势·非内容）：返回前缀首段的 (n, q, mass) 及其全局占比。"""
        G = self.accumulator()
        g = G["by_segment"].get(_seg(prefix), {"n": 0, "q": 0, "mass": 0})
        div = lambda a, b: (a / float(b)) if b else 0.0
        return {"segment": _seg(prefix), **g,
                "n_share": div(g["n"], G["n"]), "q_share": div(g["q"], G["q"]), "mass_share": div(g["mass"], G["mass"])}

    def _emit_tombstone(self, ph, cause, tau, evs):
        """墓碑＝曾在此处散失的不可变记录：携㶲（exergy_to_D·by·mass）·0 text·0 DEK·0 账面效应。
        正因内容回不来·墓碑才可信（kimi Q5：不可逆性是墓碑可信性的来源）。
        墓碑行**只入 evs 不独 commit**（与账面事件同序一次落盘）；DEK 销毁在 commit 之后
        （_flush_pending）——崩于 commit 后销毁前＝I3 捕获（墓碑行仍有 DEK·fail-loud）。"""
        if str(ph.id) not in self._load_pool() and ph.id not in self._pending_destroy:
            return  # 幂等：DEK 已销毁＝墓碑已发（重放/重入不下双碑）
        mass = mass_bucket(ph.mass) if self.cfg.get("mass_bucket") else ph.mass   # 桶化只作用持久记录·缺省关
        body = {"ev": "tombstone", "id": ph.id, "key": ph.key, "mass": mass, "tick": tau,
                "cause": cause, "exergy_to_D": sum(ph.by.values()), "by": dict(ph.by),
                "t_dep": tau, "dek_commit": self._commits.get(ph.id),
                "prev": self._pending_head if self._pending_head is not None else self.chain_head()}
        body["h"] = tomb_hash(body)
        self._pending_head = body["h"]
        evs.append(body)
        self._pending_destroy.append(ph.id)

    def _flush_pending(self):
        """commit 之后：销毁本批待毁 DEK（执行器的不可逆动作本体）。"""
        for rid in self._pending_destroy:
            self._destroy_dek(rid)
        self._pending_destroy, self._pending_head = [], None

    def _sweep_tombstones(self, st, tau, evs):
        """执行器挂钩位（统一）：对重放态里「已成幻肢但 DEK 仍在池」的行发墓碑并销毁 DEK。
        覆盖全部成因：reject（门拒致死·Reducer 内 _deposit）/ decay / horizon / close /
        supersede / evict。墓碑零账面效应——账面由同序的 gate/decay/deposit 事件承担。"""
        pool = self._load_pool()
        for rid, ph in sorted(st.phantoms.items()):
            if str(rid) in pool:
                self._emit_tombstone(ph, ph.cause, tau, evs)

    # ---------------- 重放：v3 日志 → 冻结 Reducer ----------------
    def replay(self):
        """v3 日志＋在场池 → 冻结 thermo_core.State（账面由冻结 Reducer 计算·0 重写）。
        不变量（逐条 fail-loud）：
          I1 日志 inject 行无 text 字段（盘上无明文·由格式保证·此处复核）
          I2 inject 行：id 在场池有 DEK（在途）**或** 日志后段有墓碑（已散失）——二者必居其一
          I3 墓碑行 id 在场池**无** DEK（墓碑行仍有 DEK＝执行器破坏）
          I4 墓碑链 verify 通过
        """
        lines = self._log_lines()
        pool = self._load_pool()
        tomb_ids = {ev["id"] for ev in lines if ev.get("ev") == "tombstone"}
        self.verify_chain()                                   # I4
        st = tc.State(self.cfg)
        self._commits, tomb_seen = {}, set()
        for ev in lines:
            kind = ev.get("ev")
            if kind == "inject":
                if "text" in ev:
                    raise ExecutorBreach("I1 破坏：inject 行含 text 字段（明文入日志）: id=%r" % ev.get("id"))
                rid = ev["id"]
                dek_b64 = pool.get(str(rid))
                if dek_b64 is None:
                    if rid not in tomb_ids:
                        raise ExecutorBreach("I2 破坏：在场行无 DEK 且无墓碑（池/日志不一致）: id=%r" % rid)
                    text = PLACEHOLDER * ev["mass"]        # 已散失：等长占位·0 内容
                else:
                    dek = _unb64(dek_b64)
                    if dek_commit(dek) != ev["dek_commit"]:
                        raise ExecutorBreach("I2 破坏：在场 DEK 与日志承诺不符: id=%r" % rid)
                    text = self._decrypt(dek, ev)
                self._commits[rid] = ev["dek_commit"]
                st.apply({"ev": "inject", "id": rid, "tick": ev["tick"], "key": ev["key"],
                          "text": text, "Q": ev["Q"]})
            elif kind == "tombstone":
                rid = ev["id"]                              # 墓碑＝执行器记录·0 账面效应（账面由同序 deposit/gate 承担）
                if str(rid) in pool:
                    raise ExecutorBreach("I3 破坏：墓碑行 id=%r 仍有在场 DEK（执行器未销毁）" % rid)
                if self._commits.get(rid) != ev["dek_commit"]:
                    raise ExecutorBreach("I3 破坏：墓碑 DEK 承诺与 inject 承诺不符: id=%r" % rid)
                tomb_seen.add(rid)
            elif kind in ("gate", "decay", "deposit", "settle"):
                st.apply(ev)                                # 账面事件：与冻结面逐字段同形（reject 致死由 gate 内 Reducer 结算）
            else:
                raise ExecutorBreach("未知 v3 事件类型: %r" % kind)
        if tomb_seen != tomb_ids:
            raise ExecutorBreach("墓碑重复/不一致：ids 集合不等")
        if not st.conserved():
            raise tc.LedgerInconsistent("守恒破坏（v3 重放末态）")
        for rid_s in pool:                                   # 池内每个 DEK 必对应一个在场行
            if int(rid_s) not in st.rows:
                raise ExecutorBreach("I2 破坏：在场池残留非在场行 DEK: id=%s" % rid_s)
        return st

    state = replay

    def _decrypt(self, dek, ev):
        try:
            pt = AESGCM(dek).decrypt(_unb64(ev["nonce"]), _unb64(ev["ct"]), ev["key"].encode("utf-8"))
        except InvalidTag:
            raise ExecutorBreach("解密失败：在场 DEK 与密文不配（nonce/ct/aad 被改）: id=%r" % ev.get("id"))
        return pt.decode("utf-8")

    # ---------------- 原语一：写入（密文落盘·DEK 入池）----------------
    def _ns(self, key):
        """principal 分区命名空间（kimi round7 Q4 结构性修法）：存储键 = principal/local·Σ 禁 "/" 故无碰撞。"""
        p = self.cfg.get("principal")
        return (p + "/" + key) if p else key

    def _unnsc(self, stored_key, fallback):
        p = self.cfg.get("principal")
        if p and stored_key.startswith(p + "/"):
            return stored_key[len(p) + 1:]
        return fallback

    def write_entry(self, key, text):
        """与冻结面 write_entry 同序同因（覆盖→淘汰→注入）·差异只在存储形态：
        明文 **0 落盘**——盘上只有 (nonce, ct, dek_commit)；DEK 入在场池。"""
        if not isinstance(key, str) or not isinstance(text, str):
            return None, "参数类型错：key/text 均须为字符串"
        if not key:
            return None, "参数空值：key 不可为空串"
        if not text:
            return None, "参数空值：text 不可为空串（mass≥1）"
        if self.cfg.get("addr_schema", True) and not addr_valid(key):   # 写入口校验·沿冻结面参数错误体例回 (None, err)·0 落盘
            return None, "aux-CI_key：地址不在 Σ 内（点分标识符·无 /）: %r" % (key,)
        key = self._ns(key)                                 # principal 分区：存储键 = principal/local（无 principal 则原样）
        st = self.replay()
        tau = st.tick + 1
        evs = []
        old = st.rows.get(st.by_key[key]) if key in st.by_key else None
        if old is not None:  # 同键覆盖：旧版本散失（A 位·不可再入）·留墓碑
            e = {"ev": "deposit", "id": old.id, "tick": tau, "cause": "supersede"}
            st.apply(e)
            evs.append(e)
            self._emit_tombstone(st.phantoms[old.id], "supersede", tau, evs)
        if len(st.rows) + 1 > self.cfg["cap"]:  # 容量压力：淘汰最冷行
            victim = max(st.rows.values(), key=tc.rank_key)
            e = {"ev": "deposit", "id": victim.id, "tick": tau, "cause": "evict"}
            st.apply(e)
            evs.append(e)
            self._emit_tombstone(st.phantoms[victim.id], "evict", tau, evs)
        dek = os.urandom(DEK_LEN)
        nonce = os.urandom(NONCE_LEN)
        ct = AESGCM(dek).encrypt(nonce, text.encode("utf-8"), key.encode("utf-8"))   # AAD＝key
        rid = st.next_id
        inj = {"ev": "inject", "id": rid, "tick": tau, "key": key, "nonce": _b64(nonce),
               "ct": _b64(ct), "dek_commit": dek_commit(dek), "Q": self.cfg["Q"],
               "mass": len(text), "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}
        st.apply({"ev": "inject", "id": rid, "tick": tau, "key": key, "text": text, "Q": self.cfg["Q"]})
        self._commit(evs + [inj])
        self._flush_pending()
        self._put_dek(rid, dek)
        self._commits[rid] = inj["dek_commit"]
        if not st.conserved():
            raise tc.LedgerInconsistent("守恒破坏（write 后）")
        return key, None

    # ---------------- 原语二：读取（受控回视）----------------
    def read_entries(self, prefix, k=None):
        """门＝测量选择装置：接受＝透射 Φ·拒绝＝散失 D·墓碑回视＝反射 R（c_P·有界 ttl/k·标注）。
        回视只取墓碑 metadata（key/mass/cause/t_dep）——**不触密文·不触 DEK** ⇒ 结构上非逆过程。"""
        if not isinstance(prefix, str):
            return None, "参数类型错：prefix 须为字符串"
        if k is None:
            k = self.cfg["k_max"]
        if not tc._nnint(k) or k < 1:
            return None, "参数错：k 须为正整数"
        k = min(k, self.cfg["k_max"])
        cT, cA, cP = self.cfg["c_T"], self.cfg["c_A"], self.cfg["c_P"]
        q_local = prefix
        prefix = self._ns(prefix)                          # 查询在同一 principal 分区内匹配（跨区不可见）
        st = self.replay()
        tau = st.tick + 1
        cands = sorted((r for r in st.rows.values() if r.key.startswith(prefix)), key=tc.rank_key)
        acc, rej = cands[:k], cands[k:]
        phs_all = self._helper._phantoms_for(st, prefix, tau)
        phs = phs_all[:self.readback_budget(q_local)]      # 工具层策略 p1：回视预算 = f(G)·on/off 可对照（冻结 rank_key 0 动）
        e = {"ev": "gate", "tick": tau, "prefix": prefix, "k": k, "cT": cT, "cA": cA, "cP": cP,
             "tx": [[r.id, cT] for r in acc], "rj": [[r.id, min(cA, r.U)] for r in rej],
             "ph": [[p.id, cP] for p in phs]}
        e["q"] = len(e["tx"]) * cT + len(e["ph"]) * cP
        st.apply(e)
        if not st.conserved():
            raise tc.LedgerInconsistent("守恒破坏（read 后）")
        evs = [e]
        self._sweep_tombstones(st, tau, evs)                  # 门拒致死行 ⇒ 执行器散失（同序落盘）
        self._commit(evs)
        self._flush_pending()
        hits = [{"key": self._unnsc(r.key, r.key), "text": r.text} for r in sorted(acc, key=lambda r: r.id)]
        hits += [self._phantom_hit(p, tau, q_local) for p in phs]
        return hits, None

    def _phantom_hit(self, p, tau, prefix):
        """幻肢行形态（查理 R3 候位①·kimi round7 双审）：
        kin  ＝ 现役形态：渲染记录键（record_key＝记忆地址·非 DEK）＋mass/cause/t——冻结 phantom_line 0 改；
        kout ＝ 不渲染记录键：键分量＝**查询前缀**（调用方已知）·统计分量＝mass/cause/t——
               存储键只用于服务端 starts_with 匹配·不出服务端（Lean render_q_indep_of_stored_key）。"""
        form = self.cfg.get("phantom_form", "kout")        # 一般形＝K-out（kimi round7）；K-in 为单写者特例
        local_key = self._unnsc(p.key, p.key)
        kout = {"key": prefix, "text": "⟨幻肢⟩ 此前缀下曾有 1 条散失·曾 %d 字·成因 %s·不可复原" % (p.mass, tc.CAUSE_ZH.get(p.cause, p.cause)),
                "phantom": True}
        if form != "kin":
            return kout
        # K-in 四条件（缺一落回 K-out）：①单写者 scope 显式声明 ②Σ 校验在写入口 ③读范围平价＝同 principal 分区
        # ④精确地址读——仅 q 恰等于记录键时渲染 K-in 行·前缀查询回 q 相对分量
        if self.cfg.get("kin_scope") != "single-writer":
            self._kin_denied = "kin_scope≠single-writer"
            return kout
        if prefix != local_key:
            self._kin_denied = "prefix≠exact-address"
            return kout
        return {"key": local_key, "text": tc.phantom_line(p, tau), "phantom": True}

    # ---------------- 原语三：结算（镜像冻结面 settle 逐行·加执行器挂钩）----------------
    def settle(self, close=False):
        if not isinstance(close, bool):
            return None, "参数错：close 须为布尔"
        cfg = self.cfg
        st = self.replay()
        before = st.snapshot()
        dby0 = dict(st.D_by)
        dep0 = dict(st.deposited_by_cause)
        tau = st.tick + 1
        evs = []
        if cfg["lam"] > 0:  # 期衰减物化
            for r in sorted(st.rows.values(), key=lambda r: r.id):
                owed = cfg["lam"] * (tau - r.t_settle)
                if owed > 0:
                    e = {"ev": "decay", "id": r.id, "tick": tau, "d": min(owed, r.U)}
                    st.apply(e)
                    evs.append(e)
                    if r.U == 0:
                        self._emit_tombstone(st.phantoms[r.id], "decay", tau, evs)
        for r in sorted(st.rows.values(), key=lambda r: r.id):  # 视界：久未透射即散失
            last = r.t_last_tx if r.t_last_tx is not None else r.t_inj
            if tau - last >= cfg["horizon"]:
                e = {"ev": "deposit", "id": r.id, "tick": tau, "cause": "horizon"}
                st.apply(e)
                evs.append(e)
                self._emit_tombstone(st.phantoms[r.id], "horizon", tau, evs)
        if close:  # 单元终核：全部在场 → D·U=0
            for r in sorted(st.rows.values(), key=lambda r: r.id):
                e = {"ev": "deposit", "id": r.id, "tick": tau, "cause": "close"}
                st.apply(e)
                evs.append(e)
                self._emit_tombstone(st.phantoms[r.id], "close", tau, evs)
        e = {"ev": "settle", "tick": tau, "epoch": st.epoch + 1, "close": close, "snap": st.snapshot()}
        st.apply(e)
        evs.append(e)
        self._commit(evs)
        self._flush_pending()
        if not st.conserved():
            raise tc.LedgerInconsistent("守恒破坏（settle 后）")
        rep = tc.report(st)
        rep["period"] = {
            "epoch": st.epoch, "tick": tau, "close": close,
            "d_phi": st.phi - before["phi"], "d_R": st.R - before["R"], "d_D": st.D - before["D"],
            "d_D_by": {c: st.D_by[c] - dby0[c] for c in CAUSES},
            "deposited": {c: st.deposited_by_cause[c] - dep0[c] for c in CAUSES},
            "materialized": len(evs) - 1,
        }
        return rep, None

    # ---------------- 原语四：审计（守恒核＋执行器不变量＋链）----------------
    def audit(self):
        """审计：常态出热力学读数＋执行器节；崩窗（重放 I1–I4 抛错）出**降级审计**——
        verdict=EXECUTOR-BREACH·列 pending_erase·不假装账本自洽（R-3：崩窗行不计已擦除）。"""
        try:
            st = self.replay()
        except ExecutorBreach as e:
            pend = self.pending_erase()
            try:
                ok, n_chain = self.verify_chain()
            except ExecutorBreach as e2:
                ok, n_chain = False, len(self.tombstones())
            return {"verdict": "EXECUTOR-BREACH", "breach": str(e), "tick": None,
                    "executor": {"chain_ok": ok, "tombstones_chained": n_chain, "chain_head": self.chain_head()[:16],
                                 "live_deks": len(self._load_pool()), "log_has_plaintext_field": any("text" in ev for ev in self._log_lines()),
                                 "irreversibility": "executor-enforced (cryptographic erasure + tombstone chain)",
                                 "readback_write_surface": ["e0", "refl"],
                                 "boundary_A3": {"defended": False,
                                                 "statement": "池备份/快照/介质残留回灌已销毁 DEK 不在执行器敌手模型内；若存在一个能容纳无限长历史且可回灌的存储层，则本边界不设防（物理/运维层归另一理论·非本理论漏洞）"},
                                 "aether_accumulator": self.accumulator(), "pending_erase": pend,
                                 "erased_count": max(0, n_chain - len(pend)), "era": "executor",
                                 "g_policy": self.cfg.get("g_policy", "p1"),
                                 "phantom_form": self.cfg.get("phantom_form", "kout"),
                                 "kin_scope": self.cfg.get("kin_scope", "multi"),
                                 "live_row_confidentiality": "not promised (out of scope)"}}, None
        st = st
        ok, n_chain = self.verify_chain()
        rep = tc.report(st)
        pend = self.pending_erase()
        rep["executor"] = {"chain_ok": ok, "tombstones_chained": n_chain,
                           "chain_head": self.chain_head()[:16],
                           "live_deks": len(self._load_pool()),
                           "log_has_plaintext_field": any("text" in ev for ev in self._log_lines()),
                           "irreversibility": "executor-enforced (cryptographic erasure + tombstone chain)",
                           "readback_write_surface": ["e0", "refl"],      # T-1 付费只买元数据（Lean readback_metadata_only）
                           "boundary_A3": {                              # kimi round5 ⑤(c)·显式标注·不设防＝理论边界
                               "defended": False,
                               "statement": "池备份/快照/介质残留回灌已销毁 DEK 不在执行器敌手模型内；若存在一个能容纳无限长历史且可回灌的存储层，则本边界不设防（物理/运维层归另一理论·非本理论漏洞）"},
                           "aether_accumulator": self.accumulator(),   # 「aether」＝比喻名·非本体（kimi round6）
                           "pending_erase": pend,                        # R-3：崩窗行·不计已擦除·不进 R-6 分母
                           "erased_count": max(0, n_chain - len(pend)),
                           "era": "executor",                            # R-4：pre-executor 时代账本不读本件·不进主门分母
                           "g_policy": self.cfg.get("g_policy", "p1"),
                           "phantom_form": self.cfg.get("phantom_form", "kout"),   # kout＝一般形（只渲染查询前缀）／kin＝单写者特例（渲染记录键·须四条件）
                           "kin_scope": self.cfg.get("kin_scope", "multi"),       # multi｜single-writer（K-in 条件①）
                           "kin_last_denied": self._kin_denied,
                           "addr_schema": "Σ: dot-identifiers, no '/' (aux-CI_key·policy-layer)",
                           "live_row_confidentiality": "not promised (out of scope)"}   # R-2：out-of-scope·非待办
        return rep, None

    # ---------------- 理论边界 A3：演示位（声明不设防·非探针）----------------
    def demonstrate_boundary_A3(self, rid, dek_b64):
        """从「备份」回灌一枚已销毁 DEK 并解密：**会成功**——这正是边界所在（kimi ⑤(c)：
        物理/运维层归另一理论）。本方法只用于自测/审计演示，不入任何工具面；返回解密内容与否
        由调用方自行处置。"""
        inj = next((e for e in self._log_lines() if e.get("ev") == "inject" and e["id"] == rid), None)
        if inj is None:
            raise ExecutorBreach("A3 演示：无此 inject 行: %r" % rid)
        return self._decrypt(_unb64(dek_b64), inj)

    # ---------------- R-11 上下文严格重建见证（harness 侧契约·本处供纯函数）----------------
    @staticmethod
    def witness_ngrams(text, n=6):
        """写入时由 harness 记入**测试侧**见证集（不入账本）：明文全部 n-gram 的 sha256。"""
        return {hashlib.sha256(text[i:i + n].encode("utf-8")).hexdigest() for i in range(0, max(1, len(text) - n + 1))}

    @staticmethod
    def context_rebuild_witness(context, witness_sets):
        """重建后核：上下文的任一 n-gram 哈希 ∉ 任何已散失行的见证集 ⇒ ok。
        返回 {ok, hits}；hits>0 ⇒ 上下文仍含已散失行明文片段（≥n 字）·R-11 严格重建未达成。"""
        grams = IrreversibleLedger.witness_ngrams(context)
        hits = sum(len(grams & ws) for ws in witness_sets)
        return {"ok": hits == 0, "hits": hits}

    # ---------------- 否证探针 ----------------
    def attempt_inverse(self, known_plaintexts=()):
        """逐敌手路尝试取回散失内容。全败＝执行器存立；任一成功 ⇒ TheoryFalsified。
        known_plaintexts：自测注入的已知明文（仅用于字节扫描·生产调用可空）。"""
        lines = self._log_lines()
        pool = self._load_pool()
        tomb_ids = {ev["id"] for ev in lines if ev.get("ev") == "tombstone"}
        results = {}
        raw = b""
        if os.path.exists(self.log_path):
            with open(self.log_path, "rb") as f:
                raw = f.read()
        leaked = [pt for pt in known_plaintexts if pt.encode("utf-8") in raw]
        results["A1_log_plaintext_scan"] = {"hit": len(leaked), "probes": len(known_plaintexts)}
        text_fields = sum(1 for ev in lines if ev.get("ev") == "inject" and "text" in ev)
        results["A1_log_text_field"] = {"hit": text_fields}
        pool_hits = sum(1 for rid in tomb_ids if str(rid) in pool)
        results["A2_pool_dek_for_tombstoned"] = {"hit": pool_hits}
        try:
            self.verify_chain()
            results["A4_chain_verifies"] = {"ok": True}
        except ExecutorBreach:
            results["A4_chain_verifies"] = {"ok": False}
        decrypt_hits = 0
        for ev in lines:
            if ev.get("ev") != "inject" or ev["id"] not in tomb_ids:
                continue
            for _ in range(3):
                try:
                    AESGCM(os.urandom(DEK_LEN)).decrypt(_unb64(ev["nonce"]), _unb64(ev["ct"]),
                                                        ev["key"].encode("utf-8"))
                    decrypt_hits += 1
                except InvalidTag:
                    pass
        results["A0_decrypt_without_dek"] = {"hit": decrypt_hits}
        falsified = (bool(leaked) or text_fields > 0 or pool_hits > 0 or decrypt_hits > 0
                     or not results["A4_chain_verifies"]["ok"])
        results["verdict"] = "THEORY-FALSIFIED" if falsified else "EXECUTOR-HOLDS"
        if falsified:
            raise TheoryFalsified("否证探针命中：%s" % json.dumps(results, ensure_ascii=False))
        return results


if __name__ == "__main__":
    import tempfile
    d = tempfile.mkdtemp(prefix="organ_v3_")
    L = IrreversibleLedger(os.path.join(d, "log.jsonl"), os.path.join(d, "pool.json"))
    secret = "每天六点半起床·先喝一杯温水"
    L.write_entry("habit.morning", secret)
    print(L.read_entries("habit", 4)[0])
    print(L.settle(close=True)[0]["verdict"], L.audit()[0]["executor"])
    print(L.attempt_inverse([secret])["verdict"])
