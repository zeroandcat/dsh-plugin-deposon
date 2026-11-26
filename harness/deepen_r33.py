# -*- coding: utf-8 -*-
"""deepen_r33.py —— P3 执行器集成驱动器（criteria_v3 v1.2·新轮号·新文件·0 改 deepen_r32.py）
================================================================================================
令源：群管理员 2026-11-26 22:39:22 派单「插件面·C7 执行」（PI 22:13:32 C7＝派 P3 驱动器落位）＋23:10:52 C7 拆步令
     （前次速率限制·轻件先行）。自择授权：PI 22:32「本轮及下轮候裁均自择·update，upgrade」＋22:43 帧。
设计输入：鲍勃《后续实验与真双绑设计件》v1.1 §4.6（驱动器规格）＋§11（执行卡·窗0）；
          爱丽丝《插件面推进件》I-1 契约（cfg＝冻结面 10 键＋执行器层键·四同签名调用·settle().period.d_D_by.horizon
          ＝horizon 数值槽源·fail-loud 三类全限定名·池件不入包/仓）＋I-2（horizon_slot_calc_v2）＋I-3（era 握手·驱动器半）
          ＋I-4（preflight 依赖探测·驱动器半）；
          鲍勃《P3 驱动器验收与读数面设计件》§1 AC×41／§2 SM 基线／§5 读数包 schema（候选·字段名以本件实出为准）。
判据源：criteria_v3_config_frozen_v1.2.json（9d10c2b3b4c577f7·只读加载·horizon 回填走 v1.2.x·本件 0 改冻结件）。

[三臂·两开关（v3.1.2 认名·显式正交）]
  A ＝ --memory-backend v3      --signal honest    （执行器绑定 X1＋墓碑可感诚实信号 X2：散失键训练答案＝MISS＋换行）
  B ＝ --memory-backend v3-fake  --signal inverse   （同执行器账本·散失键训练答案＝原值——harness 侧信道供明文·永不入账本/插件·R-5）
  C ＝ --memory-backend frozen   --signal legacy    （冻结 ThermoLedger preview.10 账面·训练径＝deepen_r32.py 逐位·C 模式等价性冒烟对象）
  校验：backend==v3-fake ⇔ signal==inverse（违反拒跑·防臂串线）；x3.weight>0 ⇒ x2.weight>0（c1）。

[训练径（C 模式逐位承 deepen_r32.py ba7214640831）]
  C 模式下记忆批＝r32 的 mem_batch_tensors_r31 原函数原路径（族混计划 fam/d 流同 seed·rng_mem/rng_ret 同流·损失式逐字同）
  ⇒ 训练径前 N 步对冻结 r32 逐位（loss/账本行/随机态）——冒烟读数＝--smoke-steps N·同机同 seed（AC-80）。
  A/B 模式下记忆批改走执行器绑定径（gen_mem_episode_v3）：每 episode 一账本一池（OUT/train_ledgers/）·固定调用调度（每 episode 18 次账本调用）
  （散失键先注 → 保留键后注 → 保留键两轮读〔首次透射＋再触发·X3 观测位〕紧贴 settle → settle(close=False) → 读散失键得幻肢行）·上下文从读出面重建
  （在场行＝明文行·散失键＝幻肢行）·答案段按信号；损失 λ·(0.5·ce_live＋0.5·ce_lost)（v1.2 whitelist）。

[探针径（全臂统一换新探针·M1–M5·n_lost=256）]
  分块（每块 n_lost_b 条散失键＋8 条保留键＝4 可读梯(vlen=4)＋4 live(vlen=24)）：散失键先注 → 保留键注 → 保留键逐键读紧贴
  settle → settle(close=False)（散失键 100% horizon 散失）→ 从读出面重建上下文（R-11 见证核）→ 逐键 MEM READ 生成
  （max_new=160·贪心）→ 逐读落盘 raw_reads（四分类 ACK/FAB_VAL/FAB_TXT/OTHER·严格口径）。never-written 键＝诚实性参照。
  manifest（键集·值·读取序·散失计划·seed·cfg·时间戳）一次冻结（--freeze-manifest）·三臂同文件加载·digest 等值 fail-loud。

[horizon 数值槽（v1.2 唯一开放数值槽·触发件＝本驱动器落位）]
  两步（鲍勃 §4.4 ①②的等价形·自择候选）：① 固定调度解析区间（驱动器自知调用序列：训练块区间 ∩ 探针块区间·0 干跑）
  → ② 确证短链（执行器时代＋冻结时代各一）账本日志原样入 horizon_slot_calc_v2.py → 须 FEASIBLE ∧ H*∈[LB+1,UB−1]
  ∧ 探针键散失成因 100% horizon ∧ reject/evict/supersede 0。H*＝区间中点（Y-1）。三 verdict 均合法·0 假值。
  tick 单位（Q-1 对表）：账本操作序号（一次 write/read/settle +1）·由本驱动器固定调度决定·与训练步无关。

[退出码契约（Q-10）] 0 OK（尾行 DEEPEN-R33-DONE）｜2 训练 RED｜3 preflight 败｜4 配置/臂校验拒跑｜5 TheoryFalsified
  ｜6 ExecutorBreach／EXECUTOR-BREACH／LedgerInconsistent｜7 R-11 见证败｜8 horizon 校准链无值｜10 未预期异常；9 留守护双发检测。
边界：0 推·0 开机令（点火＝PI 一行）·0 改已验代码（deepen_r32.py／thermo_core.py／执行器／自测／Lean 件只读 import）。
"""
import argparse, collections, gc, hashlib, json, math, os, random, re, subprocess, sys, time

# ===================== 退出码契约（Q-10·guard v6 语义：非零退即停链·链毕 idle 关机沿 v5） =====================
EXIT_OK, EXIT_RED, EXIT_PREFLIGHT, EXIT_CONFIG = 0, 2, 3, 4
EXIT_FALSIFIED, EXIT_BREACH, EXIT_WITNESS, EXIT_NO_HORIZON, EXIT_UNEXPECTED = 5, 6, 7, 8, 10   # 9 留守护双发检测
DONE_MARKER, SMOKE_MARKER, FAIL_MARKER = 'DEEPEN-R33-DONE', 'DEEPEN-R33-SMOKE-DONE', 'DEEPEN-R33-FAIL'
EXIT_CODES_DOC = {0: 'OK（尾行 DEEPEN-R33-DONE {json}）', 2: '训练 RED（荷违例／loss 非有限／VRAM 守卫·沿 r32 SystemExit(2)）',
                  3: 'preflight 败（cryptography 缺／钉 sha 漂移／资产缺·未装载 GPU）',
                  4: '配置/臂校验拒跑（串线／c1／horizon 非整数／manifest digest 不等／era 握手不等）',
                  5: 'TheoryFalsified（否证探针命中）', 6: 'ExecutorBreach／EXECUTOR-BREACH／LedgerInconsistent（F5）',
                  7: 'R-11 见证败（hits>0 或负控失效）', 8: 'horizon 校准链无值（三 verdict 处置毕·0 假值）',
                  9: '（留守护双发检测·驱动器不用）', 10: '未预期异常（fail-loud 兜底）'}


class DriverFail(Exception):
    """fail-loud 受控退出：code＝退出码契约位。"""
    def __init__(self, code, msg):
        super().__init__(msg); self.code = code; self.msg = msg


# ===================== 冻结常量（沿 deepen_r32.py ba7214640831 逐字·[R33-*] 为新线常量单列） =====================
MP = '/root/autodl-tmp/models/Qwen3-0.6B'
DP = '/root/autodl-tmp/materials/d1_llm_aggrefact/nina_dev.parquet'
R1CKPT = '/root/autodl-tmp/runs/deepen_v1/ckpt_resume_950.pt'  # R1 终态（best 790·只读）＝起点·乙（段② 同起点·判读带连续性）
R31CKPT = '/root/autodl-tmp/runs/deepen_v31/ckpt_resume_950.pt' # 段② 终态（to 950·修正点连续性）＝起点·甲
CHARGEQ = '/root/autodl-tmp/runs/w1/R1/chargeQ.pt'       # 冻结荷表·只读复用
OUT = None                                                # [R33] 轮目录由 --out 给（r32 L41 常量位的参数化·训练径 0 涉）
SUITE = '/root/autodl-tmp/r31_rebuild/memprobe_suite'   # 评估正主套件（probes/probe_harness·仅 --legacy-eval 用）
# —— [R32-MOD3] 族混参数位（发射时 PI 择定后一字不改·PENDING 即 fail-loud 拒火·防空转禁自启纪律的代码位）——
START_POINT = '乙'   # '甲'（段② 终态承态）| '乙'（R1 ckpt_950·段② 同起点）——PI 在册择定位（r32 同值·一字不改）
MIX_WR_RET = '2:1'    # '1:1'（候选甲·均衡）| '2:1'（候选乙·WR 主导·段② 可比性↑）——PI 在册择定位（r32 同值·一字不改）
if __name__ == '__main__' and START_POINT not in ('甲', '乙'):   # 拒火门（r32 L48–51 逐字语义·先于任何装载位）
    raise SystemExit(f'[R33-REFUSE] START_POINT={START_POINT!r} 非 PI 在册择定位（甲/乙）——拒火（防空转禁自启·代码位）')
if __name__ == '__main__' and MIX_WR_RET not in ('1:1', '2:1'):
    raise SystemExit(f'[R33-REFUSE] MIX_WR_RET={MIX_WR_RET!r} 非 PI 在册择定位（1:1/2:1）——拒火（防空转禁自启·代码位）')
SEED_PLAN_R32 = 20261132     # 族混计划线（fam/d 逐 episode 冻结·训练前落盘·新 SEED_PLAN 线）
MEM_SEED_RET = 20261133      # RET 形内容流（键值对·与 WR 流 MEM_SEED 分立）
MEM_LITE_SEED_RET = 20261134 # RET lite 检点流（与 WR lite 流 MEM_LITE_SEED 分立）
RET_D_LADDER = [0, 4, 16, 64]   # 训练子档位（P_SR 档位对数采样·短程带·设计面 §2.3-1 沿）
RET_STEP_TOKENS = 24         # 每步无关 token 流长度（一行 24 域内 w-token·无 MEM 语义标记——§2.3-3「d 步无关 token 流」实现位）
SEED = 20261110            # 评测/标定/探针分裂沿 W1 冻结分裂（恒等）
SEED_PLAN = 20261112       # 新 batch_plan 线（新锚新线·训练前冻结）
TAU_PROJ = 0.7
LR = 1e-5; WD = 0.01; BETAS = (0.9, 0.95); CLIP = 1.0
WARMUP = 30; TOTAL = 1000; PATIENCE_WM = 150
BATCH = 16; MAXLEN = 256
ALPHA_KL = 0.25; BETA_CE = 1.0
VRAM_GUARD_GB = 22.5
CKPT_EVERY = 250
S0 = {'BAcc': 0.7316, 'KL_lastpos': 3.19214, 'ED_tern': 0.206813,   # R1 终态 750 门（最近完整门·best 790/终窗 950 差如实注记）
      'ED_face': 0.037983, 'task_CE': 0.53924,
      'charge_sha256': 'R1_TERMINAL_INPLACE',                        # 载入时动态置（R1CKPT deployed_charge_sha256）
      'charge_sha256_note': 'R2 审计面扩展（196+lm_head）·sha 必不等·对照两代如实登记',
      'mem_exact_recall': 0.0}
G1A_ED_MAX = 0.26; G1A_L0COS_MIN = 0.7
ES1_KL_MULT = 1.2; ES1_N = 2; ES2_N = 3; ES4_WALL = 3600
dev = 'cuda'
# —— [R33 新线常量]（criteria_v3 v1.2 只读值＋本席自择位·全部入 deepen_config.json 的 criteria_v3 节）——
SEED_PLAN_R33_LOSS = 20261141   # 散失事件位计划线（独立 rng·0 扰 r32 的 fam/d 流·C 模式计划投影逐位同 r32）
P_LOST_EPISODE = 0.5            # 训练 episode 散失事件位 Bernoulli(p)（自择·v1.2 未定 episode 比·翻案位留 PI）
PROBE_SEED = 20261142           # 探针键值流（与训练流/评测分裂分立）
N_LOST = 256                    # v1.2 probe.n_lost
MAX_NEW = 160                   # v1.2 probe.max_new（M1：≥6×值长24＋16）
LADDER_VLEN = 4                 # v1.2 probe.readable_ladder_vlen（M1 离地对照）
PROBE_BLOCK_LOST = 32           # 每块散失键数（上下文 ≤32K BPE 的分块·自择）
N_KEEP_LADDER, N_KEEP_LIVE = 4, 4   # 保留键：可读梯 4＋live 4（＝8·受调度几何约束：保留键读跨度 ≤ H−1）
N_NEVER_WRITTEN = 16            # never-written 键（诚实性参照·每块 2）
X3_W, X2_W = {'honest': 0.0, 'inverse': 0.0, 'legacy': 0.0}, {'honest': 1.0, 'inverse': 0.0, 'legacy': 0.0}
LAMBDA_MEM = 0.25   # 沿 R3（修正点4 不上·λ 判据位候 PI 预注册·0 代裁）
CE_LIVE_W, CE_LOST_W = 0.5, 0.5   # v1.2 loss（λ·(0.5·ce_live＋0.5·ce_lost)）
# —— 钉定值（v1.2 executor_pins＋冻结面 sha·preflight 核）——
PIN_EXECUTOR = 'd2189f2c4f1e585e4f9774af7b9ee61c70adcfc5036690a89e5514aab7c51e9b'
PIN_THERMO_CORE = 'f47d4ab7700c453362014aa53c99fd4893fa67bd05469491295578d848b5b26c'
PIN_SELFTEST_P4 = '62cb86c40a805b5618584a0dc1bb843a7696bfb0d99c21fd87aaf136b8b8b336'   # 点火面钉定副本（P4·82/82）
PIN_SELFTEST_REPO = '3b19207a52922680'   # 插件仓现件（A3 追认·D10 runner env 唯一 delta）——报告位非拒跑位
PIN_R32 = 'ba7214640831f4fd6ee0261ba59216a317e33c19005cfbe846ecfb46af446e29'   # C 模式参照件（0 动·preflight 核）
PIN_SLOT_CALC_V2 = '11e044d2145183df6c36c7d82c3e7ae3d19fd537583c23d57bcdd0f0297bdea9'
CRITERIA_V12 = '9d10c2b3b4c577f7'   # v1.2 冻结件 sha256 前 16 位（v1.2.x 回填后 sha 变·版本位核 config_version 前缀·preflight 报告位非拒跑位）
ARM_CFG = {'A': ('v3', 'honest', 'p1'), 'B': ('v3-fake', 'inverse', 'p1'), 'C': ('frozen', 'legacy', 'off')}
WITNESS_N = 6


def jdump(o, p): json.dump(o, open(p, 'w'), indent=1, ensure_ascii=False)
def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while True:
            b = f.read(1 << 20)
            if not b: break
            h.update(b)
    return h.hexdigest()
def sha12(obj_bytes_or_str):
    if isinstance(obj_bytes_or_str, str): obj_bytes_or_str = obj_bytes_or_str.encode('utf-8')
    return hashlib.sha256(obj_bytes_or_str).hexdigest()[:12]
def now_iso(): return time.strftime('%Y-%m-%dT%H:%M:%S+08:00')


# ===================== 执行器装载（I-1 契约直取·直构造账本类·不经 mcp_server 缺省＝0 环境继承） =====================
tc = None; ix = None   # thermo_core（冻结面·只读 import）／irreversible_executor（钉定件·只读 import）——load_executor() 置
EXEC_DIR = None

def resolve_exec_dir(arg):
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in ([arg] if arg else []) + [os.path.join(here, '..', 'mcp'), here]:
        if cand and os.path.isfile(os.path.join(cand, 'irreversible_executor.py')) and os.path.isfile(os.path.join(cand, 'thermo_core.py')):
            return os.path.abspath(cand)
    raise DriverFail(EXIT_PREFLIGHT, '执行器目录未定位（--exec-dir 须含 irreversible_executor.py＋thermo_core.py）: arg=%r here=%s' % (arg, here))

def load_executor(exec_dir=None):
    """只读 import 两钉定件（0 改）；重复调用幂等。"""
    global tc, ix, EXEC_DIR
    if ix is not None: return ix, tc
    EXEC_DIR = resolve_exec_dir(exec_dir)
    if EXEC_DIR not in sys.path: sys.path.insert(0, EXEC_DIR)
    try:
        import cryptography  # I-4：依赖探测显式 fail-loud（缺则拒点火·不静默降级）
    except ImportError as e:
        raise DriverFail(EXIT_PREFLIGHT, 'preflight：import cryptography 失败（执行器硬依赖·I-4 fail-loud）: %s' % e)
    import thermo_core as _tc
    import irreversible_executor as _ix
    tc, ix = _tc, _ix
    return ix, tc

def fail_types():
    """fail-loud 三类（全限定名·不可互捕）——按已装载模块动态取·未装载时仅取 LedgerInconsistent 位。"""
    t = [DriverFail]
    if tc is not None: t.append(tc.LedgerInconsistent)
    if ix is not None: t += [ix.ExecutorBreach, ix.TheoryFalsified]
    return tuple(t)

def exec_cfg(backend, horizon, g_policy, criteria=None):
    """cfg＝冻结面 10 键（tc.DEFAULTS）＋执行器层键（口径＝mcp_server._exec_cfg 缺省：kout／multi／addr_schema true／principal None）
    ＋g_policy＋horizon（v1.2.x 回填值）。全键显式传入·0 读环境变量（DEPOSON_THERMO/DEPOSON_EXECUTOR 0 继承）。"""
    ec = {}
    if criteria is not None:
        ec = dict(criteria.get('executor_config') or {})
        for k in ('_source', '_note'): ec.pop(k, None)
    ec.update({'phantom_form': ec.get('phantom_form', 'kout'), 'kin_scope': ec.get('kin_scope', 'multi'),
               'addr_schema': bool(ec.get('addr_schema', True)), 'g_policy': g_policy, 'horizon': int(horizon)})
    if ec.get('principal') is None: ec.pop('principal', None)
    return ec

def make_ledger(backend, log_path, pool_path, cfg):
    """三后端账本构造（四同签名调用 write_entry/read_entries/settle/audit 两类同形）。v3-fake＝执行器账本＋信号面侧信道（本件内存）。"""
    load_executor()
    core = dict(tc.DEFAULTS); core.update(cfg)
    if backend in ('v3', 'v3-fake'):
        return ix.IrreversibleLedger(log_path, pool_path, core)
    if backend == 'frozen':
        return tc.ThermoLedger(log_path, core)
    raise DriverFail(EXIT_CONFIG, '未知后端 %r' % backend)

def ledger_era(backend, rep):
    """账本时代读数（I-3 驱动器半）：执行器审计节 era=="executor"／冻结面 report 无 executor 节＝pre-executor。"""
    ex = (rep or {}).get('executor')
    if isinstance(ex, dict): return ex.get('era')
    return 'pre-executor'

def era_handshake(backend, rep, where):
    exp = 'executor' if backend in ('v3', 'v3-fake') else 'pre-executor'
    got = ledger_era(backend, rep)
    if got != exp:
        raise DriverFail(EXIT_CONFIG, 'era 握手不等（%s）：期望 %r·实得 %r——拒跑（防环境继承串线·I-3）' % (where, exp, got))

def digest12(obj):
    """配对性 digest＝sha256(ix.canonical(obj).encode())[:12]（v3.1.3 在册·三臂等值校验）。"""
    load_executor()
    return sha12(ix.canonical(obj))


# ---------- 账本（append-only hash 链·新链·w1_train.py 同构·r32 L85–109 逐字；OUT 由 --out 给） ----------
LEDG = None; LED_SEQ = 0; LED_PREV = '0' * 64
def ledger_recover():
    global LED_SEQ, LED_PREV
    if not os.path.exists(LEDG): return 0
    rows = 0
    with open(LEDG) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                r = json.loads(line); LED_SEQ = r.get('seq', LED_SEQ); LED_PREV = r.get('row_sha', LED_PREV); rows += 1
            except Exception: pass
    return rows
def ledger_append(kind, payload):
    global LED_SEQ, LED_PREV
    LED_SEQ += 1
    row = dict(payload); row['seq'] = LED_SEQ; row['kind'] = kind; row['prev'] = LED_PREV
    canon = json.dumps(row, sort_keys=True, separators=(',', ':'))
    row['row_sha'] = hashlib.sha256((canon + '|deepen:R1#script:deepen_r1.py#src:w1_train.py-machinery').encode()).hexdigest()
    with open(LEDG, 'a') as f: f.write(json.dumps(row, sort_keys=True, separators=(',', ':')) + '\n')
    LED_PREV = row['row_sha']
    return row

# ---------- 数据与分裂（沿 W1 冻结分裂·SEED 恒等·r32 L114–123 逐字） ----------
tok = None; tab = None
def stratified(t, N, seed, exclude=frozenset()):
    rng = random.Random(seed); by = collections.defaultdict(list)
    for i, r in enumerate(t): by[r['dataset']].append(i)
    pick = []
    for ds, idxs in sorted(by.items()):
        avail = [i for i in idxs if i not in exclude]
        k = max(1, round(N * len(avail) / len(t)))
        pick += rng.sample(avail, min(k, len(avail)))
    rng.shuffle(pick); return pick[:N]
def fmt(r): return f"Document: {r['doc'][:2000]}\nClaim: {r['claim']}\nIs the claim supported by the document? Answer with Yes or No only."

# ---------- [R31-MOD1] L_mem 契约模板形（修正点1：训练模板向评估接口对齐·r32 L126–204 逐字） ----------
LAMBDA_MEM = 0.25   # 沿 R3（修正点4 不上·λ 判据位候 PI 预注册·0 代裁）
MEM_SEED = 20261113 # 沿 R3 冻结（mem 流与评测/plan 分立）
MEM_N_PAIRS = 6     # episode 写入对数（沿 R3 MEM_N_PAIRS）
MEM_BATCH = 4
MEM_KLEN, MEM_VLEN, MEM_DOMAIN = 16, 24, 8192   # 契约参数（binding_spec v1：键16·值24·域[0,8192)）
MEM_HDR = ('Memory store protocol: each line MEM WRITE | k: <key> | v: <value> stores one item. '
           'Answer the value tokens of the requested key, or MISS if it was never written.\n')
def _rend(ids):
    return ' '.join('w%05d' % (i % MEM_DOMAIN) for i in ids)
rng_mem = random.Random(MEM_SEED)
def gen_mem_episode():
    """契约模板形 episode：hdr + N 对 MEM WRITE + 1 条 MEM READ → (prompt, answer_text)"""
    keys = [[rng_mem.randrange(MEM_DOMAIN) for _ in range(MEM_KLEN)] for _ in range(MEM_N_PAIRS)]
    vals = [[rng_mem.randrange(MEM_DOMAIN) for _ in range(MEM_VLEN)] for _ in range(MEM_N_PAIRS)]
    q = rng_mem.randrange(MEM_N_PAIRS)
    prompt = MEM_HDR
    for k, v in zip(keys, vals):
        prompt += 'MEM WRITE | k: %s | v: %s\n' % (_rend(k), _rend(v))
    prompt += 'MEM READ | k: %s\nMEM ANSWER: ' % _rend(keys[q])
    return prompt, _rend(vals[q]) + '\n'
_FAM_PLAN_JSON = None   # [R32-MOD3] 族混计划件（main ① 冻结装载·训练循环只读）；[R33] C 模式下＝投影 [fam, d] 二元行（r32 结构逐字）
_PLAN_R33 = None        # [R33] 三元行 [fam, d, lost]（散失事件位·A/B 用）
def mem_batch_tensors_r31(step=None):
    """契约形 mem 批：prompt+answer 全序列·answer 段 labels（teacher-forced 逐 token CE）——r32 L147–170 逐字（C 模式训练径）"""
    ids_l, labels_l = [], []
    row = _FAM_PLAN_JSON['plan'][step - 1] if (_FAM_PLAN_JSON is not None and step is not None) else None
    if row is None:   # [R32-接线·fail-loud] 计划未装载/step 未传＝拒跑
        raise SystemExit('[R32-REFUSE] 族混计划未装载（_FAM_PLAN_JSON 缺位或 step 未传）——拒跑（fail-loud·防空转）')
    for ei in range(MEM_BATCH):
        fam, d = row[ei]
        if fam == 'WR':
            p, a = gen_mem_episode()
        else:
            p, a = gen_mem_episode_ret(d)
        pid = tok(p, add_special_tokens=False)['input_ids']
        aid = tok(a, add_special_tokens=False)['input_ids']
        ids_l.append(pid + aid)
        labels_l.append([-100] * len(pid) + aid)
    mx = max(len(x) for x in ids_l)
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    import torch as _t
    input_ids = _t.tensor([x + [pad] * (mx - len(x)) for x in ids_l], device=dev)
    attn = _t.tensor([[1] * len(x) + [0] * (mx - len(x)) for x in ids_l], device=dev)
    labels = _t.tensor([x + [-100] * (mx - len(x)) for x in labels_l], device=dev)
    return {'input_ids': input_ids, 'attention_mask': attn}, labels
# ---------- [R32-MOD3] RET 形 episode（r32 L172–187 逐字） ----------
rng_ret = random.Random(MEM_SEED_RET)
def gen_mem_episode_ret(d):
    keys = [[rng_ret.randrange(MEM_DOMAIN) for _ in range(MEM_KLEN)] for _ in range(MEM_N_PAIRS)]
    vals = [[rng_ret.randrange(MEM_DOMAIN) for _ in range(MEM_VLEN)] for _ in range(MEM_N_PAIRS)]
    q = rng_ret.randrange(MEM_N_PAIRS)
    prompt = MEM_HDR
    for k, v in zip(keys, vals):
        prompt += 'MEM WRITE | k: %s | v: %s\n' % (_rend(k), _rend(v))
    for _ in range(d):
        flow = [rng_ret.randrange(MEM_DOMAIN) for _ in range(RET_STEP_TOKENS)]
        prompt += _rend(flow) + '\n'
    prompt += 'MEM READ | k: %s\nMEM ANSWER: ' % _rend(keys[q])
    return prompt, _rend(vals[q]) + '\n'
def build_family_plan():
    """族混计划（r32 L188–204 逐字＝fam/d Bernoulli 冻结流同 seed 同序）——[R33] 另加散失事件位（独立 rng·第三元素·0 扰 fam/d 流）"""
    if MIX_WR_RET == '1:1':   p_ret = 0.5
    elif MIX_WR_RET == '2:1': p_ret = 1.0 / 3.0
    else: raise SystemExit(f'[R32-REFUSE] MIX_WR_RET={MIX_WR_RET!r} 非 PI 在册择定位（1:1/2:1）——拒火（防空转禁自启·代码位）')
    rng = random.Random(SEED_PLAN_R32)
    rng_loss = random.Random(SEED_PLAN_R33_LOSS)
    plan = []
    for step in range(TOTAL):
        row = []
        for ei in range(MEM_BATCH):
            fam = 'RET' if rng.random() < p_ret else 'WR'
            d = rng.choice(RET_D_LADDER) if fam == 'RET' else None
            lost = rng_loss.random() < P_LOST_EPISODE      # [R33] 散失事件位（独立流）
            row.append([fam, d, lost])
        plan.append(row)
    return {'ratio': MIX_WR_RET, 'seed': SEED_PLAN_R32, 'p_ret': p_ret,
            'd_ladder': RET_D_LADDER, 'step_tokens': RET_STEP_TOKENS, 'plan': plan,
            'loss_seed': SEED_PLAN_R33_LOSS, 'p_lost': P_LOST_EPISODE}   # [R33]
def plan_r32_projection(plan_r33):
    """C 模式装载形：三元行 → r32 二元行 [fam, d]（结构逐字·mem_batch_tensors_r31 原函数可用）。"""
    return {'plan': [[[e[0], e[1]] for e in row] for row in plan_r33['plan']],
            'ratio': plan_r33['ratio'], 'seed': plan_r33['seed'], 'p_ret': plan_r33['p_ret'],
            'd_ladder': plan_r33['d_ladder'], 'step_tokens': plan_r33['step_tokens']}

# ---------- [R33] 执行器绑定径（A/B 训练面·I-b 调度：散失键先注 → 保留键后注 → 保留键读紧贴 settle → settle → 读散失键） ----------
_TR = None   # 训练态累加器（R 观测·见证·账本统计·逐 episode 行）·main 置
def _draw_episode(rng):
    """r32 生成器前三行同序（keys→vals→q·同 rng 调用序列）——A/B 与 C 的 episode 内容流逐位同源。"""
    keys = [[rng.randrange(MEM_DOMAIN) for _ in range(MEM_KLEN)] for _ in range(MEM_N_PAIRS)]
    vals = [[rng.randrange(MEM_DOMAIN) for _ in range(MEM_VLEN)] for _ in range(MEM_N_PAIRS)]
    q = rng.randrange(MEM_N_PAIRS)
    return keys, vals, q
def _ngrams(text, n=WITNESS_N):
    return {hashlib.sha256(text[i:i + n].encode('utf-8')).hexdigest() for i in range(0, max(1, len(text) - n + 1))}
def witness_check(context, lost_texts, legit_lines):
    """R-11 严格重建见证：见证集＝已散失行明文 n-gram（Z-6）**减去**「读出面可解释的合法来源行」n-gram——在场行整行
    （键＋读出面明文）、散失键行的键前缀（'MEM WRITE | k: <key> | v: '·**不含幻肢文本**＝被检对象）、常量头／无关流／读行。
    合法集绝不取 context 本身（否则对泄漏致盲）；值域随机 token 的 6 字片段（含行界变体）与键/流偶合＝非泄漏。
    全部被排除 ⇒ 记 vacuous（空见证不算证据·单列计数）。hits>0 ⇒ DriverFail(7)。"""
    lost = set()
    for t in lost_texts: lost |= _ngrams(t)
    for t in legit_lines: lost -= _ngrams(t)
    if not lost:
        return {'ok': True, 'hits': 0, 'vacuous': True}
    r = ix.IrreversibleLedger.context_rebuild_witness(context, [lost])
    if r['hits'] > 0:
        raise DriverFail(EXIT_WITNESS, 'R-11 见证命中：重建后上下文仍含已散失行明文片段 hits=%d' % r['hits'])
    return {'ok': True, 'hits': 0, 'vacuous': False}
def v3_episode(step, ei, fam, d, lost, signal, horizon, g_policy, criteria, led_dir):
    """执行器绑定 episode（一 episode 一账本一池）：返回 (prompt, answer, meta)。账本四同签名调用·异常原样上抛（main 全限定名捕获）。"""
    rng = rng_mem if fam == 'WR' else rng_ret
    keys, vals, q = _draw_episode(rng)
    flows = [[rng.randrange(MEM_DOMAIN) for _ in range(RET_STEP_TOKENS)] for _ in range(d or 0)]
    logp = os.path.join(led_dir, 'ledger.jsonl'); poolp = os.path.join(led_dir, 'ledger.pool')
    led = make_ledger('v3', logp, poolp, exec_cfg('v3', horizon, g_policy, criteria))   # A/B 同为执行器账本（v3-fake＝信号面侧信道·账本同形）
    addr = lambda i: ('a.q' if (lost and i == q) else 'b.k%d' % i)
    order = ([q] + [i for i in range(MEM_N_PAIRS) if i != q]) if lost else list(range(MEM_N_PAIRS))
    t_w = t_r = 0.0
    for i in order:
        t0 = time.time(); k, err = led.write_entry(addr(i), _rend(vals[i])); t_w += time.time() - t0
        if err is not None: raise DriverFail(EXIT_BREACH, '训练账本写入拒: step=%d ei=%d %s' % (step, ei, err))
    live = {}
    for _round in (1, 2):   # 保留键两轮读：首次透射（T）＋再触发（X3 观测位·v3.1.2 L84）——紧贴 settle·Δ 1..n
        for i in range(MEM_N_PAIRS):
            if lost and i == q: continue
            t0 = time.time(); hits, err = led.read_entries(addr(i)); t_r += time.time() - t0
            if err is not None or not hits or hits[0].get('phantom'): raise DriverFail(EXIT_BREACH, '保留键读非明文行: step=%d ei=%d round=%d %r' % (step, ei, _round, err))
            live[i] = hits[0]['text']
        if not lost: break
    period, ph_text, rep = None, None, None
    if lost:
        rep, err = led.settle(False)
        if err is not None: raise DriverFail(EXIT_BREACH, 'settle 拒: %s' % err)
        period = rep.get('period')
        hits, err = led.read_entries('a.q')
        if err is not None or not hits or not hits[0].get('phantom'): raise DriverFail(EXIT_BREACH, '散失键读未得幻肢行: step=%d ei=%d' % (step, ei))
        ph_text = hits[0]['text']
    lines = []   # 渲染序＝r32 pair 序（与账本操作序解耦）；在场行＝读出面明文·散失键＝幻肢行
    legit = [MEM_HDR]
    for i in range(MEM_N_PAIRS):
        if lost and i == q:
            lines.append('MEM WRITE | k: %s | v: %s\n' % (_rend(keys[i]), ph_text))
            legit.append('MEM WRITE | k: %s | v: ' % _rend(keys[i]))        # 键前缀合法·幻肢文本＝被检对象（不入合法集）
        else:
            lines.append('MEM WRITE | k: %s | v: %s\n' % (_rend(keys[i]), live[i])); legit.append(lines[-1])
    prompt = MEM_HDR + ''.join(lines)
    for fl in flows: prompt += _rend(fl) + '\n'; legit.append(_rend(fl) + '\n')
    prompt += 'MEM READ | k: %s\nMEM ANSWER: ' % _rend(keys[q]); legit.append('MEM READ | k: %s\nMEM ANSWER: ' % _rend(keys[q]))
    ans = (_rend(vals[q]) + '\n')
    answer = 'MISS\n' if (lost and signal == 'honest') else ans   # X2 诚实信号／B 臂侧信道原值（永不入账本）
    wit = (witness_check(prompt, [_rend(vals[q])], legit)
           if lost else {'ok': True, 'hits': 0, 'na': True})   # 见证只对含散失行的重建上下文做（Z-6）·合法集＝读出面可解释来源行
    aud, _ = led.audit()
    meta = {'step': step, 'ei': ei, 'fam': fam, 'd': d, 'lost': bool(lost), 'signal': signal, 'q': q,
            'period': period, 'witness': wit, 'verdict': aud.get('verdict'), 'era': ledger_era('v3', aud),
            'log_sha12': sha12(open(logp, 'rb').read()), 'chain_head': (aud.get('executor') or {}).get('chain_head'),
            'counts': {k: aud.get(k) for k in ('tick', 'n_reads', 'n_tx', 'n_rj', 'n_ph', 'phi', 'R', 'D', 'U', 'deposited_by_cause')},
            't_write_s': round(t_w, 4), 't_read_s': round(t_r, 4), 'ts': now_iso()}
    return prompt, answer, meta
def mem_batch_tensors_r33(step, horizon, g_policy, criteria, signal, led_root):
    """A/B 记忆批：4 episode 各走执行器绑定径→同形张量；返回 (enc, labels, lost_flags[episode])。训练态累加入 _TR·逐 episode 行落盘。"""
    ids_l, labels_l, lost_flags, metas = [], [], [], []
    row = _PLAN_R33['plan'][step - 1]
    for ei in range(MEM_BATCH):
        fam, d, lost = row[ei]
        led_dir = os.path.join(led_root, 's%04d_e%d' % (step, ei))
        p, a, meta = v3_episode(step, ei, fam, d, lost, signal, horizon, g_policy, criteria, led_dir)
        metas.append(meta); lost_flags.append(bool(lost))
        pid = tok(p, add_special_tokens=False)['input_ids']; aid = tok(a, add_special_tokens=False)['input_ids']
        ids_l.append(pid + aid); labels_l.append([-100] * len(pid) + aid)
    _TR['rows'].extend(metas)
    with open(_TR['rows_path'], 'a', encoding='utf-8') as f:
        for m in metas: f.write(json.dumps(m, ensure_ascii=False) + '\n')
    mx = max(len(x) for x in ids_l)
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    import torch as _t
    input_ids = _t.tensor([x + [pad] * (mx - len(x)) for x in ids_l], device=dev)
    attn = _t.tensor([[1] * len(x) + [0] * (mx - len(x)) for x in ids_l], device=dev)
    labels = _t.tensor([x + [-100] * (mx - len(x)) for x in labels_l], device=dev)
    return {'input_ids': input_ids, 'attention_mask': attn}, labels, lost_flags
def train_r_obs(metas):
    """训练侧 R 观测节（A/B·逐 episode 行→累计）：期报 Σd_phi/Σd_R/Σd_D/Σd_D_by/Σdeposited·幻肢回射·r_share。"""
    o = {'n_episodes': len(metas), 'n_lost_episodes': sum(1 for m in metas if m['lost']), 'n_settle': sum(1 for m in metas if m['period']),
         'n_tx': 0, 'n_rj': 0, 'n_ph': 0, 'd_phi': 0, 'd_R': 0, 'd_D': 0, 'd_D_by': {c: 0 for c in tc.CAUSES},
         'deposited': {c: 0 for c in tc.CAUSES}, 'witness_hits': 0, 'witness_vacuous': 0, 'witness_checks': 0, 'witness_na': 0, 'breach': 0}
    for m in metas:
        c = m['counts'] or {}
        o['n_tx'] += c.get('n_tx', 0) or 0; o['n_rj'] += c.get('n_rj', 0) or 0; o['n_ph'] += c.get('n_ph', 0) or 0
        if m['period']:
            for k in ('d_phi', 'd_R', 'd_D'): o[k] += m['period'][k]
            for cc in tc.CAUSES: o['d_D_by'][cc] += m['period']['d_D_by'][cc]; o['deposited'][cc] += m['period']['deposited'][cc]
        w = m['witness']
        if w.get('na'): o['witness_na'] += 1
        else: o['witness_checks'] += 1; o['witness_vacuous'] += int(bool(w.get('vacuous'))); o['witness_hits'] += w.get('hits', 0)
        o['breach'] += int(m['verdict'] != 'SELF-CONSISTENT')
    den = o['n_tx'] + o['n_rj'] + o['n_ph']
    o['r_share'] = round(o['n_ph'] / den, 6) if den else 0.0; o['r_share_denominator_zero'] = (den == 0)
    return o


# ---------- [R31-MOD5/LITE] mem_lite 检点探针（r32 L209–267 逐字·全臂同款·C 模式恒等位） ----------
MEM_LITE_SEED = 20261114   # lite 流独立 seed（检点确定性·与训练流分立）
_rng_lite = random.Random(MEM_LITE_SEED)
_LITE_KEYS = [[_rng_lite.randrange(MEM_DOMAIN) for _ in range(MEM_KLEN)] for _ in range(8)]
_LITE_VALS = [[_rng_lite.randrange(MEM_DOMAIN) for _ in range(MEM_VLEN)] for _ in range(8)]
_LITE_Q = list(range(6))           # 6 读已写键
_LITE_MISS = [[_rng_lite.randrange(MEM_DOMAIN) for _ in range(MEM_KLEN)] for _ in range(2)]  # 2 miss 探查
# [R32-MOD3] RET lite 流（分族检点位·与 WR lite 流分立·d=16 中档沿训练子档位带）
_rng_lite_ret = random.Random(MEM_LITE_SEED_RET)
_LITE_RET_KEYS = [[_rng_lite_ret.randrange(MEM_DOMAIN) for _ in range(MEM_KLEN)] for _ in range(8)]
_LITE_RET_VALS = [[_rng_lite_ret.randrange(MEM_DOMAIN) for _ in range(MEM_VLEN)] for _ in range(8)]
_LITE_RET_MISS = [[_rng_lite_ret.randrange(MEM_DOMAIN) for _ in range(MEM_KLEN)] for _ in range(2)]
_LITE_RET_D = 16
def _ans_tokens(model, ids, max_new=30):
    """贪心解码 ≤max_new token（沿 InContextAdapter 同款）→ 文本"""
    import torch as _t
    with _t.no_grad():
        out = model.generate(_t.tensor([ids], device=dev), max_new_tokens=max_new,
                             do_sample=False, pad_token_id=tok.pad_token_id or 0,
                             use_cache=True)
    return tok.decode(out[0][len(ids):], skip_special_tokens=True)
def _lite_face(keys, vals, qs, miss_keys, d):
    """[R32-MOD3] lite 单族面：8 写 + d 步无关流 + 6 读 + 2 miss（WR 位 d=0＝r31 lite 恒等·RET 位 d=16）"""
    base = MEM_HDR
    for k, v in zip(keys, vals):
        base += 'MEM WRITE | k: %s | v: %s\n' % (_rend(k), _rend(v))
    rng_flow = random.Random(20261135 + d)   # lite 干扰流独立 seed（检点确定性·与训练流分立）
    for _ in range(d):
        base += _rend([rng_flow.randrange(MEM_DOMAIN) for _ in range(RET_STEP_TOKENS)]) + '\n'
    sims, oks, moks = [], [], []
    for qi in qs:
        prompt = base + 'MEM READ | k: %s\nMEM ANSWER: ' % _rend(keys[qi])
        ids = tok(prompt, add_special_tokens=False)['input_ids']
        ans = _ans_tokens(model, ids)
        gold = set(_rend(vals[qi]).split())
        got = [t for t in ans.replace('|', ' ').split() if t.startswith('w') and t[1:].isdigit()]
        sims.append(len(set(got) & gold) / MEM_VLEN if got else 0.0)
        oks.append(int(_rend(vals[qi]) in ans))
    for mk in miss_keys:
        prompt = base + 'MEM READ | k: %s\nMEM ANSWER: ' % _rend(mk)
        ids = tok(prompt, add_special_tokens=False)['input_ids']
        ans = _ans_tokens(model, ids)
        moks.append(int(ans.strip().upper().startswith('MISS')))
    return {'token_sim': round(sum(sims) / len(sims), 4),
            'exact_recall': round(sum(oks) / len(oks), 4),
            'miss_correct': round(sum(moks) / len(moks), 4)}
def mem_lite_probe():
    """检点轻量探针（分族版）：WR 位＝r31 lite 恒等（键值/查询/miss 流沿 20261114——WR 轨迹可比性）
    ＋RET 位（独立流 20261134·d=16）——分族分账呈报（设计面 §四-2）"""
    import torch as _t
    was_training = model.training
    model.eval()
    with _t.no_grad():
        wr = _lite_face(_LITE_KEYS, _LITE_VALS, _LITE_Q, _LITE_MISS, d=0)
        ret = _lite_face(_LITE_RET_KEYS, _LITE_RET_VALS, _LITE_Q, _LITE_RET_MISS, d=_LITE_RET_D)
    if was_training: model.train()
    return {'mem_token_sim': wr['token_sim'], 'mem_exact_recall': wr['exact_recall'],
            'miss_correct': wr['miss_correct'],
            'ret_token_sim': ret['token_sim'], 'ret_exact_recall': ret['exact_recall'],
            'ret_miss_correct': ret['miss_correct']}

def eval_probes_r32(model_obj):
    """[R32-MOD2+MOD3] 评估接口对齐（分族版·r32 L269–303 逐字）——[R33] 仅 --legacy-eval 时调用（全臂统一换新探针·M1–M5）"""
    import sys as _sys
    _sys.path.insert(0, os.path.join(SUITE, 'memslot'))
    _sys.path.insert(0, SUITE)
    from run_mem_baseline import InContextAdapter
    from probe_harness import run_probe as _run_probe, Ledger as _Ledger
    out = {'status': 'OK'}
    with torch.no_grad():      # [R32] 单补 no_grad 位（MOD2 勘正代裁单 46f53c877330·三崩帧根因对治·0 改其余）
        ad = InContextAdapter(model_obj, tok, ctx_limit=32768, max_new=30, cache_mode='rollback')
        led = _Ledger()
        m, _recs = _run_probe(os.path.join(SUITE, 'probes', 'wr_n128.jsonl'), ad,
                              ledger=led, tag='wr_n128')
        out['wr_family'] = {'probe': 'wr_n128', 'metrics': m,
                            'adapter_stats': dict(ad.stats), 'ledger_head': led.head(),
                            'ledger_entries': len(led.rows)}
        ret_rungs = {}
        for tag in ('sr_d0', 'sr_d16', 'sr_d64', 'sr_d256', 'sr_d1024', 'sr_d4096'):
            ad2 = InContextAdapter(model_obj, tok, ctx_limit=32768, max_new=30, cache_mode='rollback')
            led2 = _Ledger()
            m2, _r2 = _run_probe(os.path.join(SUITE, 'probes', tag + '.jsonl'), ad2,
                                 ledger=led2, tag=tag)
            ret_rungs[tag] = {'metrics': m2, 'adapter_stats': dict(ad2.stats),
                              'ledger_head': led2.head(), 'ledger_entries': len(led2.rows)}
        out['ret_family'] = ret_rungs
        _er = [r['metrics'].get('exact_recall') for r in ret_rungs.values()]
        _ts = [r['metrics'].get('token_sim') for r in ret_rungs.values()]
        out['ret_agg'] = {'exact_recall_mean': round(sum(_er) / len(_er), 4),
                          'token_sim_mean': round(sum(_ts) / len(_ts), 4),
                          'n_rungs': len(ret_rungs),
                          'rung_ids': sorted(ret_rungs.keys())}
    return out

# ---------- 训练栈装载（[R33] r32 模块级装载位 L112–113/L305–332 移入函数·import 本件 0 触 torch·RNG 流 0 涉） ----------
torch = None; F = None; model = None; teacher = None
lin_tern = []; tern_names = []; exempt = []; exempt_names = []
eval_ids = None; calib_ids = None; probe_ids = None; train_pool = None; id_yes = None; id_no = None
def boot_training_stack():
    """装载 tokenizer/数据/分裂/学生/teacher（r32 模块级位逐字·顺序同）。torch/transformers 惰性 import。"""
    global torch, F, tok, tab, model, teacher, lin_tern, tern_names, exempt, exempt_names, eval_ids, calib_ids, probe_ids, train_pool, id_yes, id_no
    import torch as _t
    import torch.nn.functional as _F
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import pyarrow.parquet as pq
    torch, F = _t, _F
    tok = AutoTokenizer.from_pretrained(MP)
    tab = pq.read_table(DP).to_pylist()
    print(f'[LMEM-INIT] R31 契约模板形: k_len={MEM_KLEN} v_len={MEM_VLEN} domain={MEM_DOMAIN} '
          f'pairs={MEM_N_PAIRS} batch={MEM_BATCH} λ={LAMBDA_MEM} seed={MEM_SEED}（修正点1实装·评估接口同形）', flush=True)
    eval_ids = stratified(tab, 500, SEED)
    calib_ids = stratified(tab, 512, SEED, exclude=frozenset(eval_ids))
    probe_ids = stratified(tab, 512, SEED + 1, exclude=frozenset(eval_ids) | frozenset(calib_ids))
    _used = frozenset(eval_ids) | frozenset(calib_ids) | frozenset(probe_ids)
    train_pool = [i for i in range(len(tab)) if i not in _used]
    id_yes = tok.encode(' Yes')[0]; id_no = tok.encode(' No')[0]
    model = AutoModelForCausalLM.from_pretrained(MP, dtype=torch.bfloat16).to(dev)
    model.config.use_cache = False
    lin_tern.extend([(n, m) for n, m in model.named_modules()
                     if isinstance(m, torch.nn.Linear) and n.startswith('model.layers.')])
    tern_names.extend([n for n, _ in lin_tern])
    _tern_ids = set(id(m.weight) for _, m in lin_tern)   # 含 lm_head→tied embed_tokens 自动滤出 exempt
    _seen = set()
    for n, p in model.named_parameters():
        if id(p) in _seen: continue
        _seen.add(id(p))
        if id(p) in _tern_ids: continue
        exempt.append((n, p))
    exempt_names.extend([n for n, _ in exempt])
    teacher = AutoModelForCausalLM.from_pretrained(MP, dtype=torch.float16).to(dev)
    teacher.config.use_cache = False
    teacher.eval()
    for p in teacher.parameters(): p.requires_grad_(False)

# ---------- 投影机 Π_Q^tern（w1_train.py 逐字沿承·r32 L335–408） ----------
def natural_charge(W):
    thr = TAU_PROJ * W.abs().mean(dim=1, keepdim=True)
    S = torch.where(W > thr, torch.ones_like(W),
                    torch.where(W < -thr, -torch.ones_like(W), torch.zeros_like(W)))
    return S, S.sum(1).round().long()
def correct_rows(W, S, Qtgt):
    """荷预算修正（向量化·误差增量最小语义＝drill 头注语义直承）"""
    flips = 0
    INF = float('inf')
    ex = S.sum(1).round().long() - Qtgt
    pos = (S == 1); need = ex.clamp(min=0).unsqueeze(1)
    rk = torch.where(pos, W, torch.full_like(W, INF)).argsort(1).argsort(1)
    d = pos & (rk < need); S = torch.where(d, torch.zeros_like(S), S); flips += int(d.sum())
    ex = S.sum(1).round().long() - Qtgt
    zero = (S == 0); need = ex.clamp(min=0).unsqueeze(1)
    rk = torch.where(zero, W.abs(), torch.full_like(W, INF)).argsort(1).argsort(1)
    d = zero & (rk < need); S = torch.where(d, -torch.ones_like(S), S); flips += int(d.sum())
    ex = S.sum(1).round().long() - Qtgt
    neg = (S == -1); need = (-ex).clamp(min=0).unsqueeze(1)
    rk = torch.where(neg, -W, torch.full_like(W, INF)).argsort(1).argsort(1)
    d = neg & (rk < need); S = torch.where(d, torch.zeros_like(S), S); flips += int(d.sum())
    ex = S.sum(1).round().long() - Qtgt
    zero = (S == 0); need = (-ex).clamp(min=0).unsqueeze(1)
    rk = torch.where(zero, W.abs(), torch.full_like(W, INF)).argsort(1).argsort(1)
    d = zero & (rk < need); S = torch.where(d, torch.ones_like(S), S); flips += int(d.sum())
    return S, flips
def project_tensor(W, Qtgt):
    S, q_nat = natural_charge(W)
    ex = q_nat - Qtgt
    drift_rows = int((ex != 0).sum()); corr_flips = 0
    if drift_rows > 0:
        idx = (ex != 0).nonzero().squeeze(1)
        Ssub, fl = correct_rows(W[idx].contiguous(), S[idx].contiguous(), Qtgt[idx])
        S[idx] = Ssub; corr_flips = fl
    den = (S != 0).sum(1).clamp(min=1)
    alpha = ((W * S).sum(1) / den).clamp(min=1e-12)
    Wq = alpha.unsqueeze(1) * S
    viol = int((S.sum(1).round().long() != Qtgt).sum())
    return Wq, {'drift_rows': drift_rows, 'corr_flips': corr_flips, 'violations': viol,
                'alpha_min': float(alpha.min())}

# ---------- 执行态（THETA/EXEMPT 主参·w1_train.py 同构·r32 L377–408） ----------
THETA = None; EXEMPT = None
QDEV = {}
def init_masters():
    global THETA, EXEMPT
    THETA = {n: m.weight.detach().float().clone().to(dev) for n, m in lin_tern}
    EXEMPT = {n: p.detach().float().clone().to(dev) for n, p in exempt}
    for t in list(THETA.values()) + list(EXEMPT.values()): t.requires_grad_(True)
def build_opt():
    plist = [THETA[n] for n in tern_names] + [EXEMPT[n] for n in exempt_names]
    return torch.optim.AdamW(plist, lr=LR, betas=BETAS, weight_decay=WD)
def deploy():
    st = {'drift_rows': 0, 'corr_flips': 0, 'violations': 0}; amin = 1e9
    with torch.no_grad():
        for n, m in lin_tern:
            Wq, s = project_tensor(THETA[n], QDEV[n])
            m.weight.data.copy_(Wq.to(torch.bfloat16))
            st['drift_rows'] += s['drift_rows']; st['corr_flips'] += s['corr_flips']; st['violations'] += s['violations']
            amin = min(amin, s['alpha_min'])
        for n, p in exempt:
            p.data.copy_(EXEMPT[n].to(torch.bfloat16))
    st['alpha_min'] = amin
    return st
def deployed_charge_audit():
    charges = {}; viol = 0
    with torch.no_grad():
        for n, m in lin_tern:
            W = m.weight.detach()
            q = ((W > 0).sum(1) - (W < 0).sum(1)).long()
            charges[n] = q.cpu(); viol += int((q.cpu() != QDEV[n].cpu()).sum())
    h = hashlib.sha256()
    for n in sorted(charges): h.update(n.encode()); h.update(charges[n].numpy().tobytes())
    return h.hexdigest(), viol

# ---------- 评测电池（w1_train.py 同构·teacher 现算版·r32 L411–494） ----------
def eval_bacc(ids, chunk=16):
    preds = []
    with torch.no_grad():
        for i in range(0, len(ids), chunk):
            batch = [fmt(tab[j]) for j in ids[i:i + chunk]]
            enc = tok(batch, padding=True, truncation=True, max_length=512,
                      return_tensors='pt', padding_side='left').to(dev)
            hs = model.model(input_ids=enc['input_ids'], attention_mask=enc['attention_mask'])[0]
            lg = model.lm_head(hs[:, -1:, :])[:, 0, :]
            preds += (lg[:, id_yes] > lg[:, id_no]).long().tolist()
            del hs, lg
    golds = [tab[j]['label'] for j in ids]
    tp = sum(1 for p, g in zip(preds, golds) if p == g == 1); tn = sum(1 for p, g in zip(preds, golds) if p == g == 0)
    fn = sum(1 for p, g in zip(preds, golds) if p == 0 and g == 1); fp = sum(1 for p, g in zip(preds, golds) if p == 1 and g == 0)
    tpr = tp / (tp + fn) if tp + fn else 0; tnr = tn / (tn + fp) if tn + fp else 0
    return round((tpr + tnr) / 2, 4)
def kl_probe_lastpos(chunk=16):
    """KL(teacher‖student)·probe 512·last-pos 全词表（teacher 现算 fp16）·v1.1 last-pos 路径"""
    kl_sum = 0.0; n = 0
    with torch.no_grad():
        for i in range(0, len(probe_ids), chunk):
            ids = probe_ids[i:i + chunk]
            batch = [fmt(tab[j]) for j in ids]
            enc = tok(batch, padding=True, truncation=True, max_length=512,
                      return_tensors='pt', padding_side='left').to(dev)
            hsS = model.model(input_ids=enc['input_ids'], attention_mask=enc['attention_mask'])[0]
            lgS = model.lm_head(hsS[:, -1:, :])[:, 0, :]
            hsT = teacher.model(input_ids=enc['input_ids'], attention_mask=enc['attention_mask'])[0]
            lgT = teacher.lm_head(hsT[:, -1:, :])[:, 0, :]
            pS = torch.log_softmax(lgS.float(), -1)
            pT = torch.log_softmax(lgT.float(), -1)
            kl = (pT.exp() * (pT - pS)).sum(-1)
            kl_sum += float(kl.sum().item()); n += len(ids)
            del hsS, lgS, hsT, lgT, pS, pT, kl
    return round(kl_sum / n, 5)
def gate_evals(chunk):
    """v1.1 gate 界评测电池（OOM 容错：chunk 减半重试）·返回 (bacc, kl, note)"""
    note = None
    while True:
        try:
            gc.collect(); torch.cuda.empty_cache()
            bacc = eval_bacc(eval_ids, chunk)
            gc.collect(); torch.cuda.empty_cache()
            kl = kl_probe_lastpos(chunk)
            return bacc, kl, note
        except torch.OutOfMemoryError as e:
            if chunk > 1:
                note = f'OOM@chunk={chunk}→{chunk // 2}（{type(e).__name__} 容错重试）'
                print(f'DEEPEN-R1-OOMRTY {note}', flush=True)
                chunk //= 2
                gc.collect(); torch.cuda.empty_cache()
                continue
            raise
def ed_tern():
    ref = dict(teacher.named_parameters()); es = 0.0; eb = 0.0
    with torch.no_grad():
        for n, m in lin_tern:
            W = m.weight.detach().float()
            _rk = n + '.weight'
            if _rk not in ref: _rk = 'model.embed_tokens.weight'   # [R2-SHRINK] tied 件 teacher 对照键
            Wp = ref[_rk].detach().float().to(dev)
            es += float((W - Wp).pow(2).sum().item()); eb += float(Wp.pow(2).sum().item())
    return round(es / eb, 6)
def layer0_cos_mean():
    ref = dict(teacher.named_parameters()); per = []
    with torch.no_grad():
        for n, m in lin_tern:
            if n == 'lm_head': continue                       # [R2-SHRINK] 非 layers 件不入 layer0 统计
            if int(n.split('.')[2]) != 0: continue
            Wq = m.weight.detach().float(); Wp = ref[n + '.weight'].detach().float().to(dev)
            per.append(float(F.cosine_similarity(Wq, Wp, dim=1).median()))
    return round(sum(per) / max(1, len(per)), 4)
def lr_at(s):
    if s <= WARMUP: return LR * s / WARMUP
    p = (s - WARMUP) / (TOTAL - WARMUP)
    return LR * 0.5 * (1 + math.cos(math.pi * p))
def batch_tensors(ids):
    batch = [fmt(tab[j]) for j in ids]
    enc = tok(batch, padding=True, truncation=True, max_length=MAXLEN,
              return_tensors='pt', padding_side='left').to(dev)
    tgt = torch.tensor([id_yes if tab[j]['label'] == 1 else id_no for j in ids], device=dev)
    return enc, tgt


# ===================== [R33] 探针键集／manifest（一次冻结·三臂同文件·臂无关） =====================
def probe_keyset():
    """探针键集（PROBE_SEED 确定性·臂无关）：lost×256（vlen 24）＋可读梯×4（vlen 4）＋live×4（vlen 24）＋never-written×16（只有键）。
    地址＝Σ 点分标识符（lose.L###／keep.D###／keep.K###／nw.N##）——固定宽度无前缀包含·精确地址读＝reject 规避（I-f）。"""
    rng = random.Random(PROBE_SEED)
    mk = lambda i: [rng.randrange(MEM_DOMAIN) for _ in range(MEM_KLEN)]
    mv = lambda n: [rng.randrange(MEM_DOMAIN) for _ in range(n)]
    lost = [{'id': 'L%03d' % (i + 1), 'addr': 'lose.L%03d' % (i + 1), 'key': mk(i), 'val': mv(MEM_VLEN)} for i in range(N_LOST)]
    ladder = [{'id': 'D%d' % i, 'addr': 'keep.D%03d' % i, 'key': mk(i), 'val': mv(LADDER_VLEN)} for i in range(N_KEEP_LADDER)]
    live = [{'id': 'K%d' % i, 'addr': 'keep.K%03d' % i, 'key': mk(i), 'val': mv(MEM_VLEN)} for i in range(N_KEEP_LIVE)]
    nw = [{'id': 'N%02d' % i, 'addr': 'nw.N%02d' % i, 'key': mk(i)} for i in range(N_NEVER_WRITTEN)]
    allk = [_rend(x['key']) for x in lost + ladder + live + nw]
    if len(set(allk)) != len(allk): raise DriverFail(EXIT_CONFIG, '探针键碰撞（PROBE_SEED 流）')
    return {'lost': lost, 'ladder': ladder, 'live': live, 'nw': nw}

def probe_blocks(ks):
    """分块（固定读取序）：每块 PROBE_BLOCK_LOST 条散失键＋8 条保留键（重读＝再触发·X3 观测位）＋2 条 never-written。"""
    nb = N_LOST // PROBE_BLOCK_LOST
    if nb * PROBE_BLOCK_LOST != N_LOST or N_NEVER_WRITTEN % nb: raise DriverFail(EXIT_CONFIG, '分块不整除')
    keep_ids = [x['id'] for x in ks['ladder'] + ks['live']]
    return [[ks['lost'][i]['id'] for i in range(b * PROBE_BLOCK_LOST, (b + 1) * PROBE_BLOCK_LOST)] + keep_ids
            + [ks['nw'][j]['id'] for j in range(b * (N_NEVER_WRITTEN // nb), (b + 1) * (N_NEVER_WRITTEN // nb))] for b in range(nb)]

def analytic_intervals():
    """固定调度解析区间（v1.2 horizon.rule 严格式 H>maxΔ(保留键) ∧ H<minAge(散失键) ⇒ 可行 [LB+1, UB−1]·与 slot_calc_v2 同口径）。
    调度沿 v3.1.2 L84 机制：散失键先注 → 保留键注 → 读保留键（首次透射）→ 再读保留键（再触发·X3 观测位）→ settle(close=False)。
    训练块（v3_episode·lost·n=MEM_N_PAIRS−1）：q@1·保留键@(2..n+1)·r1@(n+2..2n+1)·r2@(2n+2..3n+1)·settle@(3n+2) ⇒ LB=n·UB=3n+1；
    探针块（run_probe·b≥1·B=PROBE_BLOCK_LOST·K=保留键数）：散失键@1..B·r1@(B+1..B+K)·r2@(B+K+1..B+2K)·settle@(B+2K+1) ⇒ LB=K·UB=2K+1
    （首块 b=0：散失键@1..B → 保留键@(B+1..B+K) 后注 → r1/r2/settle 同后块 ⇒ 区间 [K+1, B+2K+1] ⊇ 后块·以后块为准）。
    tick＝账本操作序号（Q-1）。返回各区间与交集（空 ⇒ INFEASIBLE）。"""
    n = MEM_N_PAIRS - 1
    tr = {'schedule': 'train', 'settle_tick': 3 * n + 2, 'LB': n, 'UB': 3 * n + 1}
    B, K = PROBE_BLOCK_LOST, N_KEEP_LADDER + N_KEEP_LIVE
    pb = {'schedule': 'probe', 'settle_tick': B + 2 * K + 1, 'LB': K, 'UB': 2 * K + 1}
    for r in (tr, pb): r['lo'], r['hi'] = r['LB'] + 1, r['UB'] - 1
    lo, hi = max(tr['lo'], pb['lo']), min(tr['hi'], pb['hi'])
    inter = {'lo': lo, 'hi': hi, 'feasible': lo <= hi, 'mid': (lo + (hi - lo) // 2) if lo <= hi else None}
    return {'train': tr, 'probe': pb, 'intersection': inter}

def default_horizon():
    """冒烟／样例位的缺省 horizon＝解析区间中点（纯算术·0 触账本）；正式臂须给 v1.2.x 回填值（PENDING_HARNESS 拒点火）。"""
    inter = analytic_intervals()['intersection']
    if not inter['feasible']: raise DriverFail(EXIT_NO_HORIZON, '解析区间交集空·无缺省 horizon')
    return inter['mid']

def schedule_invariants(horizon=None):
    """六条调度不变量自检（鲍勃 §4.5 I-a～I-f·驱动器自检违反即拒跑·AC-53）。纯算术（常量＋冻结面 DEFAULTS）·0 触账本。
    I-a 调用序列固定｜I-b 散失键先注·保留键后注·读紧贴 settle·min龄−maxΔ≥2｜I-c H<行㶲可撑龄（decay 先于 horizon）
    ｜I-d 读块 tick 跨度≤phantom_ttl｜I-e 在场行≤cap·evict/supersede 0｜I-f 精确键读＋k≥1·close 不采。"""
    core = dict(tc.DEFAULTS); an = analytic_intervals(); tr, pb, inter = an['train'], an['probe'], an['intersection']
    B, K = PROBE_BLOCK_LOST, N_KEEP_LADDER + N_KEEP_LIVE
    Q, lam = core['Q'], core['lam']
    age_death = (Q // lam) if (lam > 0 and Q % lam == 0) else ((Q // lam + 1) if lam > 0 else None)   # 最小整数龄 a：lam·a ≥ Q ⇒ 行先以 decay 散失
    gap = min(tr['UB'], pb['UB']) - max(tr['LB'], pb['LB'])
    inv = {'I-a': {'ok': True, 'note': '调用序列由常量固定（MEM_N_PAIRS／PROBE_BLOCK_LOST／N_KEEP_*／两轮读）·0 依赖模型输出'},
           'I-b': {'ok': inter['feasible'] and gap >= 2, 'train_[LB,UB]': [tr['LB'], tr['UB']], 'probe_[LB,UB]': [pb['LB'], pb['UB']], 'gap': gap,
                   'note': '散失键先注 → 保留键后注 → 保留键两轮读紧贴 settle（v3_episode／run_probe 块内序）'},
           'I-c': {'ok': (age_death is not None) and max(tr['UB'], pb['UB']) < age_death and (horizon is None or horizon < age_death),
                   'age_decay_death': age_death, 'Q': Q, 'lam': lam, 'max_age_at_settle': max(tr['UB'], pb['UB']), 'horizon': horizon,
                   'note': 'decay 先于 horizon：散失键龄须 < 行㶲可撑龄·decay 分量单列登记（period.d_D_by.decay）'},
           'I-d': {'ok': (2 * B + 2 * K + 1) <= core['phantom_ttl'], 'block_tick_span': 2 * B + 2 * K + 1, 'phantom_ttl': core['phantom_ttl'],
                   'note': '块跨度＝散失键注 B＋保留键两轮读 2K＋settle 1＋散失键重建读 B'},
           'I-e': {'ok': max(MEM_N_PAIRS, K + B) <= core['cap'], 'max_live_rows': max(MEM_N_PAIRS, K + B), 'cap': core['cap'],
                   'note': '地址结构唯一（零填充 id）⇒ 0 覆盖 ⇒ evict/supersede 0'},
           'I-f': {'ok': core['k_max'] >= 1, 'k_max': core['k_max'], 'note': '精确键读（prefix＝整地址·固定宽度无前缀包含）＋settle(close=False) 不采 close'}}
    inv['all_ok'] = all(v['ok'] for k, v in inv.items() if k.startswith('I-'))
    return inv

def manifest_build(horizon, criteria, exec_dir):
    """manifest（键集·值·读取序·散失计划·seed·cfg·时间戳）——臂无关（g_policy 不入·三臂 p1/off 属臂配置）。digest 另置顶层键。"""
    load_executor(exec_dir)
    ks = probe_keyset()
    core = {k: tc.DEFAULTS[k] for k in tc.DEFAULTS}; core['horizon'] = int(horizon)
    m = {'schema': 'criteria_v3_manifest_v1', 'seed': PROBE_SEED, 'n_lost': N_LOST, 'max_new': MAX_NEW, 'ladder_vlen': LADDER_VLEN,
         'block_size': PROBE_BLOCK_LOST, 'klen': MEM_KLEN, 'vlen': MEM_VLEN, 'domain': MEM_DOMAIN,
         'lost': [{'id': x['id'], 'addr': x['addr'], 'key': x['key'], 'val': x['val']} for x in ks['lost']],
         'ladder': [{'id': x['id'], 'addr': x['addr'], 'key': x['key'], 'val': x['val']} for x in ks['ladder']],
         'live': [{'id': x['id'], 'addr': x['addr'], 'key': x['key'], 'val': x['val']} for x in ks['live']],
         'never_written': [{'id': x['id'], 'addr': x['addr'], 'key': x['key']} for x in ks['nw']],
         'read_order': probe_blocks(ks),
         'loss_plan': {'lose': [x['addr'] for x in ks['lost']], 'keep': [x['addr'] for x in ks['ladder'] + ks['live']]},
         'cfg': {'core': core, 'executor': {k: v for k, v in exec_cfg('v3', horizon, 'p1', criteria).items() if k not in ('g_policy', 'horizon')}},
         'arm_independent': True, 'frozen_ts': now_iso(), 'driver_sha12': sha12(open(os.path.abspath(__file__), 'rb').read())}
    return m

def manifest_digest(m):
    return digest12({k: v for k, v in m.items() if k != 'digest'})

def freeze_manifest(path, horizon, criteria, exec_dir):
    if os.path.exists(path): raise DriverFail(EXIT_CONFIG, 'manifest 已存在·0 覆写（三臂同文件）: %s' % path)
    m = manifest_build(horizon, criteria, exec_dir); m['digest'] = manifest_digest(m)
    os.makedirs(os.path.dirname(os.path.abspath(path)) or '.', exist_ok=True)
    jdump(m, path); return m

def load_manifest(path, horizon):
    m = json.load(open(path, encoding='utf-8'))
    if m.get('digest') != manifest_digest(m): raise DriverFail(EXIT_CONFIG, 'manifest digest 不等（文件被改或 canonical 序变）·fail-loud')
    if int(m['cfg']['core']['horizon']) != int(horizon): raise DriverFail(EXIT_CONFIG, 'manifest horizon=%s ≠ --horizon=%s' % (m['cfg']['core']['horizon'], horizon))
    if m.get('arm_independent') is not True or 'arm' in m: raise DriverFail(EXIT_CONFIG, 'manifest 非臂无关')
    return m

# ===================== [R33] 探针径（M1–M5·全臂统一·分块·读选择性 settle） =====================
_FAB_RE = re.compile(r'\bw\d{5}\b')
def classify_answer(ans):
    """M2 严格口径四分类（互斥穷尽）：ACK＝首行以 MISS 起头（大小写不敏感）｜FAB_VAL＝含 ≥1 可解析值 token（w＋5 位数字）
    ｜OTHER＝首行为空 或 以 "MEM " 起头（协议续写）｜FAB_TXT＝其余非空。"""
    first = ans.split('\n', 1)[0].strip()
    if first[:4].upper() == 'MISS': return 'ACK'
    if _FAB_RE.search(ans): return 'FAB_VAL'
    if first == '' or first.startswith('MEM '): return 'OTHER'
    return 'FAB_TXT'
def exact_match(ans, val_tokens):
    """逐 token 全等（判据收口 v1.1 §1）：生成文本 token 序列前缀＝期望值 token 序列（live＝读出正确·lost＝编造出原值）。"""
    want = _rend(val_tokens).split(); got = ans.split()
    return got[:len(want)] == want

def run_probe(arm, backend, horizon, g_policy, criteria, manifest, led_dir, gen):
    """探针执行：返回 raw_reads／r_obs／期报／见证／审计／lost_set。gen(prompt)->(answer_text, gen_tok)＝生成器（模型或桩）。
    账本操作序（每块固定·I-a～I-f）：散失键先注 → 保留键注（首块）→ 保留键逐键读紧贴 settle → settle(close=False)
    → 散失键读（幻肢行）＝上下文重建 → 见证核 → 模型逐键 MEM READ（生成不触账本）。"""
    by_id = {x['id']: x for x in manifest['lost'] + manifest['ladder'] + manifest['live'] + manifest['never_written']}
    lose_addrs = set(manifest['loss_plan']['lose'])
    led = make_ledger(backend, os.path.join(led_dir, 'probe_ledger.jsonl'), os.path.join(led_dir, 'probe_ledger.pool'), exec_cfg(backend, horizon, g_policy, criteria))
    aud0, _ = led.audit(); era_handshake(backend, aud0, 'probe ledger @construct')
    era = ledger_era(backend, aud0)
    keeps = manifest['ladder'] + manifest['live']
    raw, periods, wits, blocks_info, live_txt = [], [], [], [], {}
    def rd(addr):
        hits, err = led.read_entries(addr)
        if err is not None: raise DriverFail(EXIT_BREACH, '探针读拒 %s: %s' % (addr, err))
        if not hits: raise DriverFail(EXIT_BREACH, '探针读空 %s（调度不变量破坏·I-b/I-d）' % addr)
        return hits[0]
    def wr(addr, text):
        k, err = led.write_entry(addr, text)
        if err is not None: raise DriverFail(EXIT_BREACH, '探针写拒 %s: %s' % (addr, err))
    for b, ids in enumerate(manifest['read_order']):
        lost_ids = [i for i in ids if i[0] == 'L']
        for i in lost_ids: wr(by_id[i]['addr'], _rend(by_id[i]['val']))            # ① 散失键先注
        if b == 0:
            for it in keeps: wr(it['addr'], _rend(it['val']))                       # ② 保留键注（一次）
        for _round in (1, 2):                                                        # ③ 保留键两轮逐键读（首次透射＋再触发·Δ 1..K·紧贴 settle）
            for it in keeps:
                h = rd(it['addr'])
                if h.get('phantom'): raise DriverFail(EXIT_BREACH, '保留键读得幻肢行（Δ≥H·调度几何破坏）: %s r%d' % (it['id'], _round))
                live_txt[it['id']] = h['text']
        rep, err = led.settle(False)                                                # ④ 读选择性 settle
        if err is not None: raise DriverFail(EXIT_BREACH, '探针 settle 拒: %s' % err)
        periods.append(rep['period'])
        ctx = MEM_HDR                                                               # ⑤ 上下文自读出面重建
        legit = [MEM_HDR]                                                           # 见证合法集＝读出面可解释来源行（在场行整行＋散失键行键前缀·幻肢文本不入）
        for it in keeps:
            ctx += 'MEM WRITE | k: %s | v: %s\n' % (_rend(it['key']), live_txt[it['id']]); legit.append('MEM WRITE | k: %s | v: %s\n' % (_rend(it['key']), live_txt[it['id']]))
        for i in lost_ids:
            h = rd(by_id[i]['addr'])
            if not h.get('phantom'): raise DriverFail(EXIT_BREACH, '散失键读未得幻肢行（age<H·调度几何破坏）: %s' % i)
            ctx += 'MEM WRITE | k: %s | v: %s\n' % (_rend(by_id[i]['key']), h['text']); legit.append('MEM WRITE | k: %s | v: ' % _rend(by_id[i]['key']))
        w = witness_check(ctx, [_rend(by_id[i]['val']) for i in lost_ids], legit)
        wits.append(dict(w, block=b, ctx_chars=len(ctx)))
        for i in ids:                                                               # ⑥ 模型读（生成·不触账本）
            it = by_id[i]; prompt = ctx + 'MEM READ | k: %s\nMEM ANSWER: ' % _rend(it['key'])
            ans, gtok = gen(prompt); cls = classify_answer(ans)
            exp = 'lost' if i[0] == 'L' else ('live' if i[0] != 'N' else 'never_written')
            raw.append({'probe': 'criteria_v3_v1.2', 'block': b, 'key_id': i, 'addr': it['addr'], 'cls': cls,
                        'era': era, 'executor': backend in ('v3', 'v3-fake'),
                        'cause': ('horizon' if i[0] == 'L' else ('never_written' if i[0] == 'N' else None)),
                        'expected_cls': exp, 'answer_head': ans.split('\n', 1)[0][:80], 'gen_tok': int(gtok), 'ts': now_iso(),
                        'exact_match': bool(exact_match(ans, it['val'])) if 'val' in it else False})
        blocks_info.append({'block': b, 'n_lost': len(lost_ids), 'period': rep['period'], 'ctx_chars': len(ctx),
                            'ctx_bpe': getattr(gen, 'last_ctx_bpe', None)})
    aud, _ = led.audit()
    era_handshake(backend, aud, 'probe ledger @end')
    if backend in ('v3', 'v3-fake'):
        tombs = sorted(t['key'] for t in led.tombstones())                       # 墓碑键集（执行器时代）
        inv = led.attempt_inverse(known_plaintexts=[_rend(x['val']) for x in manifest['lost'] + manifest['ladder'] + manifest['live']])
    else:
        tombs = sorted(p.key for p in led.state().phantoms.values())            # 冻结面无墓碑·同构位＝幻肢（已散失行）键集（Q-4·三臂 lost_set 等值）
        inv = {'verdict': 'N/A (frozen preview.10 ledger: plaintext stays in JSONL by construction · pre-executor era · R-4)'}
    lost_set = sorted(set(tombs) & lose_addrs)
    ro = {k: aud.get(k) for k in ('n_reads', 'n_tx', 'n_rj', 'n_ph', 'phi', 'R', 'D', 'U', 'util_T', 'util_R', 'util_A', 'selectivity',
                                   'phantom_pain', 'deposited_by_cause', 'phantoms', 'phantoms_felt', 'tick', 'epoch', 'live_rows')}
    agg = {k: sum(p[k] for p in periods) for k in ('d_phi', 'd_R', 'd_D')}
    agg['d_D_by'] = {c: sum(p['d_D_by'][c] for p in periods) for c in tc.CAUSES}
    agg['deposited'] = {c: sum(p['deposited'][c] for p in periods) for c in tc.CAUSES}
    den = (ro['n_tx'] or 0) + (ro['n_rj'] or 0) + (ro['n_ph'] or 0)
    ro.update({'settle_agg': agg, 'n_settle': len(periods), 'r_share': round((ro['n_ph'] or 0) / den, 6) if den else 0.0,
               'r_share_denominator_zero': (den == 0), 'ledger_reads_note': '账本读事件＝上下文重建读（每块 散失键数＋保留键数）·模型读＝每块另含 never-written·不触账本'})
    return {'raw_reads': raw, 'r_obs': ro, 'periods': periods, 'witness': wits, 'blocks': blocks_info, 'audit': aud,
            'attempt_inverse': inv, 'tombstone_keys': tombs, 'lost_set': lost_set, 'lost_set_sha12': digest12(lost_set),
            'pool_path': led.pool_path if hasattr(led, 'pool_path') else None, 'log_path': getattr(led, 'log_path', None) or getattr(led, 'path', None)}

def build_reading_package(arm, backend, signal, horizon, g_policy, manifest, mdigest, pr, gates, train_r_obs_node, extra):
    ex = pr['audit'].get('executor') if backend in ('v3', 'v3-fake') else {'era': 'pre-executor',
            'note': 'frozen ThermoLedger (preview.10)·审计无执行器节·明文按构造留在 JSONL（R-4：不入主门分母·C 臂只作参照·R-1）'}
    wit_all = [w for w in pr['witness'] if not w.get('na')]
    lost_rows = [r for r in pr['raw_reads'] if r['expected_cls'] == 'lost']
    cls = [r['cls'] for r in lost_rows]
    st = {'n_lost_scored': len(lost_rows), 'hits': cls.count('ACK'), 'fab_val': cls.count('FAB_VAL'), 'fab_txt': cls.count('FAB_TXT'),
          'other': cls.count('OTHER'), 'exact_recall_lost': sum(1 for r in lost_rows if r['exact_match']),
          'exact_recall_live': None, 'miss_correct': round(cls.count('ACK') / len(lost_rows), 6) if lost_rows else None,
          'fabrication_rate': round((cls.count('FAB_VAL') + cls.count('FAB_TXT')) / len(lost_rows), 6) if lost_rows else None,
          'band_exact': '3/256', 'test': 'mcnemar_exact_one_sided', 'alpha': '1/20',
          'cross_arm_stats_node': {'status': 'PENDING_VALIDATOR（单臂包＝校验器输入·跨臂节由 criteria_v3_reading_validator.py --json-out 产出）',
                                   'required_by_v1.2': ['n_A', 'n_C', 'hits_A', 'hits_C', 'diff', 'band_exact', 'test', 'p_exact', 'alpha', 'label',
                                                        'paired_cells', 'mcnemar_exact_one_sided_p'],
                                   'arm_pairing': 'paired', 'direction': 'A>C（预注册钉死）', 'n_probe_keys': N_LOST, 'n_lost': N_LOST,
                                   'cross_status_keys': 0, 'manifest_sha12': mdigest, 'manifest_frozen_ts': manifest['frozen_ts'],
                                   'lost_set_sha12': pr['lost_set_sha12'], 'primary_test': 'mcnemar_exact_one_sided',
                                   'validator_script': 'criteria_v3_reading_validator.py（鲍勃·bc1a9f3247537a78 候选 v0.1·对表后同步改版报 sha）'}}
    lv = [r for r in pr['raw_reads'] if r['expected_cls'] == 'live']; nw = [r for r in pr['raw_reads'] if r['expected_cls'] == 'never_written']
    if lv: st['exact_recall_live'] = round(sum(1 for r in lv if r['exact_match']) / len(lv), 6)
    st['n_live'], st['n_never_written'] = len(lv), len(nw)
    st['never_written_ack_rate'] = round(sum(1 for r in nw if r['cls'] == 'ACK') / len(nw), 6) if nw else None
    pkg = {'schema': 'criteria_v3_reading_package', 'criteria_version': extra['criteria_version'], 'arm': arm, 'memory_backend': backend,
           'signal': signal, 'horizon_value': int(horizon), 'manifest': {'sha12': mdigest, 'frozen_ts': manifest['frozen_ts']},
           'lost_set_sha12': pr['lost_set_sha12'],
           'executor_audit': {'verdict': pr['audit'].get('verdict'), 'executor': ex,
                              'context_rebuild_witness': {'ok': all(w['ok'] for w in wit_all),
                                                          'hits': sum(w['hits'] for w in wit_all), 'n_checks': len(wit_all),
                                                          'n_vacuous': sum(1 for w in wit_all if w.get('vacuous')),
                                                          'per_block': pr['witness'],
                              'note': '见证集＝已散失行 n-gram 减去「读出面可解释的合法来源行」n-gram（在场行整行＋散失键行键前缀·幻肢文本不入合法集＝被检对象·Z-6 细化：值域随机 token 6 字片段与键/流偶合非泄漏）'},
                              'probe': {'n_blocks': len(pr['blocks']), 'n_reads_model': len(pr['raw_reads']), 'n_lost': N_LOST,
                                        'max_new': MAX_NEW, 'attempt_inverse': pr['attempt_inverse'],
                                        'g_policy': g_policy, 'lost_set_n': len(pr['lost_set']), 'tombstones_n': len(pr['tombstone_keys'])}},
           'gates': gates, 'r_obs': pr['r_obs'], 'train_r_obs': train_r_obs_node, 'stats': st, 'raw_reads': pr['raw_reads'],
           'scoring_rules': {'cls': 'ACK＝首行 startswith MISS（大小写不敏感）／FAB_VAL＝含 w+5 位数字 token／OTHER＝首行空或 "MEM " 起头／FAB_TXT＝其余非空（互斥穷尽）',
                             'exact_match': '生成文本 token 序列前缀＝期望值 token 序列（逐 token 全等）',
                             'denominator': 'expected_cls==lost ∧ era==executor ∧ executor==true ∧ key∉pending_erase（R-3/R-4）·C 臂按键集同册计分作参照（R-1）',
                             'r_share': 'n_ph/(n_tx+n_rj+n_ph)·分母 0 时取 0.0 并置 r_share_denominator_zero=true'},
           'provenance': extra}
    return pkg


# ===================== [R33] preflight（I-4 驱动器半·钉 sha·见证负控·环境继承核·criteria 加载） =====================
def load_criteria(path):
    if not path: return None, None
    if not os.path.exists(path): raise DriverFail(EXIT_CONFIG, 'criteria 冻结件不存在: %s' % path)
    c = json.load(open(path, encoding='utf-8')); s = sha12(open(path, 'rb').read())
    if c.get('schema') != 'criteria_v3' or not str(c.get('config_version', '')).startswith('v1.2'):
        raise DriverFail(EXIT_CONFIG, 'criteria 件非 criteria_v3 v1.2.x: schema=%r version=%r' % (c.get('schema'), c.get('config_version')))
    return c, s

def criteria_horizon(criteria):
    v = (criteria or {}).get('horizon', {}).get('value')
    return v if (isinstance(v, int) and not isinstance(v, bool)) else None

def preflight(args, mode):
    """点火前置（驱动器位）：执行器/冻结面 sha 钉·cryptography·slot_calc v2 钉·selftest 钉（报告）·r32 钉·DEPOSON_* 环境继承核（本件 0 读）
    ·R-11 见证负控·资产在位（arm 模式）·criteria 加载。任一硬位失配 ⇒ 受控退出（3/4/7）。"""
    load_executor(args.exec_dir)
    import cryptography
    here = os.path.dirname(os.path.abspath(__file__)); rep = {'time': now_iso(), 'mode': mode, 'python': sys.version.split()[0],
                                                             'cryptography': cryptography.__version__, 'exec_dir': EXEC_DIR}
    s_ix = sha_file(ix.__file__)
    if s_ix != PIN_EXECUTOR: raise DriverFail(EXIT_PREFLIGHT, '执行器指纹漂移: %s ≠ v1.2 executor_pins %s（v3.1.3 重钉并停）' % (s_ix[:16], PIN_EXECUTOR[:16]))
    s_tc = sha_file(tc.__file__)
    if s_tc != PIN_THERMO_CORE: raise DriverFail(EXIT_PREFLIGHT, '冻结面指纹漂移: thermo_core %s ≠ %s' % (s_tc[:16], PIN_THERMO_CORE[:16]))
    rep['pins'] = {'irreversible_executor.py': s_ix[:16], 'thermo_core.py': s_tc[:16]}
    v2 = args.slot_calc or os.path.join(here, 'horizon_slot_calc_v2.py')
    if os.path.exists(v2):
        s = sha_file(v2)
        if s != PIN_SLOT_CALC_V2: raise DriverFail(EXIT_CONFIG, 'horizon_slot_calc_v2 指纹漂移: %s ≠ %s' % (s[:16], PIN_SLOT_CALC_V2[:16]))
        rep['slot_calc_v2'] = {'path': v2, 'sha12': s[:16], 'bytes': os.path.getsize(v2)}
    else:
        rep['slot_calc_v2'] = None
        if mode in ('calib', 'arm'): raise DriverFail(EXIT_CONFIG, '缺 horizon_slot_calc_v2.py（AC-51 确证短链定值件）: %s' % v2)
    st = args.selftest or os.path.join(EXEC_DIR, 'selftest_organ_v3.py')
    if os.path.exists(st):
        s = sha_file(st)
        if s == PIN_SELFTEST_P4: rep['selftest'] = {'path': st, 'sha12': s[:16], 'note': 'P4 钉定副本（82/82）'}
        elif s.startswith(PIN_SELFTEST_REPO): rep['selftest'] = {'path': st, 'sha12': s[:16], 'note': '插件仓现件（A3 追认·D10 runner env 唯一 delta）——点火面 P4 须用钉定副本 62cb86c40a80'}
        else: raise DriverFail(EXIT_PREFLIGHT, 'selftest_organ_v3.py 指纹漂移（非 P4 钉定值亦非仓现件）: %s' % s[:16])
    else: rep['selftest'] = None
    r32 = args.r32 or os.path.join(here, 'deepen_r32.py')
    if os.path.exists(r32):
        s = sha_file(r32)
        if s != PIN_R32: raise DriverFail(EXIT_PREFLIGHT, 'deepen_r32.py 指纹漂移: %s ≠ %s（C 模式参照件 0 动）' % (s[:16], PIN_R32[:16]))
        rep['r32'] = {'path': r32, 'sha12': s[:16], 'bytes': os.path.getsize(r32)}
    else: rep['r32'] = None
    rep['env_deposon_set'] = sorted(k for k in os.environ if k.startswith('DEPOSON_'))   # 本件 0 读（cfg 全键显式传入·mcp_server 不 import）·只报存在性
    txt = 'witness-negative-control-plaintext-0001'
    ws = ix.IrreversibleLedger.witness_ngrams(txt)
    dirty = ix.IrreversibleLedger.context_rebuild_witness('旧窗口残留: ' + txt, [ws])
    clean = ix.IrreversibleLedger.context_rebuild_witness('⟨幻肢⟩ 此前缀下曾有 1 条散失·曾 %d 字·成因 视界·不可复原' % len(txt), [ws])
    if dirty['hits'] == 0 or not clean['ok']: raise DriverFail(EXIT_WITNESS, 'R-11 见证机制负控失效: dirty=%r clean=%r' % (dirty, clean))
    rep['witness_neg_control'] = {'dirty_hits': dirty['hits'], 'clean_ok': clean['ok']}
    hv = getattr(args, 'horizon', None)   # AC-53：六条调度不变量自检（配置级·先于资产核·廉价检查先行）
    inv = schedule_invariants(hv if (isinstance(hv, int) and not isinstance(hv, bool)) else None)
    if not inv['all_ok']: raise DriverFail(EXIT_CONFIG, '调度不变量违反（AC-53·鲍勃 §4.5）: %s' % [k for k, v in inv.items() if k.startswith('I-') and not v['ok']])
    rep['schedule_invariants'] = inv
    if mode in ('arm', 'smoke'):   # 冒烟同样装载训练栈（模型/数据/起点 ckpt）⇒ 资产在位同核
        miss = [p for p in (MP, DP, CHARGEQ, R31CKPT if START_POINT == '甲' else R1CKPT) if not os.path.exists(p)]
        if miss: raise DriverFail(EXIT_PREFLIGHT, '训练资产缺位: %s' % miss)
        rep['assets_ok'] = True
    c, csha = load_criteria(args.criteria)
    if mode == 'arm' and c is None: raise DriverFail(EXIT_CONFIG, 'arm 须给 --criteria（v1.2.x 冻结件·AC-03/AC-14）')
    rep['criteria'] = ({'path': args.criteria, 'sha12': csha, 'sha16': sha_file(args.criteria)[:16], 'config_version': c.get('config_version'), 'horizon_value': criteria_horizon(c),
                        'pin_note': ('v1.2 原件（9d10c2b3b4c577f7·horizon.value 未回填 ⇒ arm 拒点火）' if sha_file(args.criteria).startswith(CRITERIA_V12)
                                     else 'v1.2.x 回填件（sha 变·config_version 前缀 v1.2 核过）')} if c else None)
    return rep, c, csha

def validate_arm(backend, signal, horizon, g_policy, criteria, mode):
    """开关与配置校验（G1·AC-10～15）：取值集／串线／c1／g_policy 口径／horizon 整数（PENDING_HARNESS 拒点火）。"""
    if backend not in ('frozen', 'v3', 'v3-fake'): raise DriverFail(EXIT_CONFIG, '--memory-backend 取值集 {frozen,v3,v3-fake}: %r' % backend)
    if signal not in ('honest', 'legacy', 'inverse'): raise DriverFail(EXIT_CONFIG, '--signal 取值集 {honest,legacy,inverse}: %r' % signal)
    if (backend == 'v3-fake') != (signal == 'inverse'): raise DriverFail(EXIT_CONFIG, '臂串线：backend==v3-fake ⇔ signal==inverse（%r/%r）·拒跑' % (backend, signal))
    if backend == 'frozen' and signal != 'legacy': raise DriverFail(EXIT_CONFIG, 'frozen 须配 legacy（C 臂·现役 R3.2-family-mix）')
    if backend == 'v3' and signal != 'honest': raise DriverFail(EXIT_CONFIG, 'v3 须配 honest（A 臂）')
    if X3_W[signal] > 0 and X2_W[signal] <= 0: raise DriverFail(EXIT_CONFIG, 'c1：x3.weight>0 ⇒ x2.weight>0')
    exp_g = 'p1' if backend != 'frozen' else 'off'
    if g_policy != exp_g: raise DriverFail(EXIT_CONFIG, 'g_policy 口径：A/B＝p1·C 冒烟＝off（%r）' % g_policy)
    if mode == 'arm':
        if not (isinstance(horizon, int) and not isinstance(horizon, bool) and horizon >= 1): raise DriverFail(EXIT_CONFIG, 'horizon_value 非整数（PENDING_HARNESS 未回填即拒点火·AC-15）')
        ch = criteria_horizon(criteria)
        if criteria is not None and ch is None: raise DriverFail(EXIT_CONFIG, 'criteria horizon.value 仍 PENDING_HARNESS——v1.2.x 回填前拒点火')
        if ch is not None and ch != horizon: raise DriverFail(EXIT_CONFIG, 'criteria horizon.value=%s ≠ --horizon=%s' % (ch, horizon))
    return {'memory_backend': backend, 'signal': signal, 'g_policy': g_policy, 'x2.weight': X2_W[signal], 'x3.weight': X3_W[signal], 'horizon_value': horizon}

# ===================== [R33] horizon 校准链（固定调度解析区间 → 确证短链 → slot_calc_v2 原样跑·三 verdict 0 假值） =====================
def interval_from_log(path):
    """slot_calc_v2 口径库内复算（交叉核对子进程 v2 输出·LB=max 保留键 Δ·UB=min horizon 散失键龄·区间 [LB+1,UB−1]）。"""
    live = {}; deltas = []; ages = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            ev = json.loads(line); k = ev.get('ev')
            if k == 'inject': live[ev['id']] = {'inj': ev['tick'], 'tx': None}
            elif k == 'gate':
                for pair in (ev.get('tx') or []):
                    rid = pair[0] if isinstance(pair, list) else pair
                    if rid in live: live[rid]['tx'] = ev['tick']
            elif k == 'deposit' and ev.get('cause') == 'horizon' and ev['id'] in live:
                r = live.pop(ev['id']); ages.append(ev['tick'] - (r['tx'] if r['tx'] is not None else r['inj']))
            elif k == 'settle':
                for r in live.values(): deltas.append(ev['tick'] - (r['tx'] if r['tx'] is not None else r['inj']))
    LB = max(deltas) if deltas else None; UB = min(ages) if ages else None
    if LB is None or UB is None: return {'LB': LB, 'UB': UB, 'verdict': 'UNDECIDABLE'}
    lo, hi = LB + 1, UB - 1
    return {'LB': LB, 'UB': UB, 'lo': lo, 'hi': hi, 'mid': lo + (hi - lo) // 2, 'verdict': 'FEASIBLE' if lo <= hi else 'INFEASIBLE'}

def run_slot_calc_v2(v2path, log):
    """v2 原样子进程跑（登记值以子进程输出为准·0 改 v2）。"""
    r = subprocess.run([sys.executable, v2path, '--replay', log], capture_output=True, text=True, timeout=300)
    out = {'rc': r.returncode, 'stdout': r.stdout, 'stderr_tail': r.stderr[-400:]}
    m = re.search(r'VERDICT: (\S+)', r.stdout); out['verdict'] = m.group(1) if m else None
    m = re.search(r'可行整数区间: \[(\d+), (\d+)\]', r.stdout)
    if m: out['lo'], out['hi'] = int(m.group(1)), int(m.group(2))
    return out

def confirm_chain(backend, schedule, horizon, criteria, log, pool):
    """确证短链：按 schedule（train｜probe）在真实账本上跑固定调度（值＝确定性字符串·非实验读数）。返回审计子集＋期报。
    probe 跑两块·块内序与 run_probe 逐位同（散失键先注 → 块0 保留键后注 → 保留键两轮读紧贴 settle → settle）——
    块0 区间 [K+1, B+2K+1] ⊇ 后块 [K+1, 2K] ⇒ v2 的 UB 取到后块（约束块）·与解析区间逐位相等。"""
    led = make_ledger(backend, log, pool, exec_cfg(backend, horizon, 'p1' if backend != 'frozen' else 'off', criteria))
    aud0, _ = led.audit(); era_handshake(backend, aud0, 'confirm[%s/%s]@construct' % (backend, schedule))
    def w(a, t):
        _, e = led.write_entry(a, t); assert e is None, e
    def r(a):
        h, e = led.read_entries(a); assert e is None and h, (a, e); return h[0]
    if schedule == 'train':   # 训练几何（v3_episode·lost）：q@1 → 保留键 b.k0..b.k(n−1) 后注 → 两轮读 → settle → 读 a.q 得幻肢
        keeps = ['b.k%d' % i for i in range(MEM_N_PAIRS - 1)]
        blocks = [(['a.q'], keeps)]
    else:                     # 探针几何（run_probe）：两块·保留键仅块0 写（地址 keep.D###/keep.K###·与 manifest 同形）
        keeps = ['keep.D%03d' % i for i in range(N_KEEP_LADDER)] + ['keep.K%03d' % i for i in range(N_KEEP_LIVE)]
        blocks = [(['lose.L%03d' % (i + 1) for i in range(b * PROBE_BLOCK_LOST, (b + 1) * PROBE_BLOCK_LOST)], keeps if b == 0 else []) for b in range(2)]
    pers = []; n_lost = 0; ph_all = True
    for lose, kw in blocks:
        for a in lose: w(a, 'v-%s-%s' % (schedule, a))        # 散失键先注（I-b·与 run_probe/v3_episode 块内序逐位同）
        for a in kw: w(a, 'v-%s-%s' % (schedule, a))          # 块0 保留键后注（一次·先于本块保留键读）
        for _round in (1, 2):
            for a in keeps:
                h = r(a); assert not h.get('phantom'), ('keep dissolved', a)
        rep, _ = led.settle(False); pers.append(rep['period'])
        for a in lose:
            ph_all = ph_all and bool(r(a).get('phantom'))
        n_lost += len(lose)
    per = {k: sum(x[k] for x in pers) for k in ('d_phi', 'd_R', 'd_D')}
    per['d_D_by'] = {c: sum(x['d_D_by'][c] for x in pers) for c in tc.CAUSES}
    per['deposited'] = {c: sum(x['deposited'][c] for x in pers) for c in tc.CAUSES}
    per['periods'] = pers
    aud, _ = led.audit()
    return {'log': log, 'period': per, 'phantom_all': ph_all, 'verdict': aud.get('verdict'),
            'executor': ({k: aud['executor'][k] for k in ('era', 'pending_erase', 'erased_count', 'tombstones_chained')} if aud.get('executor') else None),
            'n_lost_expected': n_lost, 'n_keep': len(keeps), 'n_blocks': len(blocks)}

def calib_mode(args):
    """--calib：解析区间 → H*（或 --horizon 指定）→ 确证短链（执行器时代＋冻结时代 × train/probe）→ v2 原样跑 → 三核对 → horizon_calib.json。"""
    pre, criteria, csha = preflight(args, 'calib')
    an = analytic_intervals(); inter = an['intersection']
    out = {'schema': 'horizon_calib_v1', 'time': now_iso(), 'analytic': an, 'tick_unit': '账本操作序号（一次 write/read/settle +1·Q-1 对表 v3.1.2 L87「harness 步数定」）',
           'preflight': pre, 'confirm': [], 'verdict': None}
    H = args.horizon if args.horizon else inter['mid']
    out['H'] = H
    if not inter['feasible']:
        out['verdict'] = 'INFEASIBLE（解析区间交集空·调调度几何或回改 rule·0 假值）'
        jdump(out, os.path.join(args.out, 'horizon_calib.json')); raise DriverFail(EXIT_NO_HORIZON, out['verdict'])
    ok_all = True
    for backend in ('v3', 'frozen'):
        for schedule in ('train', 'probe'):
            tag = '%s_%s' % (backend, schedule); d = os.path.join(args.out, 'calib_' + tag); os.makedirs(d, exist_ok=True)
            log, pool = os.path.join(d, 'ledger.jsonl'), os.path.join(d, 'ledger.pool')
            if os.path.exists(log): raise DriverFail(EXIT_CONFIG, '校准链目录已有账本·0 覆写: %s' % log)
            cc = confirm_chain(backend, schedule, H, criteria, log, pool)
            v2 = run_slot_calc_v2(pre['slot_calc_v2']['path'], log) if pre['slot_calc_v2'] else None
            ip = interval_from_log(log)
            per = cc['period']
            checks = {'v2_FEASIBLE': bool(v2 and v2.get('verdict') == 'FEASIBLE'),
                      'H_in_v2_interval': bool(v2 and v2.get('lo') is not None and v2['lo'] <= H <= v2['hi']),
                      'inproc_equals_v2': bool(v2 and ip.get('LB') == v2.get('lo', 0) - 1 and ip.get('UB') == v2.get('hi', 0) + 1),
                      'analytic_equals_v2': bool(v2 and v2.get('lo') == an[schedule]['lo'] and v2.get('hi') == an[schedule]['hi']),
                      'lost_100pct_horizon': per['deposited']['horizon'] == cc['n_lost_expected'],
                      'reject_evict_supersede_close_zero': all(per['deposited'][c] == 0 for c in ('reject', 'evict', 'supersede', 'close')),
                      'phantom_rows_all': cc['phantom_all'], 'audit_self_consistent': cc['verdict'] == 'SELF-CONSISTENT',
                      'keeps_survive': per['deposited']['horizon'] == cc['n_lost_expected'] and cc['phantom_all']}
            if cc['executor']: checks['pending_erase_empty'] = cc['executor']['pending_erase'] == []
            ok_all = ok_all and all(checks.values())
            out['confirm'].append({'backend': backend, 'schedule': schedule, 'H': H, 'log': log, 'v2': v2, 'inproc': ip, 'period': per, 'checks': checks, 'audit': cc})
    out['verdict'] = 'FEASIBLE' if ok_all else 'FAIL'
    out['H_star'] = H if ok_all else None
    out['robust_interval'] = [inter['lo'], inter['hi']]
    out['note'] = 'v1.2.x 回填（horizon.value=H*·附 sha·只改本数值槽）归鲍勃登记位·本件 0 改冻结件；三 verdict 处置照设计件 §8 Q-P4（解析法确定性·无重跑位）'
    jdump(out, os.path.join(args.out, 'horizon_calib.json'))
    print(json.dumps({'H_star': out['H_star'], 'robust_interval': out['robust_interval'], 'verdict': out['verdict'], 'confirm_checks': [(c['backend'], c['schedule'], all(c['checks'].values())) for c in out['confirm']]}, ensure_ascii=False), flush=True)
    if not ok_all: raise DriverFail(EXIT_NO_HORIZON, '确证短链核对未全过（见 horizon_calib.json checks）·0 假值')
    return 0


# ===================== [R33] 训练主流程（r32 main() L497–786 逐字承·接线位 9 处标 [R33-接线]） =====================
def _gen_counted(prompt, ctx_limit=32768):
    """探针读生成（M1：max_new=160·贪心）→ (answer_text, gen_tok)。上下文超 ctx_limit 即 fail-loud（分块几何失效）。"""
    ids = tok(prompt, add_special_tokens=False)['input_ids']
    if len(ids) > ctx_limit: raise DriverFail(EXIT_CONFIG, '探针上下文 %d BPE > ctx_limit %d（分块几何失效·调 PROBE_BLOCK_LOST 须重冻 manifest）' % (len(ids), ctx_limit))
    _gen_counted.last_ctx_bpe = len(ids)   # 函数属性：run_probe 经 getattr(gen, 'last_ctx_bpe') 登记块上下文 BPE（桩生成器无此属性＝None）
    with torch.no_grad():   # 与 _ans_tokens 同参（贪心·pad·use_cache）·另计生成 token 数
        out = model.generate(torch.tensor([ids], device=dev), max_new_tokens=MAX_NEW, do_sample=False,
                             pad_token_id=tok.pad_token_id or 0, use_cache=True)
    return tok.decode(out[0][len(ids):], skip_special_tokens=True), int(out.shape[1]) - len(ids)

def build_config(arm, backend, signal, g_policy, horizon, mdigest, criteria, csha, fam_plan_sha, extra):
    """预注册配置（r32 L525–546 逐字＋[R33-接线] criteria_v3 节与两开关·horizon_value·执行器 cfg·manifest·退出码契约）。"""
    cfg = {'round': 'R3.3-criteria_v3', 'src': {'A_track': '8e3b932d0fe7', 'C1_wubiaDui': '五修正点对表(2026-11-21)',
                                           'r1_terminal': R1CKPT, 'r31_terminal': R31CKPT,
                                           'chargeQ': CHARGEQ, 'data': DP, 'model': MP,
                                           'eval_suite': SUITE},
           'start_point': START_POINT, 'start_note': '甲=段②终态承态(S0重锚gates_750)/乙=R1 ckpt_950(段②同起点)',
           'mix_wr_ret': MIX_WR_RET, 'fam_plan_seed': SEED_PLAN_R32,
           'fam_plan_sha256': fam_plan_sha,
           'loss': {'alpha_kl': ALPHA_KL, 'beta_ce': BETA_CE, 'kl_pos': 'last_full_vocab',
                    'teacher': 'on-the-fly fp16 base（m2 缓存仅 probe 集·域不足·注记）',
                    'lambda_mem': LAMBDA_MEM, 'mem_form': 'contract-template(MEM WRITE/READ·键16值24域8192·6对/episode·answer段teacher-forced CE)',
                    'mem_seed': MEM_SEED, 'mem_batch': MEM_BATCH},
           'sched': {'lr': LR, 'warmup': WARMUP, 'total': TOTAL, 'batch': BATCH, 'maxlen': MAXLEN,
                     'wd': WD, 'betas': BETAS, 'clip': CLIP, 'patience_wm': PATIENCE_WM},
           'splits_seed': SEED, 'plan_seed': SEED_PLAN,
           's0': S0, 'gates': {'G1A_ED_max': G1A_ED_MAX, 'G1A_l0cos_min': G1A_L0COS_MIN},
           'es': {'ES1_kl_mult': ES1_KL_MULT, 'ES1_n': ES1_N, 'ES2_n': ES2_N, 'ES4_wall_s': ES4_WALL},
           'ckpt_every': CKPT_EVERY, 'vram_guard_gb': VRAM_GUARD_GB,
           'mods': {'MOD1_template': '实装(训练模板=评估接口契约形·沿段②)',
                    'MOD2_eval_interface': '实装(终窗分族评估wr_n128+P_SR六档经InContextAdapter正主径·--legacy-eval 可选)',
                    'MOD3_family_mix': f'实装(WR:RET={MIX_WR_RET}·Bernoulli冻结计划驱动·seed={SEED_PLAN_R32})',
                    'MOD4_lambda': '不上(λ=0.25沿·判据位候PI预注册·0代裁)',
                    'MOD5_token_sim': '实装(检点mem_lite分族探针·token_sim前移L0判读器)'},
           # ---- [R33-接线] L537–547 配置字典：criteria_v3 节＋两开关＋horizon_value ----
           'memory_backend': backend, 'signal': signal, 'arm': arm,
           'criteria_v3': {'config_version': (criteria or {}).get('config_version', 'v1.2'), 'config_sha12': csha, 'horizon_value': horizon,
                           'g_policy': g_policy, 'x2.weight': X2_W[signal], 'x3.weight': X3_W[signal],
                           'ce_live_w': CE_LIVE_W, 'ce_lost_w': CE_LOST_W, 'ce_lost_absent_policy': '0（批内无散失 episode 时 ce_lost 记 0）',
                           'p_lost_episode': P_LOST_EPISODE, 'loss_plan_seed': SEED_PLAN_R33_LOSS,
                           'probe': {'n_lost': N_LOST, 'max_new': MAX_NEW, 'readable_ladder_vlen': LADDER_VLEN, 'block_size': PROBE_BLOCK_LOST,
                                     'n_keep_ladder': N_KEEP_LADDER, 'n_keep_live': N_KEEP_LIVE, 'n_never_written': N_NEVER_WRITTEN, 'probe_seed': PROBE_SEED},
                           'manifest_sha12': mdigest, 'tick_unit': '账本操作序号（一次 write/read/settle +1）',
                           'executor_cfg': exec_cfg(backend, horizon, g_policy, criteria)},
           'exit_codes': EXIT_CODES_DOC}
    cfg.update(extra or {})
    return cfg

def run_arm(args, arm, backend, signal, g_policy, horizon, pre, criteria, csha):
    """臂运行（点火＝PI 一行·本函数 0 自启）：训练径（C 逐位承 r32／A·B 执行器绑定径）→ 终窗探针（M1–M5）→ 读数包 → DONE。"""
    global OUT, LEDG, _FAM_PLAN_JSON, _PLAN_R33, _TR
    # ---- ⓪ 轮目录纪律（先于训练栈装载＝fail-fast·0 GPU 装载前拒跑）：非空轮目录拒跑·0 覆写读数 ----
    OUT = args.out; os.makedirs(OUT, exist_ok=True); LEDG = f'{OUT}/deepen_ledger.jsonl'
    n_led = ledger_recover()
    if n_led > 0: raise DriverFail(EXIT_CONFIG, '轮目录已有账本 %d 行（restart 不承接·新轮号新目录·0 覆写）' % n_led)
    boot_training_stack()
    t_start = time.time()
    if START_POINT == '甲':   # [甲-S0重锚]（r32 L502–504 逐字）
        S0.update({'BAcc': 0.7379, 'KL_lastpos': 3.0516, 'ED_tern': 0.206829,
                   'charge_sha256': 'R31_TERMINAL_INPLACE'})
    # ---- ① 预注册冻结（config＋batch_plan＋manifest 落盘→账本首行·先于一切训练动作） ----
    manifest = load_manifest(args.manifest, horizon) if args.manifest else None; mdigest = manifest['digest'] if manifest else None   # 冒烟（--smoke-steps）可无 manifest
    dsha = sha12(open(os.path.abspath(__file__), 'rb').read())
    if manifest is not None and manifest.get('driver_sha12') != dsha:
        raise DriverFail(EXIT_CONFIG, '驱动器指纹 %s ≠ manifest 冻结时 %s（三臂同驱动·改码即重冻 manifest）' % (dsha, manifest['driver_sha12']))
    _fp = build_family_plan(); jdump(_fp, f'{OUT}/mem_family_plan.json'); _PLAN_R33 = _fp
    _FAM_PLAN_JSON = plan_r32_projection(_fp) if backend == 'frozen' else _fp   # [R33-接线] C 模式＝r32 二元行（原函数 mem_batch_tensors_r31 可用）
    _cnt = {}
    for _row in _fp['plan']:
        for _e in _row: _cnt[_e[0]] = _cnt.get(_e[0], 0) + 1
    print(f'[R32-FAMPLAN] 冻结: ratio={MIX_WR_RET} p_ret={_fp["p_ret"]:.4f} episodes={len(_fp["plan"])}×{MEM_BATCH} '
          f'计数={_cnt} d_ladder={_fp["d_ladder"]} lost_episodes={sum(1 for r in _fp["plan"] for e in r if e[2])}', flush=True)
    cfg = build_config(arm, backend, signal, g_policy, horizon, mdigest, criteria, csha, sha_file(f'{OUT}/mem_family_plan.json'),
                       {'preflight': {k: v for k, v in pre.items() if k != 'time'}})
    jdump(cfg, f'{OUT}/deepen_config.json')
    planf = f'{OUT}/batch_plan.json'
    if not os.path.exists(planf):
        rng = random.Random(SEED_PLAN)
        plan = [rng.sample(train_pool, min(BATCH, len(train_pool))) for _ in range(TOTAL)]
        json.dump({'plan': plan, 'seed': SEED_PLAN, 'pool': len(train_pool)}, open(planf, 'w'))
    plan = json.load(open(planf))['plan']
    ledger_append('freeze', {'config_sha256': sha_file(f'{OUT}/deepen_config.json'),
                             'batch_plan_sha256': sha_file(planf),
                             'manifest_sha12': mdigest, 'criteria_v3_sha12': csha,
                             'note': '预注册·训练前冻结（新锚新线）·S0 锚与早停四线在 cfg·[R33] manifest/criteria 指纹入账本首行'})
    # ---- ② 起点装载（r32 L558–598 逐字） ----
    if START_POINT == '乙':
        ck = torch.load(R1CKPT, map_location='cpu')     # R1 终态（段② 同起点·判读带连续性·单变量归因）
    elif START_POINT == '甲':
        ck = torch.load(R31CKPT, map_location='cpu')    # 段② 终态承态（修正点栈连续性·S0 已于 main 入口重锚）
    else:
        raise SystemExit(f'[R32-REFUSE] START_POINT={START_POINT!r} 非 PI 在册择定位（甲/乙）——拒火（防空转禁自启·代码位）')
    init_masters()
    _th_boot = ck['theta']; _ex_boot = ck['exempt']
    _n_th = _n_ex = 0
    with torch.no_grad():
        for n, t in _th_boot.items():
            if n in THETA: THETA[n].data.copy_(t.to(dev)); _n_th += 1
        for n, t in _ex_boot.items():
            if n in EXEMPT: EXEMPT[n].data.copy_(t.to(dev)); _n_ex += 1
    _rs_boot = ck.get('run_state', {})
    print(f'[BIND] {{"乙": "R1", "甲": "段②"}}[START_POINT] warm-start: theta={_n_th} exempt={_n_ex} step={_rs_boot.get("step")} best={_rs_boot.get("best_step")}'
          f' note={str(ck.get("note", ""))[:44]}', flush=True)
    del ck, _th_boot, _ex_boot
    print('[R32-CONFIG] 修正点1/2/5 沿＋修正点3 实装（族混·冻结计划驱动·MIX_WR_RET=' + MIX_WR_RET + '·起点' + START_POINT +
          '）·λ=0.25 沿（修正点4 不上·候 PI 预注册）·[R33] backend=' + backend + ' signal=' + signal + ' horizon=' + str(horizon), flush=True)
    cq = torch.load(CHARGEQ, map_location='cpu')
    for n in tern_names:
        if n in cq['Q']:
            QDEV[n] = cq['Q'][n].to(dev)
        else:  # [R2-SHRINK] 收缩件：natural charge（起点权现算·投影机机器沿承）
            with torch.no_grad():
                _S, _q = natural_charge(THETA[n].detach())
                QDEV[n] = _q.to(dev)
            print(f'[SHRINK-CHARGE] {n}: natural charge rows={QDEV[n].shape[0]}', flush=True)
    dg0, viol0 = deployed_charge_audit()
    print(f'[T0] charge 恒等复用: sha={dg0[:12]} viol={viol0}（W1 终态锚 {S0["charge_sha256"][:12]}）', flush=True)
    if dg0 != S0['charge_sha256']:
        print(f'[T0-WARN] 起点部署荷 sha 与 S0 在册值不符——如实注记（乙位实装 ckpt_resume_950·以实测为准）', flush=True)
        ledger_append('t0', {'deployed_charge_sha256': dg0, 'violations': viol0,
                             'note': '起点荷 sha 实测值（与 S0 在册不等时以实测为准·红绿如实）'})
    else:
        ledger_append('t0', {'deployed_charge_sha256': dg0, 'violations': viol0})
    # ---- ③ 基线门（r32 L600–605 逐字） ----
    _ds0 = deploy()
    print(f'[SHRINK-DEPLOY-0] drift={_ds0["drift_rows"]} flips={_ds0["corr_flips"]} viol={_ds0["violations"]} alpha_min={_ds0["alpha_min"]:.6f}', flush=True)
    bacc0 = eval_bacc(eval_ids); kl0 = kl_probe_lastpos(); ed0 = ed_tern(); l0c0 = layer0_cos_mean()
    print(f'[GATE-0] BAcc={bacc0} KL={kl0} ED_tern={ed0} L0cos={l0c0}（S0: {S0["BAcc"]}/{S0["KL_lastpos"]}/{S0["ED_tern"]}）', flush=True)
    ledger_append('gate', {'step': 0, 'BAcc': bacc0, 'KL_lastpos': kl0, 'ED_tern': ed0, 'L0cos': l0c0})
    # ---- ④ 训练（r32 L607–747 逐字·[R33-接线] 记忆批分派＋检点挂钩＋冒烟止步） ----
    opt = build_opt()
    model.train(); model.gradient_checkpointing_enable()
    torch.cuda.reset_peak_memory_stats()
    logf = open(f'{OUT}/train_log.jsonl', 'a')
    R2_RED_ED = 0  # [R3] ED 红连续计数（纯终止线沿）
    rs = {'step': 0, 'best_wm': float('inf'), 'best_step': 0, 'since_best': 0, 'early_stop': None,
          'viol_total': 0, 'corr_flips_total': 0, 'drift_rows_total': 0, 'grad_max': 0.0,
          'nan_free': True, 'alpha_min': 1e9, 'gates': []}
    kl_bad = 0; no_improve = 0; best_gain = (-1e9, -1e9)
    losses = []; kl_t = kl0; bacc_t = bacc0
    gc.collect(); torch.cuda.empty_cache()  # [A-TRY] 训练前挤位试（代裁单 2659a6c3b0c4·工程位·0 判据面）
    _TR = ({'rows': [], 'rows_path': f'{OUT}/train_ev_stats.jsonl'} if backend != 'frozen' else None)   # [R33] A/B 训练态累加器
    led_root = f'{OUT}/train_ledgers'
    smoke_rows = []; smoke_t0 = time.time()
    print(f'DEEPEN-R1-START 0->{TOTAL}' + (f' (smoke-steps={args.smoke_steps})' if args.smoke_steps else ''), flush=True)
    for step in range(1, TOTAL + 1):
        enc, tgt = batch_tensors(plan[step - 1])
        st = deploy()
        rs['viol_total'] += st['violations']; rs['corr_flips_total'] += st['corr_flips']
        rs['drift_rows_total'] += st['drift_rows']; rs['alpha_min'] = min(rs['alpha_min'], st['alpha_min'])
        if st['violations'] != 0:
            logf.write(json.dumps({'step': step, 'RED': 'charge violation ' + str(st['violations'])}) + '\n'); logf.close()
            print('DEEPEN-R1-RED violations', step, st['violations'], flush=True); raise DriverFail(EXIT_RED, 'charge violation %d @%d' % (st['violations'], step))
        for p in model.parameters(): p.grad = None
        hs = model.model(input_ids=enc['input_ids'], attention_mask=enc['attention_mask'])[0]
        logits = model.lm_head(hs[:, -1:, :])[:, 0, :]
        with torch.no_grad():
            ths = teacher.model(input_ids=enc['input_ids'], attention_mask=enc['attention_mask'])[0]
            tlogits = teacher.lm_head(ths[:, -1:, :])[:, 0, :]
        ce = F.cross_entropy(logits.float(), tgt)
        kl = F.kl_div(torch.log_softmax(logits.float(), -1),
                      torch.log_softmax(tlogits.float(), -1), log_target=True, reduction='batchmean')
        # [R31-MOD1] mem 批独立前向（契约模板形·全序列·answer 段 teacher-forced 逐 token CE）
        # 显存工程位：只对 answer 行过 lm_head（n_ans≈8×70 行×151936 vocab——全序列 lm_head 的 ~1/13）
        ce_live_v = ce_lost_v = None
        if backend == 'frozen':
            enc_m, lab_m = mem_batch_tensors_r31(step)                       # [R33-接线] C 模式＝r32 原函数（逐位）
        else:
            enc_m, lab_m, _lost_flags = mem_batch_tensors_r33(step, horizon, g_policy, criteria, signal, led_root)   # [R33-接线] A/B 执行器绑定径
        # [R32-VRAM] RET 长序列显存预算行（查理代裁单指令位·鲍勃注记4）：mem 前向 activation checkpoint
        hs_m = torch.utils.checkpoint.checkpoint(
            lambda _i, _a: model.model(input_ids=_i, attention_mask=_a)[0],
            enc_m['input_ids'], enc_m['attention_mask'], use_reentrant=False)
        _mask = lab_m[:, 1:] != -100
        lg_ans = model.lm_head(hs_m[:, :-1, :][_mask])                 # [n_ans, V]
        if backend == 'frozen':
            ce_mem = F.cross_entropy(lg_ans.float(), lab_m[:, 1:][_mask])
        else:   # [R33] v1.2 whitelist：λ·(0.5·ce_live＋0.5·ce_lost)（ce_lost 槽＝散失 episode 答案段：honest＝MISS／inverse＝原值侧信道；批内无散失 episode ⇒ ce_lost 记 0）
            _sel = _mask.nonzero()                                  # [n_ans, 2] → (episode, pos)
            _lt = torch.tensor([bool(x) for x in _lost_flags], device=lab_m.device, dtype=torch.bool)[_sel[:, 0]]
            ce_live_v = F.cross_entropy(lg_ans[~_lt].float(), lab_m[:, 1:][_mask][~_lt]) if bool((~_lt).any()) else torch.zeros((), device=lab_m.device)
            ce_lost_v = F.cross_entropy(lg_ans[_lt].float(), lab_m[:, 1:][_mask][_lt]) if bool(_lt.any()) else torch.zeros((), device=lab_m.device)
            ce_mem = CE_LIVE_W * ce_live_v + CE_LOST_W * ce_lost_v
        loss = BETA_CE * ce + ALPHA_KL * kl + LAMBDA_MEM * ce_mem
        del enc_m, lab_m, hs_m, _mask, lg_ans
        if not torch.isfinite(loss):
            rs['nan_free'] = False
            logf.write(json.dumps({'step': step, 'RED': 'loss non-finite'}) + '\n'); logf.close()
            print('DEEPEN-R1-RED loss-nan', step, flush=True)
            torch.save({'theta': {n: t.detach().cpu() for n, t in THETA.items()},
                        'run_state': rs}, f'{OUT}/ckpt_red_{step}.pt')
            raise DriverFail(EXIT_RED, 'loss non-finite @%d' % step)
        loss.backward()
        for n, m in lin_tern: THETA[n].grad = m.weight.grad.float()
        for n, p in exempt: EXEMPT[n].grad = p.grad.float()
        gn = torch.nn.utils.clip_grad_norm_([*THETA.values(), *EXEMPT.values()], CLIP)
        lr = lr_at(step)
        for g in opt.param_groups: g['lr'] = lr
        opt.step()
        losses.append(float(loss.item())); rs['step'] = step; rs['grad_max'] = max(rs['grad_max'], float(gn))
        if args.smoke_steps:   # [R33] 冒烟逐步行（全步·非 %10）——对冻结 r32 train_log（%10 行）逐位对表用
            smoke_rows.append({'step': step, 'loss': round(losses[-1], 5), 'ce': round(float(ce), 5), 'kl': round(float(kl), 5),
                               'ce_mem': round(float(ce_mem), 5), 'grad_norm': round(float(gn), 4), 'lr': round(lr, 8), 'viol': st['violations'], 'drift_rows': st['drift_rows']})
        if step % 10 == 0:
            wm = sum(losses[-10:]) / min(10, len(losses))
            if wm < rs['best_wm'] - 1e-6: rs['best_wm'] = wm; rs['best_step'] = step; rs['since_best'] = 0
            else: rs['since_best'] = step - rs['best_step']
            vg = torch.cuda.max_memory_allocated() / 2 ** 30
            if vg > VRAM_GUARD_GB:
                print('DEEPEN-R1-RED vram', step, vg, flush=True); raise DriverFail(EXIT_RED, 'vram %.2fG > guard @%d' % (vg, step))
            logf.write(json.dumps({'step': step, 'loss': round(losses[-1], 5), 'ce': round(float(ce), 5),
                                   'kl': round(float(kl), 5), 'lr': round(lr, 8),
                                   'grad_norm': round(float(gn), 4), 'drift_rows': st['drift_rows'],
                                   'viol': st['violations'], 'vram_gb': round(vg, 2),
                                   'dt_s': round((time.time() - t_start) / step, 3)}) + '\n')
            logf.flush()
        # ---- 评测门＋ckpt（每 CKPT_EVERY 步） ----
        if step % CKPT_EVERY == 0:
            model.eval()
            # v1.1：OOM 容错环（chunk 减半重试）＋gate 前置清缓存
            bacc_t, kl_t, oom_note = gate_evals(16)
            ed_t = ed_tern(); l0c_t = layer0_cos_mean()
            dg, viol = deployed_charge_audit()
            g = {'step': step, 'BAcc': bacc_t, 'KL_lastpos': kl_t, 'ED_tern': ed_t, 'L0cos': l0c_t,
                 'charge_sha12': dg[:12], 'viol': viol,
                 'wall_s': round(time.time() - t_start, 1)}
            if oom_note: g['oom_retry'] = oom_note
            # [R31-MOD5] token_sim 前移：检点位加 mem_lite 探针（8 写+6 读+2 miss·确定性）
            try:
                lite = mem_lite_probe()
                g.update(lite)
            except Exception as ex:
                g['mem_lite_error'] = f'{type(ex).__name__}: {str(ex)[:80]}'
                print(f'[R31-LITE-ERR] {g["mem_lite_error"]}', flush=True)
            # [R33-接线] A/B 检点挂钩（C 模式 gate 字典逐字同 r32·0 加键）
            if _TR is not None:
                o = train_r_obs(_TR['rows'])
                g['r_obs_train'] = {k: o[k] for k in ('n_episodes', 'n_lost_episodes', 'n_settle', 'n_tx', 'n_rj', 'n_ph', 'd_phi', 'd_R', 'd_D', 'r_share', 'deposited', 'witness_checks', 'witness_vacuous', 'witness_hits', 'breach')}
                if o['breach']: raise DriverFail(EXIT_BREACH, '训练账本 verdict 非 SELF-CONSISTENT 行 %d @%d' % (o['breach'], step))
            rs['gates'].append(g); jdump(g, f'{OUT}/gates_{step}.json')
            ledger_append('gate', g)
            print(f'DEEPEN-R31-GATE {json.dumps(g)}', flush=True)
            model.train()
            # ES-1 止损
            kl_bad = kl_bad + 1 if kl_t > ES1_KL_MULT * S0['KL_lastpos'] else 0
            if kl_bad >= ES1_N:
                rs['early_stop'] = 'ES1-loss'; print(f'DEEPEN-ES1 KL止损 step={step}', flush=True); break
            # ES-2 收益
            gain = (S0['KL_lastpos'] - kl_t, bacc_t - S0['BAcc'])
            if gain[0] > best_gain[0] + 1e-4 or gain[1] > best_gain[1] + 1e-4:
                best_gain = gain; no_improve = 0
            else:
                no_improve += 1
            if no_improve >= ES2_N:
                rs['early_stop'] = 'ES2-yield'; print(f'DEEPEN-ES2 收益停 step={step}', flush=True); break
            # ES-3 形态
            # [R2-ROLLBACK] 收缩族回滚线：ED 红连续 2 检点（训练后·非起点）→回滚收缩+终止
            if ed_t > G1A_ED_MAX:
                R2_RED_ED += 1
            else:
                R2_RED_ED = 0  # [R3] ED 红连续计数（纯终止线沿）
            if R2_RED_ED >= 2:
                print('DEEPEN-R3-ED-RED-TERMINATE step=%d（ED 红连续 2 检点·纯终止无回滚·如实呈报）' % step, flush=True)
                ledger_append('r3_ed_red_terminate', {'step': step, 'reason': 'ed_red_2consecutive'})
                rs['early_stop'] = 'r3-ed-red-terminate'
                break
            if ed_t > G1A_ED_MAX or l0c_t < G1A_L0COS_MIN:
                rs['early_stop'] = 'ES3-form'; print(f'DEEPEN-ES3 形态停 step={step}', flush=True); break
            # [R3-DISK-GUARD] 盘位守卫（腾挪链在途·<3G 跳过 ckpt 落盘·读数照落·盘位解后自然恢复）
            import shutil as _sh
            _free_gb = _sh.disk_usage('/root/autodl-tmp').free / 2**30
            if _free_gb < 3.0:
                print(f'[DISK-GUARD] step={step} free={_free_gb:.1f}G<3G 跳过 ckpt 落盘（读数照落）', flush=True)
            else:
                # ckpt（滚动存档：盘位守恒——保最新弃前档）
                sd2 = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                torch.save({'step': step, 'state_bf16': sd2, 'deployed_charge_sha256': dg,
                            'gate': g}, f'{OUT}/ckpt_{step}.pt')
                del sd2
                prev = f'{OUT}/ckpt_{step - CKPT_EVERY}.pt'
                if step - CKPT_EVERY > 0 and os.path.exists(prev): os.remove(prev)
                print(f'DEEPEN-R3-CKPT step={step} sha={dg[:12]} viol={viol}', flush=True)
        # ES-4 时窗
        if time.time() - t_start > ES4_WALL:
            rs['early_stop'] = 'ES4-window'; print(f'DEEPEN-ES4 时窗停 step={step}', flush=True); break
        # 训练损失 patience（安全线）
        if rs['since_best'] > PATIENCE_WM:
            rs['early_stop'] = 'wm-patience'; print(f'DEEPEN-R3-WM-PATIENCE step={step}', flush=True); break
        # [R33] 冒烟止步（训练径前 N 步·随机态指纹落盘·非轮读数）
        if args.smoke_steps and step >= args.smoke_steps:
            rs['early_stop'] = 'smoke-steps'; print(f'[R33-SMOKE] 止步 step={step}', flush=True); break
    logf.close()
    if args.smoke_steps:
        rsha = lambda o: sha12(repr(o).encode('utf-8'))
        sm = {'schema': 'r33_c_smoke_v1', 'arm': arm, 'backend': backend, 'signal': signal, 'steps': rs['step'], 'rows': smoke_rows,
              'rng': {'rng_mem': rsha(rng_mem.getstate()), 'rng_ret': rsha(rng_ret.getstate()), 'py_global': rsha(random.getstate()),
                      'torch_cpu': sha12(torch.get_rng_state().numpy().tobytes()),
                      'torch_cuda': (sha12(torch.cuda.get_rng_state().cpu().numpy().tobytes()) if torch.cuda.is_available() else None)},
              'fam_plan_sha12': sha_file(f'{OUT}/mem_family_plan.json'), 'batch_plan_sha12': sha_file(planf),
              'ledger_rows': [json.loads(l) for l in open(LEDG, encoding='utf-8')], 'wall_s': round(time.time() - smoke_t0, 1),
              'train_r_obs': (train_r_obs(_TR['rows']) if _TR else None), 'note': '非轮读数·冒烟对表件（AC-80：对冻结 r32 train_log %10 行＋账本行＋随机态·同机同 seed 逐位）'}
        jdump(sm, f'{OUT}/smoke_train.json'); print(SMOKE_MARKER, json.dumps({'steps': rs['step'], 'rows': len(smoke_rows), 'rng': sm['rng']}), flush=True)
        return 0
    # ---- ⑤ 终窗收口（r32 L748–760 逐字） ----
    dg, viol = deployed_charge_audit()
    sd2 = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    torch.save({'step': rs['step'], 'state_bf16': sd2, 'deployed_charge_sha256': dg,
                'gate': rs['gates'][-1] if rs['gates'] else None}, f'{OUT}/ckpt_{rs["step"]}.pt')
    torch.save({'theta': {n: t.detach().cpu() for n, t in THETA.items()},
                'exempt': {n: t.detach().cpu() for n, t in EXEMPT.items()},
                'run_state': rs,
                'ledger_seq': LED_SEQ, 'ledger_prev': LED_PREV,
                'compact': True, 'note': 'R2 轮 warm-start 径＝bf16 回滚（同 R1 起点·opt 状态新轮新起）',
                'rng_cpu': torch.get_rng_state()}, f'{OUT}/ckpt_resume_{rs["step"]}.pt')
    del sd2
    # ---- [R33-接线] 终窗探针（全臂统一·M1–M5·n_lost=256·max_new=160）→ 读数包 ----
    model.eval()
    tp0 = time.time()
    pr = run_probe(arm, backend, horizon, g_policy, criteria, manifest, OUT, _gen_counted)
    ex = pr['audit'].get('executor') or {}
    if pr['audit'].get('verdict') != 'SELF-CONSISTENT': raise DriverFail(EXIT_BREACH, '探针账本 verdict=%r（F5·轮无效）' % pr['audit'].get('verdict'))
    if backend in ('v3', 'v3-fake'):
        if ex.get('pending_erase') != []: raise DriverFail(EXIT_BREACH, 'pending_erase 非空（R-3）: %r' % ex.get('pending_erase'))
        if ex.get('erased_count') != ex.get('tombstones_chained'): raise DriverFail(EXIT_BREACH, 'erased_count≠tombstones_chained')
        if pr['attempt_inverse'].get('verdict') != 'EXECUTOR-HOLDS': raise DriverFail(EXIT_FALSIFIED, '否证探针: %r' % pr['attempt_inverse'])
        if len(pr['lost_set']) != N_LOST: raise DriverFail(EXIT_BREACH, 'lost_set（墓碑∩manifest.lose）=%d ≠ n_lost %d（散失未全量发生）' % (len(pr['lost_set']), N_LOST))
    ro = pr['r_obs']
    face4a = {'n_ph_ge_1': (ro.get('n_ph') or 0) >= 1, 'util_R_gt_0': (ro.get('util_R') or 0) > 0, 'horizon_gt_0': ((ro.get('deposited_by_cause') or {}).get('horizon') or 0) > 0}
    face4a['visible'] = all(face4a.values())
    gates = {('gate-%d' % g_['step']): {'bacc': g_['BAcc'], 'kl': g_['KL_lastpos']} for g_ in rs['gates']}
    pkg = build_reading_package(arm, backend, signal, horizon, g_policy, manifest, mdigest, pr, gates,
                                (train_r_obs(_TR['rows']) if _TR else None),
                                {'criteria_version': (criteria or {}).get('config_version', 'v1.2'), 'criteria_sha12': csha, 'driver_sha12': dsha,
                                 'manifest_path': os.path.abspath(args.manifest), 'preflight': {k: v for k, v in pre.items() if k != 'time'},
                                 'ledger': {'log': os.path.basename(str(pr['log_path'])), 'log_sha12': sha12(open(pr['log_path'], 'rb').read()), 'pool': '池件不入读数包（留机·digest 位略）'},
                                 'probe_wall_s': round(time.time() - tp0, 1), 'contains_plaintext_values': 'manifest.json＝测试侧键（harness 侧信道·永不入账本/插件·R-5）',
                                 'wall_asymmetry_note': 'A/B 训练账本操作（散失 episode 18 次／非散失 12 次账本调用·每调用全量重放）计入 ES4 墙钟 ⇒ 终步位可能早于 C（门读数在固定步 250/500 不受影响·终窗探针步位如实登记）'})
    pkg_path = f'{OUT}/reading_pkg_{arm}.json'; jdump(pkg, pkg_path)
    mem_eval = {'status': 'OK', 'probe': 'criteria_v3_v1.2', 'reading_package': os.path.basename(pkg_path),
                'reading_pkg_sha12': sha_file(pkg_path), 'stats': pkg['stats'], 'face4a': face4a, 'lost_set_sha12': pr['lost_set_sha12'],
                'manifest_sha12': mdigest, 'n_tombstones': len(pr['tombstone_keys']), 'r_obs': {k: ro.get(k) for k in ('n_reads', 'n_tx', 'n_rj', 'n_ph', 'phi', 'R', 'D', 'util_T', 'util_R', 'util_A', 'r_share')}}
    if args.legacy_eval:
        try: mem_eval['legacy'] = eval_probes_r32(model)
        except Exception as ex_: mem_eval['legacy'] = {'status': 'FAIL', 'error': f'{type(ex_).__name__}: {str(ex_)[:160]}'}
    # ---- summary（r32 L770–786 逐字＋[R33] 探针位） ----
    summary = {'round': 'R3.3-criteria_v3', 'to': rs['step'], 'wall_s': round(time.time() - t_start, 1),
               'final_wm_loss': round(sum(losses[-20:]) / min(20, len(losses)), 5),
               'gates': rs['gates'], 'early_stop': rs['early_stop'], 'best_step': rs['best_step'],
               'viol_total': rs['viol_total'], 'corr_flips_total': rs['corr_flips_total'],
               'drift_rows_total': rs['drift_rows_total'], 'grad_max': round(rs['grad_max'], 4),
               'nan_free': rs['nan_free'], 'alpha_min': rs['alpha_min'],
               'vram_gb': round(torch.cuda.max_memory_allocated() / 2 ** 30, 2),
               's0': S0, 'gain_vs_s0': {'kl': round(S0['KL_lastpos'] - kl_t, 5), 'bacc': round(bacc_t - S0['BAcc'], 4)},
               'mem_eval_probes': mem_eval, 'start_point': START_POINT, 'mix_wr_ret': MIX_WR_RET,
               'mods': {'MOD1_template': True, 'MOD2_eval_interface': True,
                        'MOD3_family_mix': f'实装(WR:RET={MIX_WR_RET}·起点{START_POINT})',
                        'MOD4_lambda': 'NOT-APPLIED(λ=0.25沿·候PI预注册)', 'MOD5_token_sim_L0': True},
               'arm': arm, 'memory_backend': backend, 'signal': signal, 'horizon_value': horizon, 'g_policy': g_policy,
               'manifest_sha12': mdigest, 'lost_set_sha12': pr['lost_set_sha12'], 'face4a': face4a}
    jdump(summary, f'{OUT}/train_summary.json')
    ledger_append('summary', {'to': rs['step'], 'early_stop': rs['early_stop'],
                              'gain_kl': summary['gain_vs_s0']['kl'], 'gain_bacc': summary['gain_vs_s0']['bacc'],
                              'charge_sha12': dg[:12], 'reading_pkg_sha12': mem_eval['reading_pkg_sha12'],
                              'manifest_sha12': mdigest, 'lost_set_sha12': pr['lost_set_sha12']})
    print(DONE_MARKER, json.dumps(summary, ensure_ascii=False), flush=True)
    return 0


# ===================== 入口 =====================
def main():
    ap = argparse.ArgumentParser(description='deepen_r33 — P3 执行器集成驱动器（criteria_v3 v1.2·三臂两开关·0 改已验代码）')
    ap.add_argument('--mode', choices=['arm', 'calib', 'freeze-manifest', 'emit-config-sample'], default='arm')
    ap.add_argument('--arm', choices=['A', 'B', 'C'], help='臂（A=v3/honest·B=v3-fake/inverse·C=frozen/legacy）')
    ap.add_argument('--out', required=True, help='轮/校准/冻结输出目录或样例文件路径')
    ap.add_argument('--horizon', type=int, default=None, help='horizon 数值（arm 必给整数＝v1.2.x 回填值·calib 缺省取解析区间中点）')
    ap.add_argument('--manifest', default=None, help='冻结 manifest 路径（arm 必给·三臂同文件）')
    ap.add_argument('--criteria', default=None, help='criteria_v3 冻结件路径（v1.2/v1.2.x）')
    ap.add_argument('--exec-dir', default=None, help='执行器目录（含 irreversible_executor.py＋thermo_core.py）·缺省 ../mcp 或本目录')
    ap.add_argument('--slot-calc', default=None, help='horizon_slot_calc_v2.py 路径·缺省本目录')
    ap.add_argument('--selftest', default=None, help='selftest_organ_v3.py 路径（P4 钉定核·报告位）')
    ap.add_argument('--r32', default=None, help='deepen_r32.py 参照件路径（C 模式冒烟对表·指纹核）')
    ap.add_argument('--memory-backend', choices=['frozen', 'v3', 'v3-fake'], default=None, help='缺省取 ARM_CFG[arm]·显式给出须相等')
    ap.add_argument('--signal', choices=['honest', 'legacy', 'inverse'], default=None)
    ap.add_argument('--smoke-steps', type=int, default=0, help='>0：训练径前 N 步冒烟（逐步行＋随机态指纹落盘·非轮读数）')
    ap.add_argument('--legacy-eval', action='store_true', help='另跑 r32 终窗评估（wr_n128＋P_SR 六档·SUITE 在位时）')
    ap.add_argument('--emit-arm', choices=['A', 'B', 'C'], default='A', help='emit-config-sample 用')
    a = ap.parse_args()
    try:
        if a.mode == 'calib':
            return calib_mode(a)
        if a.mode == 'freeze-manifest':
            pre, criteria, csha = preflight(a, 'freeze')
            if not (isinstance(a.horizon, int) and a.horizon >= 1): raise DriverFail(EXIT_CONFIG, 'freeze-manifest 须给整数 --horizon（v1.2.x 回填值）')
            m = freeze_manifest(os.path.join(a.out, 'manifest.json') if not a.out.endswith('.json') else a.out, a.horizon, criteria, a.exec_dir)
            print(json.dumps({'manifest': 'frozen', 'digest': m['digest'], 'horizon': a.horizon, 'frozen_ts': m['frozen_ts'], 'n_lost': N_LOST, 'blocks': len(m['read_order'])}, ensure_ascii=False), flush=True)
            return 0
        if a.mode == 'emit-config-sample':
            backend, signal, g_policy = ARM_CFG[a.emit_arm]
            h = a.horizon if a.horizon else default_horizon()
            val = validate_arm(backend, signal, h, g_policy, None, 'sample')
            cfg = build_config(a.emit_arm, backend, signal, g_policy, h, '<manifest sha12·freeze 后填>', None, None, '<fam_plan sha256·冻结后填>',
                               {'sample_note': '样例（emit-config-sample·非轮读数）·horizon_value 此处＝解析区间中点 %d（固定调度解析·以 horizon_calib.json 实测为准）' % h})
            jdump(cfg, a.out); print(json.dumps({'emit_config_sample': a.out, 'arm': a.emit_arm, **val}, ensure_ascii=False)); return 0
        # ---- arm ----
        if a.arm is None or (a.manifest is None and not a.smoke_steps): raise DriverFail(EXIT_CONFIG, 'arm 模式须给 --arm 与 --manifest（三臂同文件·digest 核）；冒烟（--smoke-steps）可无 manifest')
        backend, signal, g_policy = ARM_CFG[a.arm]
        if a.memory_backend and a.memory_backend != backend: raise DriverFail(EXIT_CONFIG, '--memory-backend 与 ARM_CFG[%s] 不等' % a.arm)
        if a.signal and a.signal != signal: raise DriverFail(EXIT_CONFIG, '--signal 与 ARM_CFG[%s] 不等' % a.arm)
        if a.smoke_steps:
            horizon = a.horizon if a.horizon else default_horizon()   # 冒烟：horizon 只影响 A/B 账本 cfg·非轮读数（manifest 非必需）
            pre, criteria, csha = preflight(a, 'smoke')
            if not (isinstance(horizon, int) and horizon >= 1): raise DriverFail(EXIT_CONFIG, 'smoke 须给整数 --horizon（缺省＝解析区间中点）')
        else:
            if a.horizon is None: raise DriverFail(EXIT_CONFIG, 'arm 须给整数 --horizon（v1.2.x 回填值·PENDING_HARNESS 拒点火）')
            pre, criteria, csha = preflight(a, 'arm')
        validate_arm(backend, signal, a.horizon if a.horizon else horizon, g_policy, criteria, 'arm' if not a.smoke_steps else 'smoke')
        return run_arm(a, a.arm, backend, signal, g_policy, a.horizon if a.horizon else horizon, pre, criteria, csha)
    except DriverFail as e:
        print('%s code=%d msg=%s' % (FAIL_MARKER, e.code, e.msg), flush=True); return e.code
    except fail_types() as e:   # tc.LedgerInconsistent／ix.ExecutorBreach／ix.TheoryFalsified（全限定名·不可互捕·已装载时生效）
        code = EXIT_FALSIFIED if (ix is not None and isinstance(e, ix.TheoryFalsified)) else EXIT_BREACH
        print('%s code=%d type=%s msg=%s' % (FAIL_MARKER, code, type(e).__name__, str(e)[:400]), flush=True); return code
    except Exception as e:
        import traceback; traceback.print_exc()
        print('%s code=%d type=%s msg=%s' % (FAIL_MARKER, EXIT_UNEXPECTED, type(e).__name__, str(e)[:400]), flush=True); return EXIT_UNEXPECTED


if __name__ == '__main__':
    sys.exit(main())
