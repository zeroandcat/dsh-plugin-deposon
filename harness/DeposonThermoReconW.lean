/-
DeposonThermoReconW.lean — σ / W2 / W5 三项求证件（PI 18:01 A5·lean 求证位）

头注沿革: v1（daf39e5e3cab…）头注「P-σ 以定理前提承载」与件内 §W-4（以
          sigma_invariant 定理＋定义承载）自相不一——本席 Lean 双审意见件 C3 审出
          （实况＝后者：P-σ 是 SigmaLedger 第六字段记录定义·sigma_invariant 证其
          不变性·0 定理以 P-σ 为前提）；preview.12 附B 甲（PI P481 裁 2026-11-27）
          沿该件 C3 候选改文勘正头注两处措辞·定理与证明体 0 动。

令源: PI 2026-11-26 18:01 裁定执行批 A5（kimi round12 七项中三项逐项 Lean 求证出件）:
      · σ  = A 侧稳态参照 —— PI 裁「引入」（③/3b 二选一取引入·P2 降定理路径）
      · W2 = 舍入函子复合性（Alabama 悖论）—— PI 裁「承认整数账仅单事件粒度守恒并利用」
      · W5 = 尺度分离假设（§4.1 g_aether 累积 vs §4.3 readback 不改参数）—— 逐项求证
      问单原文: 查理实录件 shared/查理_kimi_round11重发与round12三问实录_20261126/
      （kimi_round11_q3_resend_answer.txt = ③ 整问单·kimi_round11_q3b_resend_answer.txt
       = 3b 补位·σ/W2/W5 原文逐字在此）。

定位: 三项的**账面像求证**（Nat 级·core-only·0 sorry·0 新增公理）。
      本体层难点（DPI/Spohn 泛函·W4 σ 存在唯一·CPTP 无逆定理 T4）**不入**账面像——
      kimi ③b ① 已明示「熵产非负必须挂参照态才成立」为本体层论证·账面像只承载其
      结构位（参照独立于事件·相对读数单调·严格增段不可逆）·如实注·不越层。

三层落位（σ 引入涉新公设/定义位·按 PI 令面三层落）:
  §W-σ 定义层   —— SigmaLedger（v2 Ledger 五字段 + sigma_ref 第六字段）
  §W-σ 公设位   —— P-σ「A 侧稳态参照存在且独立于事件」: 以**定义承载＋不变性定理**
                    （sigma_invariant·五迁移任一单步不改 sigma_ref）承载·deliberately
                    not as an axiom·**非任何定理的前提**（头注措辞勘正·preview.12 附B 甲·
                    沿本席 Lean 双审意见件 C3 候选改文·PI P481 裁 2026-11-27）·
                    不入 Lean 公理面（0 新增 axiom·公理纪律与 v2 同）
  §W-σ 定理层   —— sigma_invariant（P-σ 穷尽承载）/ diss_rel_mono 三条（DPI 账面像）/
                    strict_increase_no_return（因果方向倒转像·③b 主定理）/
                    sigma_conserved_inject（账本语义成推论像）
  §W-W2 定义层  —— mrQ1/mrQ2（两柱最大余数量子化·确定性·tie 按柱序·定点 scale=100）
  §W-W2 定理层  —— mrQ_sum（单事件粒度守恒·利用位①）/ alabama_counterexample
                    （复合粒度反例·边界钉位）/ real_composite_sum（复合守恒只在
                    实数账·粒度无关像）/ conserved_inject_dissipate（链级总量守恒·
                    利用位②——总量恒等式粒度无关·分布像粒度相对）
  §W-W5 定义层  —— EvKind（事件类型分派）/ gStepW5 / gSeq / countNonReadback
  §W-W5 假设位  —— W5 尺度分离: 以**定义固定 + 前提化**承载（非 axiom）——
                    readback 事件对 g_aether 账面零增量；若架构席给出 g_aether
                    累积方程·此定义位被替换（kimi W5 注·替换位开放）
  §W-W5 定理层  —— w5_readback_step_identity（§4.3 句像）/ w5_composite_zero_contribution
                    （§4.1×§4.3 相容等式·主定理）/ w5_feedback_branch（无 W5 分叉反例·
                    假设位非空洞的必要性实证）

与 v2 32 定理（DeposonThermoRecon.lean·sha12 45c56f1e5487·0 动）关系·逐条:
  · SigmaLedger 五字段 = Ledger 形态级复刻（e0/phi/refl/diss/us 逐位同名同型）;
    sInject/sDissipate/sTransmit/sReflect/sDeposit = 五迁移逐位同形（sigma_ref 位新增·
    迁移体逐字同形·0 触 v2）。
  · sdiss_mono 五条 = v2 diss_monotone 五条同名对读（σ 态复刻·同证法）。
  · sigma_conserved_inject = v2 conserved_inject 的 σ 态扩展（守恒恒等式不涉 sigma_ref）。
  · W2 复刻面七件（Ledger/Conserved/inject/dissipate/sum_set/conserved_inject/
    conserved_dissipate）= v2 §1/§2/§3-0/§3-1 形态级复刻·逐字同证·0 import;
    conserved_inject_dissipate = v2 两单步定理的串联样板（v2 无复合条·本件新增）。
  · σ 的 sigma_ref/diss_rel_mono 族/strict_increase_no_return 与 W2 的 mrQ 族、
    W5 全节 = **新构造**（v2 无对应位）。
  · v2 对 DeposonThermo.lean（15 件·已退役 A1）的继承关系在 v2 头注·本件不重复。
与 companion 58 定理（IrreversibleDeposon.lean·0decb3a4059f·0 动）关系:
  · 0 触三钉（d2189f2c4f1e / 3b19207a5292 已追认 A3 / 0decb3a4059f）·0 import·形态级对读。
  · strict_increase_no_return ↔ companion 无直接对应（执行器层 dissipate 为整行散失·
    D 严格增段的「无逆」由 no_recover_shape 同族承载）。
  · w5 相容定理 ↔ companion readback 边界 4 条的 g_unchanged 位**同向**——W5 的账面
    承载在执行器实现层已被 companion 落实（形态级同向·非形式导出·0 形式桥）。
  · W5 的 EvKind/gStepW5 是假设的独立最小面·**非** companion G/g 累积器复刻
    （companion g 是执行器层构件·不入账本截面·v2 §1 头注同口径）。

构建: lean 4.15.0 core-only · no mathlib · no sorry · 0 新增 axiom
      （公理面 = propext / Quot.sound 上限·§W-4 逐定理报齐）。
-/

namespace DeposonThermoReconW

-- ============================================================
-- §W-σ  A 侧稳态参照 σ（PI 裁引入·kimi round11 ③b 最小重构形的账面像）
-- ============================================================
-- kimi ③b ④ 原文要义（逐字·摘）: 设散射半群 {Λ_t} 为 CPTP 保迹，且 A 侧存在稳态
-- 参照 σ（Λ_t σ=σ）；定义 D(t) := ε⁻¹·累积熵产 S(ρ(t)‖σ)。由数据处理不等式得
-- D 单调不减，严格增的段上 Λ_t 无 CPTP 逆。于是账本的 append-only 是 D 单调的像、
-- 五转移的整数守恒是 T+R+A=1 在 ε-格点上的像——账本语义成为推论，剩余公设只有
-- 「σ 存在」一条。
-- 账面像落位（如实注·不越层）:
--   · 本体层「σ 存在唯一」是 W4 难点（L 本原 ⇒ σ 唯一且 Λ_t → σ）·账面像上 sigma_ref
--     是 Nat 常量·存在性平凡化——账面像只承载「参照独立于事件」的结构位（P-σ）。
--   · P-σ 以定义承载＋不变性定理（sigma_invariant）承载·非定理前提·**不入 Lean
--     axiom 面**（0 新增公理·v2 公理纪律同）——措辞勘正同头注（preview.12 附B 甲）。

/-- σ 扩展账本态: v2 Ledger 五字段（形态级复刻·继承锚）＋ A 侧稳态参照水位
    sigma_ref（第六字段·kimi ③b 的 σ 账面承载）。
    与 companion 关系: companion 无 σ 位（58 定理无稳态参照构件）——σ 是账本层
    新构造（kimi ③b ② 原话: σ 的稳态性与 ε 量化映射不在 R3 现有本体层里）。 -/
structure SigmaLedger where
  e0 : Nat
  phi : Nat
  refl : Nat
  diss : Nat
  us : List Nat
  sigma_ref : Nat
  deriving Repr

/-- σ 版五迁移（v2 §2 逐位同形 + sigma_ref 位对全部迁移恒不变）。
    sigma_ref 恒不变＝ P-σ「Λ_t σ = σ」的账面构造承载（公设层落位）。 -/
def sInject (s : SigmaLedger) (q : Nat) : SigmaLedger :=
  { s with e0 := s.e0 + q, us := q :: s.us }

def sDissipate (s : SigmaLedger) (i a : Nat) : SigmaLedger :=
  { s with
    diss := s.diss + (if h : i < s.us.length then a else 0),
    us := if h : i < s.us.length then s.us.set i (s.us[i] - a) else s.us }

def sTransmit (s : SigmaLedger) (c : Nat) : SigmaLedger :=
  { s with e0 := s.e0 + c, phi := s.phi + c }

def sReflect (s : SigmaLedger) (c : Nat) : SigmaLedger :=
  { s with e0 := s.e0 + c, refl := s.refl + c }

def sDeposit (s : SigmaLedger) (i : Nat) : SigmaLedger :=
  { s with
    diss := s.diss + (if h : i < s.us.length then s.us[i] else 0),
    us := if h : i < s.us.length then s.us.set i 0 else s.us }

/-- P-σ 的穷尽承载（公设位·定理形）: 五迁移穷尽的任何单步都不改 sigma_ref——
    「Λ_t σ = σ」的账面像。本体层注: σ 的存在唯一（W4）是本体层难点·账面像
    存在性平凡化（任意 Nat 常量皆可）·本定理只钉「独立性」结构位。 -/
theorem sigma_invariant (s s' : SigmaLedger)
    (h : (∃ q, s' = sInject s q) ∨ (∃ i a, s' = sDissipate s i a)
      ∨ (∃ c, s' = sTransmit s c) ∨ (∃ c, s' = sReflect s c) ∨ (∃ i, s' = sDeposit s i)) :
    s'.sigma_ref = s.sigma_ref := by
  rcases h with ⟨q, rfl⟩ | ⟨i, a, rfl⟩ | ⟨c, rfl⟩ | ⟨c, rfl⟩ | ⟨i, rfl⟩
  · rfl
  · rfl
  · rfl
  · rfl
  · rfl

/-- D 单调五条（v2 diss_monotone 五条同名对读·σ 态复刻·同证法）。
    v2 头注位（P2 账面像·升格待证）在 σ 件的重述: σ 引入后 D 单调的重述位是
    P-σ 前提下的推论像（因果方向倒转·见 strict_increase_no_return）·
    v2 文件 0 动·升格的本体层论证是论文面（查理线）非本件。 -/
theorem sdiss_mono_inject (s : SigmaLedger) (q : Nat) :
    (sInject s q).diss ≥ s.diss := Nat.le_refl _

theorem sdiss_mono_dissipate (s : SigmaLedger) (i a : Nat) :
    (sDissipate s i a).diss ≥ s.diss := by
  unfold sDissipate
  split <;> simp_all

theorem sdiss_mono_transmit (s : SigmaLedger) (c : Nat) :
    (sTransmit s c).diss ≥ s.diss := Nat.le_refl _

theorem sdiss_mono_reflect (s : SigmaLedger) (c : Nat) :
    (sReflect s c).diss ≥ s.diss := Nat.le_refl _

theorem sdiss_mono_deposit (s : SigmaLedger) (i : Nat) :
    (sDeposit s i).diss ≥ s.diss := by
  unfold sDeposit
  split <;> simp_all

/-- DPI 账面像·耗散向: σ_ref 固定·D 柱相对稳态参照的读数不减。
    本体层对应: kimi T3（D(t) = ∫₀ᵗ σ_EP ds 不减·Spohn·条件 σ 是不动点）——
    账面像只承载「相对读数单调」·0 主张熵产泛函本身（不越层注）。
    前提 diss ≥ sigma_ref 防 Nat 截断减法的伪等值。 -/
theorem diss_rel_mono_dissipate (s : SigmaLedger) (i a : Nat)
    (hge : s.sigma_ref ≤ s.diss) :
    s.sigma_ref ≤ (sDissipate s i a).diss
    ∧ s.diss - s.sigma_ref ≤ (sDissipate s i a).diss - s.sigma_ref := by
  unfold sDissipate
  split
  · show s.sigma_ref ≤ s.diss + a
      ∧ s.diss - s.sigma_ref ≤ s.diss + a - s.sigma_ref
    constructor <;> omega
  · show s.sigma_ref ≤ s.diss + 0
      ∧ s.diss - s.sigma_ref ≤ s.diss + 0 - s.sigma_ref
    constructor <;> omega

/-- DPI 账面像·凝华向（同形）: deposit 事件下相对读数不减。 -/
theorem diss_rel_mono_deposit (s : SigmaLedger) (i : Nat)
    (hge : s.sigma_ref ≤ s.diss) :
    s.sigma_ref ≤ (sDeposit s i).diss
    ∧ s.diss - s.sigma_ref ≤ (sDeposit s i).diss - s.sigma_ref := by
  unfold sDeposit
  split
  · show s.sigma_ref ≤ s.diss + s.us[i]
      ∧ s.diss - s.sigma_ref ≤ s.diss + s.us[i] - s.sigma_ref
    constructor <;> omega
  · show s.sigma_ref ≤ s.diss + 0
      ∧ s.diss - s.sigma_ref ≤ s.diss + 0 - s.sigma_ref
    constructor <;> omega

/-- DPI 账面像·读回向: reflect 事件不动 D 柱——相对读数恒等（等号情形·
    「不减」含等）。读回付账走 R 不走 D（v2 readback_no_d_refund 的 σ 态对读）。 -/
theorem diss_rel_mono_reflect (s : SigmaLedger) (c : Nat) :
    (sReflect s c).diss = s.diss
    ∧ s.diss - s.sigma_ref = (sReflect s c).diss - s.sigma_ref := ⟨rfl, rfl⟩

/-- **主定理·因果方向倒转的账面像**（kimi ③b「熵产严格为正的段上 Λ_t 无 CPTP 逆」）:
    一次耗散事件使 D 严格增（熵产严格为正的账面像）后·任何单步（五迁移穷尽）
    都无法使 D 回到事件前的值。**方向**: 不可逆性（无逆）从「严格增 + 签名单调」
    推出·而非作为前提——③b ①「无 CPTP 逆是果」的账面形。
    本体层注: 本定理只对 D 柱读数成立·非态空间映射的不可逆性本身
    （CPTP 无逆的本体层定理是 kimi T4·不形式化于此·如实注）。 -/
theorem strict_increase_no_return (s : SigmaLedger) (i a : Nat)
    (hgt : (sDissipate s i a).diss > s.diss)
    (s'' : SigmaLedger)
    (h5 : (∃ q, s'' = sInject (sDissipate s i a) q)
      ∨ (∃ j b, s'' = sDissipate (sDissipate s i a) j b)
      ∨ (∃ c, s'' = sTransmit (sDissipate s i a) c)
      ∨ (∃ c, s'' = sReflect (sDissipate s i a) c)
      ∨ (∃ j, s'' = sDeposit (sDissipate s i a) j)) :
    s''.diss ≠ s.diss := by
  rcases h5 with ⟨q, rfl⟩ | ⟨j, b, rfl⟩ | ⟨c, rfl⟩ | ⟨c, rfl⟩ | ⟨j, rfl⟩
  · have h1 := sdiss_mono_inject (sDissipate s i a) q
    omega
  · have h1 := sdiss_mono_dissipate (sDissipate s i a) j b
    omega
  · have h1 := sdiss_mono_transmit (sDissipate s i a) c
    omega
  · have h1 := sdiss_mono_reflect (sDissipate s i a) c
    omega
  · have h1 := sdiss_mono_deposit (sDissipate s i a) j
    omega

/-- 账本语义成推论像（kimi ③b ④「账本语义成为推论」的账面形）:
    守恒谓词在 σ 扩展态下保持（注入向代表·五迁移同形可对读 v2 §3-1）。
    σ 的角色注: 守恒恒等式本身不涉 sigma_ref——σ 引入改变的是**方向族的依据位**
    （D 单调从独立公设像变为 P-σ 前提下的推论像）·非守恒族（见 v2 §3-1 与本件
    strict_increase_no_return 头注）。 -/
theorem sigma_conserved_inject (s : SigmaLedger) (q : Nat)
    (h : s.e0 = s.phi + s.refl + s.diss + s.us.sum) :
    (sInject s q).e0 = (sInject s q).phi + (sInject s q).refl
      + (sInject s q).diss + (sInject s q).us.sum := by
  show s.e0 + q = s.phi + s.refl + s.diss + (q + s.us.sum)
  omega

-- ============================================================
-- §W-W2  舍入函子复合性（Alabama 悖论·PI 裁「承认整数账仅单事件粒度守恒并利用」）
-- ============================================================
-- kimi ③ W2 原文要义（逐字·摘）: 最大余数法在复合下不满足结合律（Alabama 悖论），
-- 所以「逐事件整数守恒」＋「复合后仍守恒」不是自动的。要么换可结合方案
-- （固定分母 floor ＋ 显式 carry 结转），要么承认整数账只在单事件粒度守恒、
-- 复合层面只在实数账上守恒。这条不证，「integral form」是空的。
-- PI 2026-11-26 18:01 裁定: 承认整数账仅单事件粒度守恒并利用（二选一取后者）。
-- 求证落位（三层）:
--   定义层: mrQ1/mrQ2（最大余数量子化·确定性·tie 按柱序·定点 scale=100）。
--   定理层: mrQ_sum（单事件粒度守恒 = 利用位①·把 v2 §3-1 守恒族的粒度限定
--           实证化为可检命题）/ alabama_counterexample（复合粒度分布反例 =
--           边界钉位·三柱分布的整数账是事件粒度相对的）/ real_composite_sum
--           （复合层面守恒只在实数（定点）账·粒度无关像）/ conserved_inject_dissipate
--           （链级总量守恒 = 利用位②·总量恒等式沿迁移链复合保持——与分布像的
--           粒度相对性**分开**·两级主张各归各位）。
--   公设位: 无新增——W2 裁定是账面纪律（守恒主张的范围限定）·非新公设。

/-- 最大余数量子化·柱 1（确定性·tie 按柱序·定点 scale=100）。
    输入: 定点分配 x1 x2（x1 + x2 = 100·N·N 为事件总量量子数）。
    floor 后差额（0 或 1）按余数大小补·余数相同 tie 取柱 1（柱序确定性）。 -/
def mrQ1 (x1 x2 : Nat) : Nat :=
  if (x1 + x2) / 100 - (x1 / 100 + x2 / 100) = 0 then x1 / 100
  else if x1 % 100 ≥ x2 % 100 then x1 / 100 + 1 else x1 / 100

/-- 最大余数量子化·柱 2（与 mrQ1 共用同一 condition 结构·互补位）。 -/
def mrQ2 (x1 x2 : Nat) : Nat :=
  if (x1 + x2) / 100 - (x1 / 100 + x2 / 100) = 0 then x2 / 100
  else if x1 % 100 ≥ x2 % 100 then x2 / 100 else x2 / 100 + 1

/-- **单事件粒度守恒**（利用位①）: 量子化输出和 = 事件总量 N——
    v2 §3-1 守恒族与 companion 守恒族「每笔迁移后 E⁰ = Φ+R+D+U」的粒度限定·
    在量子化面实证化为可检命题: 守恒主张**只**在单事件粒度成立。 -/
theorem mrQ_sum (N x1 x2 : Nat) (h : x1 + x2 = 100 * N) :
    mrQ1 x1 x2 + mrQ2 x1 x2 = N := by
  unfold mrQ1 mrQ2
  split <;> (try split) <;> omega

/-- **Alabama 复合反例**（边界钉位）: 两笔事件各为定点 (160, 40)（总量 2ε·
    量子化 (2, 0)·单事件守恒 ✓）·逐事件整数账和 = (4, 0); 合并为一笔粗粒化
    事件 (320, 80)（总量 4ε·量子化 (3, 1)·复合总额守恒 ✓）——两账各守恒·
    **分布不一致**: (4, 0) ≠ (3, 1)。整数分布像是事件粒度相对的——
    「复合后仍守恒（同一整数分布）」不是自动的·Alabama 悖论实例化落地。
    （kimi W2 原文「这条不证，integral form 是空的」——本定理即该条的形式载体。） -/
theorem alabama_counterexample :
    mrQ1 160 40 = 2 ∧ mrQ2 160 40 = 0
    ∧ mrQ1 320 80 = 3 ∧ mrQ2 320 80 = 1
    ∧ (mrQ1 160 40 + mrQ1 160 40 ≠ mrQ1 320 80
       ∨ mrQ2 160 40 + mrQ2 160 40 ≠ mrQ2 320 80) := by
  decide

/-- **复合层面的守恒只在实数账**（粒度无关像）: 两事件的定点分配之和 =
    合并事件的定点分配——加法结合·与粒度无关。
    对比 alabama_counterexample: **总量像**粒度无关（本定理）·
    **分布像**粒度相对（反例）——W2 裁定「承认整数账仅单事件粒度守恒、
    复合层面只在实数账上守恒」两级主张的形式载体。 -/
theorem real_composite_sum (a1 b1 a2 b2 : Nat) :
    (a1 + b1) + (a2 + b2) = (a1 + a2) + (b1 + b2) := by omega

-- ---- W2 复刻面（v2 §1/§2/§3-0/§3-1 形态级复刻·逐字同证·0 import·继承锚） ----

/-- 账本状态（v2 Ledger 形态级复刻·继承锚·字段逐位同名同型）。 -/
structure WLedger where
  e0 : Nat
  phi : Nat
  refl : Nat
  diss : Nat
  us : List Nat
  deriving Repr

/-- 守恒谓词（v2 Conserved 形态级复刻）。 -/
def WConserved (s : WLedger) : Prop := s.e0 = s.phi + s.refl + s.diss + s.us.sum

def winject (s : WLedger) (q : Nat) : WLedger :=
  { s with e0 := s.e0 + q, us := q :: s.us }

def wdissipate (s : WLedger) (i a : Nat) : WLedger :=
  { s with
    diss := s.diss + (if h : i < s.us.length then a else 0),
    us := if h : i < s.us.length then s.us.set i (s.us[i] - a) else s.us }

/-- 池单项改写守和（v2 sum_set 逐字同证·继承锚）。 -/
theorem wsum_set (l : List Nat) (i a : Nat) (h : i < l.length) :
    (l.set i a).sum + l[i] = l.sum + a := by
  induction l generalizing i with
  | nil => simp at h
  | cons x xs ih =>
    cases i with
    | zero => simp only [List.set_cons_zero, List.sum_cons, List.getElem_cons_zero]; omega
    | succ i =>
      have h' : i < xs.length := Nat.lt_of_succ_lt_succ h
      have hs := ih i h'
      simp only [List.set_cons_succ, List.sum_cons, List.getElem_cons_succ]
      omega

/-- 注入守恒（v2 conserved_inject 逐字同证·继承锚）。 -/
theorem wconserved_inject {s : WLedger} (h : WConserved s) (q : Nat) :
    WConserved (winject s q) := by
  unfold WConserved at h ⊢
  simp only [winject, List.sum_cons]
  omega

/-- 耗散守恒（v2 conserved_dissipate 逐字同证·继承锚）。 -/
theorem wconserved_dissipate {s : WLedger} (h : WConserved s) {i a : Nat}
    (hl : i < s.us.length) (ha : a ≤ s.us[i]) :
    WConserved (wdissipate s i a) := by
  unfold WConserved at h ⊢
  have hs := wsum_set s.us i (s.us[i] - a) hl
  simp only [wdissipate, dif_pos hl]
  omega

/-- **链级总量守恒**（利用位②·v2 无复合条·本件新增样板）:
    注入 → 耗散两步复合后守恒谓词保持——**总量恒等式沿迁移链复合保持**
    （任意长链由归纳·本件给两步样板）。与 alabama_counterexample 对照:
    总量恒等式（WConserved）粒度无关·三柱分布像粒度相对——两级主张分开·
    W2 裁定「承认并利用」的账面纪律闭环: 账本按**事件粒度**读守恒
    （每笔 E⁰ = Φ+R+D+U）·复合对账用**总量核**（e0 侧 append 型累计·本定理）·
    不对三柱分布做复合整数主张。 -/
theorem wconserved_inject_dissipate (s : WLedger) (h : WConserved s) (q i a : Nat)
    (hl : i < (winject s q).us.length) (ha : a ≤ (winject s q).us[i]) :
    WConserved (wdissipate (winject s q) i a) :=
  wconserved_dissipate (wconserved_inject h q) hl ha

-- ============================================================
-- §W-W5  尺度分离假设（§4.1 g_aether 累积 vs §4.3 readback 不改参数·PI 逐项求证）
-- ============================================================
-- kimi ③ 纠正二原文要义（逐字·摘）: §4.1「the accumulated g_aether bias」——
-- g_aether 会累积；§4.3「it does not change (g_couple, g_aether) or any postulate」
-- ——readback 不改 g_aether。两句不能同真。若 (g_couple, g_aether) 是慢变量、
-- readback 只在快时间尺度作用，则 §4.3 对、§4.1 的 "accumulated" 要限定为
-- 「由非 readback 事件累积」；若 g_aether 确实随 readback 累积，§4.3 那句要删，
-- readback 就不再是「不改参数的新散射事件」，而是「带反馈的散射事件」——
-- 另一个模型。我倾向前者（尺度分离），但那是假设，见待证 W5。
-- 求证落位（三层）:
--   定义层: EvKind（事件类型分派·readback = reflect 位）/ gStepW5 / gSeq /
--           countNonReadback——W5 假设的独立最小面（**非** companion G/g 复刻·
--           companion g 是执行器层构件不入账本截面·v2 §1 头注同口径）。
--   假设位: W5 以**定义固定 + 前提化**承载（readback 零增量入 gStepW5 定义）·
--           非 axiom·0 新增公理；若架构席给出 g_aether 累积方程·此定义位被替换
--           （kimi W5 原注·替换位开放）。
--   定理层: w5_readback_step_identity（§4.3 句账面像）/ w5_composite_zero_contribution
--           （**相容主定理**·§4.1×§4.3 两句同真的账面等式）/ w5_feedback_branch
--           （无 W5 分叉反例·「另一模型」自洽可构造——假设位非空洞的必要性实证）。

inductive EvKind where
  | evInj | evDis | evTra | evRefl | evDep

/-- 事件类型分派: readback 位 = evRefl（reflect 迁移·读回反射·v2 §2 ④ 对应）。 -/
def isReadback : EvKind → Bool
  | EvKind.evRefl => true
  | _ => false

/-- W5 演化（尺度分离假设的账面承载·定义固定）: readback（evRefl）对 g_aether
    账面**零增量**（§4.3 句像）·非 readback 事件各增 1（§4.1 "accumulated" 的
    限定像——由非 readback 事件累积）。
    companion 对读: 该承载在执行器实现层已被 companion readback 边界 4 条的
    g_unchanged 位落实（形态级同向·非形式导出）。 -/
def gStepW5 (g : Nat) (k : EvKind) : Nat :=
  if isReadback k = true then g else g + 1

/-- W5 演化下的事件序列 g 终值（fold 的显式递归形）。 -/
def gSeq (g : Nat) : List EvKind → Nat
  | [] => g
  | k :: ks => gSeq (gStepW5 g k) ks

/-- 非 readback 事件计数（§4.1 限定句的累积量像）。 -/
def countNonReadback : List EvKind → Nat
  | [] => 0
  | k :: ks => (if isReadback k = true then 0 else 1) + countNonReadback ks

/-- 单步恒等（§4.3 句像）＋非 readback 累积（§4.1 限定像）的合取落位。 -/
theorem gStepW5_add (g : Nat) (k : EvKind) :
    gStepW5 g k = g + (if isReadback k = true then 0 else 1) := by
  unfold gStepW5
  split <;> omega

theorem countNonReadback_cons (k : EvKind) (ks : List EvKind) :
    countNonReadback (k :: ks) = (if isReadback k = true then 0 else 1)
      + countNonReadback ks := rfl

/-- **相容主定理**（§4.1 × §4.3 两句同真的账面等式）:
    W5 演化下·任意事件序列的 g 终值 = 初值 + 非 readback 累积量——
    readback 子列对 g_aether 累积**零贡献**（Σ readback 增量 = 0）。
    于是 §4.1「accumulated g_aether bias」限定为「由非 readback 事件累积」·
    §4.3「readback 不改 (g_couple, g_aether)」保持——两句是**同一等式的两面**·
    账面像相容（kimi 纠正二的尺度分离支落地）。 -/
theorem w5_composite_zero_contribution : ∀ (ks : List EvKind) (g : Nat),
    gSeq g ks = g + countNonReadback ks := by
  intro ks g
  induction ks generalizing g with
  | nil => simp [gSeq, countNonReadback]
  | cons k ks ih =>
    rw [gSeq, countNonReadback_cons, gStepW5_add,
        ih (g + (if isReadback k = true then 0 else 1))]
    omega

/-- §4.3 句像＋§4.1 限定像的单步合取（读回零增量·耗散累积·写入口累积）。 -/
theorem w5_readback_step_identity (g : Nat) :
    gStepW5 g EvKind.evRefl = g
    ∧ gStepW5 g EvKind.evDis = g + 1
    ∧ gStepW5 g EvKind.evInj = g + 1 := by
  simp [gStepW5, isReadback]

/-- **无 W5 的分叉反例**（假设位非空洞的必要性实证）: 反馈散射模型——readback
    事件也累积（增量 1）——与 W5 演化在 readback 单步上**不同**（g 变 vs g 不变）。
    两个模型皆自洽可构造 ⇒「readback 是否改参数」是需要显式假设的**真二选一**
    （kimi 纠正二原话: 若 g_aether 确实随 readback 累积·§4.3 那句要删·
    readback 成「带反馈的散射事件」——另一个模型）。W5 假设位的选取由此反例
    钉住为实质假设·非空洞占位。 -/
def gStepFeedback (g : Nat) (_k : EvKind) : Nat := g + 1

theorem w5_feedback_branch (g : Nat) :
    gStepFeedback g EvKind.evRefl ≠ gStepW5 g EvKind.evRefl := by
  show g + 1 ≠ g
  omega

-- ============================================================
-- §W-4  公理面审计（报齐）
-- ============================================================
-- 0 新增公理。逐定理 #print axioms: 可接受集 = Lean 自带 propext / Quot.sound
-- （无 sorryAx·无 Classical.choice）; rfl 级定理无公理依赖。
-- P-σ（σ 公设位）与 W5（尺度分离假设位）**均未落 axiom**——
-- 前者以 sigma_invariant 定理 + 定义承载·后者以 gStepW5 定义固定 + 前提化承载·
-- 与 v2 公理纪律同（公理面只承载记账语义·本体公设不入公理面）。

#print axioms sigma_invariant
#print axioms sdiss_mono_inject
#print axioms sdiss_mono_dissipate
#print axioms sdiss_mono_transmit
#print axioms sdiss_mono_reflect
#print axioms sdiss_mono_deposit
#print axioms diss_rel_mono_dissipate
#print axioms diss_rel_mono_deposit
#print axioms diss_rel_mono_reflect
#print axioms strict_increase_no_return
#print axioms sigma_conserved_inject
#print axioms mrQ_sum
#print axioms alabama_counterexample
#print axioms real_composite_sum
#print axioms wsum_set
#print axioms wconserved_inject
#print axioms wconserved_dissipate
#print axioms wconserved_inject_dissipate
#print axioms gStepW5_add
#print axioms countNonReadback_cons
#print axioms w5_composite_zero_contribution
#print axioms w5_readback_step_identity
#print axioms w5_feedback_branch

end DeposonThermoReconW
