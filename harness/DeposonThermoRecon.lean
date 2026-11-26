/-
DeposonThermoRecon.lean — 热力学重构件（定义／公设／定理三层·案头件①）

令源: 群管理员 2026-11-26 09:03:59／09:28:31 令①（热力学重构·欠交重试·令不变）
      PI 2026-11-26 08:10（真双绑＝双象全绑定）·09:33（穷尽完备前置·继续重构插件及插件仓）

定位: R3 v5preR3 §2.8「Thermodynamic reconstruction: absorption slot」的账本层承接件。
      本件只承载**热力学账本层**（总量账＋三终账＋在场池·五迁移＋守恒/方向/付账/结算定理）；
      **执行器层**（budget policy `phantom_budget`／readback 预算与幻肢门槛／墓碑链
      `chain_ok`／可读表 `ReadKin/ReadKout`／DEK 与密文面／g_aether 累积器）全部留在
      companion `IrreversibleDeposon.lean`（58 定理·三钉冻结
      d2189f2c4f1e / 62cb86c40a80 / 0decb3a4059f）——本件 0 触三钉·不构成重钉。

三层结构:
  §1 定义层 —— Ledger / U / Conserved / ExeFace / proj（全部为记账语义）
  §2 公设层 —— 迁移签名（构造性公设: 签名即入账规则·无 recover 迁移）
                ＋份额律 T+R+A=1 的账面承载声明
                ＋本体公设 P2 的账外声明（不入 Lean 公理面·见 §2 头注）
  §3 定理层 —— 3-0 池算术辅助
                3-1 守恒族（E⁰ = Φ + R + D + U·守恒谓词五迁移保持）
                3-2 方向族（D 单调＝P2 投影候选·恒真重述·kimi round11 ②）＋池单调族（U 侧·非 P2 像）
                3-3 读回付账族（阿兰 §4.4 限定句的账面形·Bennett 1982 / Sagawa–Ueda）
                3-4 结算族（凝华·Deposon 本义·终端归零像）
                3-5 桥接族（继承的形态级锚·单步对读·非形式导出）

约束输入（如实接住·不翻案·裁决权留 PI）:
  · kimi round11（查理实录件 2026-11-26·帐本语义五问）:
      ③ 账本＝工具表述层审计器 —— 本件全部内容是记账语义·不是物理定律（§1 头注）；
        账本层结论只作否证实现层主张与一致性检查·**不作正面物理主张**（round11 ③ 后半）。
      ② D 单调＝P2 账面像·升格待证 —— §3-2 每条定理头注标注「账面像·不充当 P2 的面」。
      3a U 最弱·禁写独立物理态 —— U 不设独立字段·恒为在场池账面和（审计余数位·§1）。
  · 阿兰 §4.4 勘正句（R3 稿面引文与对话集源引用对表件·08:17 包）:
      「熵产生非零」只可主张「本理论读回事件含 A 份额所致」·非读出动作普遍律
      （Bennett 1982 读出可逆·Sagawa–Ueda 2008/2009 测量成本有界）——§3-3 按此限定。

与现行件的继承／取代／增补关系（速查·逐条详注见案头 md）:
  · 对 harness/DeposonThermo.lean（15 定理·v5preR2 在册）: **继承＋头注升级**（非证明强度提升·与 P2 升格待证无关）。
    State→Ledger 改名·签名/证法逐字一致化; T0–T9 全部继承; 增补 = 读回付账族
    ＋结算终端族＋pool_monotone_deposit＋五迁移版 no_recover_shape（原件无）。
  · 对 IrreversibleDeposon.lean（58 定理·执行器伴件 v3.1.1）: **划界＋投影继承·0 取代**。
    执行器层定理全部留在 companion; 本件 §3-5 给投影 proj 与单步对读条目（交换仅单步·
    仅逐字段等值＋U 等值·池序约定不同⇒复合序列不交换·反例见 proj_inject 头注）——
    companion 账本层守恒/单调定理与本件形态级同形可对读·**非形式导出**（0 import·无形式桥）;
    companion 三钉 sha 不动。

构建: lean 4.15.0 core-only·no mathlib·no `sorry`。
      公理面 = Lean 自带 propext / Quot.sound（§4 逐定理报齐·无新增公理·
      decide 数据定理 4 条＋rfl/构造项等值 9 条＝13 条无公理依赖）。
-/

namespace DeposonThermoRecon

-- ============================================================
-- §1 定义层 —— 记账语义（kimi round11 ③: 账本＝工具表述层审计器·非物理态）
-- ============================================================

/- 记账单位＝㶲量子（integer quanta over ℕ·类型面用 Nat 与原件逐字一致）。
    份额律 T+R+A=1 的整数记账像: **每量子单通道全份额入账**（份额律在记账分辨率下的退化像）·
    账本只记整数份额
    （R3 §2.7 口径: 公理层是实数份额律·账本是其记账分辨率下的整数像——
    总量＋三终账＝记账分辨率·阿兰三通道勘正件同口径）。 -/
/-- 热力学账本状态: 注入询㶲总量 + 三终账 + 在场池。
    类型级边界（与执行器层划界）: 本结构**无** key／DEK／密文／墓碑链／累积器字段——
    那些是执行器层（companion Cipher / Row / TBody / G / V3State）的构件。
    与 harness/DeposonThermo.lean State（L37-43）逐字段同形（继承锚·State→Ledger）。 -/
structure Ledger where
  e0 : Nat    -- E⁰: 注入询㶲总量（行 + 查询）·结算核
  phi : Nat   -- Φ 账: T 通道（透射）账面像
  refl : Nat  -- R 账: R 通道（反射·付账读回）账面像
  diss : Nat  -- D 账: A 通道（耗散）账面像·只进不出
  us : List Nat -- 在场池: 每行余量子（池序; 已凝华行以 0 项承载）
  deriving Repr

/-- U 账＝在场池的账面和（审计余数位·kimi round11 3a 落位: U **不设独立字段**·
    恒为账面余数·禁写独立物理态——其语义依赖离散化与层边界）。
    定义与 harness/DeposonThermo.lean 的池和口径一致（List.sum）。 -/
def U (s : Ledger) : Nat := s.us.sum

/-- 守恒谓词（第一定律的账面定义·由定义给定·非证明）: E⁰ = Φ + R + D + U·整数逐位。
    与 harness/DeposonThermo.lean L46 逐字同形（继承锚·签名一致化）。 -/
def Conserved (s : Ledger) : Prop := s.e0 = s.phi + s.refl + s.diss + s.us.sum

-- ============================================================
-- §2 公设层 —— 迁移签名（构造性公设）＋份额律账面承载＋P2 账外声明
-- ============================================================
-- (a) 迁移签名即公设: 下列五个迁移**穷尽**账本层的一切合法状态变更（构造性公设）。
--     **穷尽性＝建模约定·非定理**（无 inductive Reach 形式载体·round12 C11）。
--     签名中**无 recover 迁移**——散失份额没有任何退款路径（P2 账面像·构造性）。
-- (b) 份额律 T+R+A=1 的账面承载: 每笔查询㶲的分配由签名规则承载——
--     transmit 收 T 份额入 Φ·reflect 收 R 份额入 R·dissipate/deposit 收 A 份额入 D。
--     账本不记实数份额（记账分辨率·§1 Nat 头注）。
-- (c) 本体公设 P2（散失不回流·R3 §1）**不引入为 Lean 公理**: 它是本体层断言·
--     类型论公理面只承载记账语义（公理面报齐见 §4）。P2 的账面层**投影候选**（非等价·不充当面·round12 C12） =
--     §3-2 方向族（D 单调）∪ §3-3 readback_no_d_refund ∪ (a) 无 recover 签名。
--     kimi round11 ②: 该账面像「不能充当 P2 的面」·P2 升格为定理待证——本件
--     只证账面像·0 代裁升格。
-- 五迁移与 harness/DeposonThermo.lean L49-71 逐字同形（继承锚）。

/-- 迁移 ①inject 写入: 行携 q 量子入池（池前置·E⁰ 增 q）。
    companion inject（池后置 ++ [r]）的形状差由 §3-5 桥接在池和等值意义下承接。 -/
def inject (s : Ledger) (q : Nat) : Ledger :=
  { s with e0 := s.e0 + q, us := q :: s.us }

/-- 迁移 ②dissipate 门拒／衰减: 行 i 支付 a 量子入 D。
    越界索引: 无事件（Python 核 fail-loud 拒绝·与原件同口径）。 -/
def dissipate (s : Ledger) (i a : Nat) : Ledger :=
  { s with
    diss := s.diss + (if h : i < s.us.length then a else 0),
    us := if h : i < s.us.length then s.us.set i (s.us[i] - a) else s.us }

/-- 迁移 ③transmit 透射: 查询㶲 c 流入 Φ（T 份额·暗物质象读入位）。 -/
def transmit (s : Ledger) (c : Nat) : Ledger :=
  { s with e0 := s.e0 + c, phi := s.phi + c }

/-- 迁移 ④reflect 读回反射: 查询㶲 c 流入 R（R 份额·光空穴象回射位·付账读回）。
    执行器层的幻肢门槛（tombstone 在场才可达·companion L208）在**执行器层**·
    不在本签名内——账本层只承载份额去向（边界注）。 -/
def reflect (s : Ledger) (c : Nat) : Ledger :=
  { s with e0 := s.e0 + c, refl := s.refl + c }

/-- 迁移 ⑤deposit 凝华结算: 行 i 的全部余量一次送入 D（凝华位·行位记 0）。
    companion dissipate（整行散失）在账本层的像即本迁移（§3-5 proj_dissipate）。 -/
def deposit (s : Ledger) (i : Nat) : Ledger :=
  { s with
    diss := s.diss + (if h : i < s.us.length then s.us[i] else 0),
    us := if h : i < s.us.length then s.us.set i 0 else s.us }

-- ============================================================
-- §3 定理层
-- ============================================================

-- ---- §3-0 池算术辅助引理 ----------------------------------------------------

/-- 池单项改写守和（继承 DeposonThermo T0 sum_set·逐字同证）:
    改第 i 项为 a 后: 新池和 + 旧值 = 旧池和 + a。 -/
theorem sum_set (l : List Nat) (i a : Nat) (h : i < l.length) :
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

/-- 池后置单项的和像（桥接辅助·58 件 U_inject 同路）:
    (us ++ [Q]).sum = us.sum + Q。 -/
theorem us_append_one_sum (us : List Nat) (Q : Nat) :
    (us ++ [Q]).sum = us.sum + Q := by
  induction us with
  | nil => simp
  | cons x xs ih => simp only [List.cons_append, List.sum_cons, ih]; omega

/-- 全零池守和（终端凝华辅助·新）: 池中全为 0 项则池和为 0。 -/
theorem sum_all_zero : ∀ (l : List Nat), (∀ u ∈ l, u = 0) → l.sum = 0 := by
  intro l
  induction l with
  | nil => intro _; simp
  | cons x xs ih =>
    intro h
    have hx : x = 0 := h x (by simp)
    have hxs := ih (fun u hu => h u (by simp [hu]))
    simp only [List.sum_cons]
    omega

/-- 删除已凝华（0 项）守池和（继承 DeposonThermo T9 sum_drop_zero）。
    Python 核把已 deposit 行以 0 项承载·删除不改变池和（账面像）。 -/
theorem sum_drop_zero : ∀ (l₁ l₂ : List Nat), (l₁ ++ 0 :: l₂).sum = (l₁ ++ l₂).sum := by
  intro l₁
  induction l₁ with
  | nil => intro l₂; simp only [List.nil_append, List.sum_cons, List.sum_nil, Nat.zero_add]
  | cons x xs ih =>
    intro l₂
    simp only [List.cons_append, List.sum_cons, ih l₂]

-- ---- §3-1 守恒族（E⁰ = Φ + R + D + U·五迁移逐一保持） ---------------
-- 继承 DeposonThermo T1–T5·签名一致化·逐条同形重证（证法逐字）。

theorem conserved_inject {s : Ledger} (h : Conserved s) (q : Nat) :
    Conserved (inject s q) := by
  unfold Conserved at h ⊢
  simp only [inject, List.sum_cons]
  omega

theorem conserved_dissipate {s : Ledger} (h : Conserved s) {i a : Nat}
    (hl : i < s.us.length) (ha : a ≤ s.us[i]) :
    Conserved (dissipate s i a) := by
  unfold Conserved at h ⊢
  have hs := sum_set s.us i (s.us[i] - a) hl
  simp only [dissipate, dif_pos hl]
  omega

theorem conserved_transmit {s : Ledger} (h : Conserved s) (c : Nat) :
    Conserved (transmit s c) := by
  unfold Conserved at h ⊢
  simp only [transmit]; omega

theorem conserved_reflect {s : Ledger} (h : Conserved s) (c : Nat) :
    Conserved (reflect s c) := by
  unfold Conserved at h ⊢
  simp only [reflect]; omega

theorem conserved_deposit {s : Ledger} (h : Conserved s) {i : Nat}
    (hl : i < s.us.length) :
    Conserved (deposit s i) := by
  unfold Conserved at h ⊢
  have hs := sum_set s.us i 0 hl
  simp only [deposit, dif_pos hl]
  omega

-- ---- §3-2 方向族（D 单调＝P2 投影候选·恒真重述·kimi round11 ②） ---------------
-- 每条定理的账面像身份: 「D 不减」是**记账语义**层面的方向锚·由迁移签名构造性给出；
-- 它是 P2（散失不回流·本体层）的账面层投影候选·**不充当 P2 的面**·P2 升格为定理待证
-- （kimi round11 ②·不翻案）。继承 DeposonThermo T6（五迁移逐一）。
-- 本族前五条内容＝签名不改 D 的直接重述（恒真·构造保证即恒真）·**不承载 P2 的证明义务**
-- （round12 C·如实注）；pool_monotone 两族为 U 侧池单调·**非 P2 像**。

theorem diss_monotone_inject (s : Ledger) (q : Nat) :
    (inject s q).diss ≥ s.diss := Nat.le_refl _

theorem diss_monotone_dissipate (s : Ledger) (i a : Nat) :
    (dissipate s i a).diss ≥ s.diss := by
  unfold dissipate
  split <;> simp_all

theorem diss_monotone_transmit (s : Ledger) (c : Nat) :
    (transmit s c).diss ≥ s.diss := Nat.le_refl _

theorem diss_monotone_reflect (s : Ledger) (c : Nat) :
    (reflect s c).diss ≥ s.diss := Nat.le_refl _

theorem diss_monotone_deposit (s : Ledger) (i : Nat) :
    (deposit s i).diss ≥ s.diss := by
  unfold deposit
  split <;> simp_all

/-- 无恢复形态（继承 companion no_recover_shape L704·增补至五迁移全覆盖）:
    账本层五迁移穷尽的任何单步都使 D 不减——「签名无 recover 迁移」的构造性读法。
    P2 账面层投影候选·升格待证（kimi round11 ②·不充当 P2 的面）。 -/
theorem no_recover_shape (s s' : Ledger)
    (h : (∃ q, s' = inject s q) ∨ (∃ i a, s' = dissipate s i a)
      ∨ (∃ c, s' = transmit s c) ∨ (∃ c, s' = reflect s c) ∨ (∃ i, s' = deposit s i)) :
    s'.diss ≥ s.diss := by
  rcases h with ⟨q, rfl⟩ | ⟨i, a, rfl⟩ | ⟨c, rfl⟩ | ⟨c, rfl⟩ | ⟨i, rfl⟩
  · exact diss_monotone_inject s q
  · exact diss_monotone_dissipate s i a
  · exact diss_monotone_transmit s c
  · exact diss_monotone_reflect s c
  · exact diss_monotone_deposit s i

/-- 在场池单调（门拒／衰减不增池·继承 DeposonThermo T7 pool_monotone）。
    **U 侧池单调·非 P2 账面像**（round12 分族注）。 -/
theorem pool_monotone {s : Ledger} {i a : Nat} (hl : i < s.us.length)
    (ha : a ≤ s.us[i]) :
    (dissipate s i a).us.sum ≤ s.us.sum := by
  have hs := sum_set s.us i (s.us[i] - a) hl
  simp only [dissipate, dif_pos hl]
  omega

/-- 凝华不增池（增补·DeposonThermo 无·**U 侧池单调·非 P2 账面像**）: deposit 只减不增在场池。
    companion 无对应（其 dissipate 是整行删除·池单调由 remove_id 承载）——
    账本层以 0 项承载已凝华行·池和非增。 -/
theorem pool_monotone_deposit {s : Ledger} {i : Nat} (hl : i < s.us.length) :
    (deposit s i).us.sum ≤ s.us.sum := by
  have hs := sum_set s.us i 0 hl
  simp only [deposit, dif_pos hl]
  omega

-- ---- §3-3 读回付账族（阿兰 §4.4 限定句的账面形·增补·DeposonThermo 无） ------
-- 限定约束（阿兰 R3 稿面引文对表件·接令如实接住）: 「熵产生非零」只可主张
-- 「本理论读回事件含 A 份额所致」——Bennett 1982: 读出可逆·擦除才有 Landauer 成本;
-- Sagawa–Ueda 2008/2009: 测量本身的最小成本有界。故本族定理只陈述**本理论**的
-- 读回事件账面（查询㶲付账入 R·A 份额分文不退·D 存量正性保持）·
-- 不声称任何读出动作熵产生非零（非普遍律）。

/-- 读回付账位: 一次付账读回把查询㶲 c 记入 R·不动 Φ·不动 D·不动池。
    （R 通道付账·单事件账面形——读回是新散射事件的 R 份额入账。） -/
theorem refl_paid_readback (s : Ledger) (c : Nat) :
    (reflect s c).refl = s.refl + c ∧ (reflect s c).phi = s.phi
    ∧ (reflect s c).diss = s.diss ∧ (reflect s c).us = s.us := ⟨rfl, rfl, rfl, rfl⟩

/-- 读回不退耗散（P2 投影候选之二·增补）: reflect **行盲**（无行参·账本层不定位到行）——
    「散失份额分文不退」在账本层＝**签名无退款路径**（构造性·round12 B9）·
    行定位与幻肢门槛留执行器层; reflect 对 D 的账面增量恒为 0
    （幻肢回射语义·thermo_core.py L226-235 同形: 幻肢回射只入 R·散失行的 D 记录不变）。 -/
theorem readback_no_d_refund (s : Ledger) (c : Nat) :
    (reflect s c).diss = s.diss := rfl

/-- 读回付账来自查询侧: e0 计入 c·在场池不动（增补）——读回消耗查询侧㶲·
    不触碰在场池（companion readback_rows_unchanged 的账本层对应）。 -/
theorem readback_query_paid (s : Ledger) (c : Nat) :
    (reflect s c).e0 = s.e0 + c ∧ (reflect s c).us = s.us := ⟨rfl, rfl⟩

/-- D 存量正性在读回后保持（阿兰 §4.4 限定句账面形·增补·存量保持位·round12 B9 改名改述）:
    若 D 存量为正·则读回后 D 存量仍为正——**diss_monotone_reflect 的正性推论**·
    **非事件份额归属主张**（读回事件自身 ΔD 恒 0·见 `readback_no_d_refund`）。
    **限定**: 本定理不声称任何读出动作熵产生非零
    （Bennett 1982／Sagawa–Ueda 2008/2009·见本族头注）。 -/
theorem readback_d_pos_preserved (s : Ledger) (c : Nat) (hA : s.diss > 0) :
    (reflect s c).diss > 0 := hA

-- ---- §3-4 结算族（凝华·Deposon 本义·终端归零像·增补＋继承 T8） --------------

/-- 凝华全额付账（增补）: deposit 把行 i 的全部余量一次送入 D·D 增量恰为 u_i。 -/
theorem deposit_full_paid (s : Ledger) (i : Nat) (h : i < s.us.length) :
    (deposit s i).diss = s.diss + s.us[i] := by
  simp only [deposit, dif_pos h]

/-- 终端归零像（增补·R3 §2.8 absorption slot／T-B 终端归零的账本层对应）:
    任何守恒链·若在场池全为已凝华（0 项）·则 E⁰ 全额分解入三通道 Φ+R+D·
    U 终端为零位（kimi round11 3a: U 只是账面余数·终端余数可为零）。
    P2 账面读法: D 只进不出（§3-2）·终端无退款路径。 -/
theorem terminal_decomposed (s : Ledger) (h : Conserved s) (hz : ∀ u ∈ s.us, u = 0) :
    s.e0 = s.phi + s.refl + s.diss := by
  unfold Conserved at h
  rw [sum_all_zero s.us hz] at h
  omega

/-- 结算基线场景（继承 DeposonThermo T8 settle_close·逐字同场景）:
    注入 100×2 → 透射 10 → 行 b 支付 30+10+10=50（50 在场）·行 a 支付 20+10=30
    并凝华余量 70; D = 30+20+10+10+10+70 = 150·E⁰ = 210 = Φ10 + R0 + D150 + U50。 -/
def s0 : Ledger := ⟨0, 0, 0, 0, []⟩

def run : Ledger :=
  deposit
    (dissipate (dissipate (dissipate (dissipate (dissipate
      (transmit (inject (inject s0 100) 100) 10)
      0 30) 1 20) 0 10) 1 10) 0 10)
    1

theorem settle_close :
    run.e0 = 210 ∧ run.phi = 10 ∧ run.refl = 0 ∧ run.diss = 150 ∧ run.us = [50, 0] := by
  decide

theorem settle_conserved : Conserved run := by
  unfold Conserved
  decide

/-- 读回付账场景（增补·新）: 注入 100 → 透射 10 → 凝华（D=100·池 0 项）→
    读回付账 5 入 R（行盲读面·账本层不定位行·round12 B9 同口径）。E⁰ = 115 = Φ10 + R5 + D100 + U0 ——
    读回是**新散射事件**（R3 §2.9 K2 口径）·查询㶲经 R 份额入账·
    散失份额分文不退（readback_no_d_refund 的场景像）。 -/
def run2 : Ledger :=
  reflect (deposit (transmit (inject s0 100) 10) 0) 5

theorem settle_readback :
    run2.e0 = 115 ∧ run2.phi = 10 ∧ run2.refl = 5 ∧ run2.diss = 100 ∧ run2.us = [0] := by
  decide

theorem settle_readback_conserved : Conserved run2 := by
  unfold Conserved
  decide

-- ---- §3-5 桥接族（继承的形态级锚·单步对读·非形式导出） ---------------------------------
-- companion IrreversibleDeposon.lean V3State（L133-141）的热力学字段截面:
--   e0（总量）·phi / refl / diss（三终账）+ rows 的余量子列表（Q 列）。
-- ExeFace 是该截面的形态级复刻（0 触 companion·三钉 sha 不动）。

/-- 执行器层状态的热力学截面（companion V3State 的热力学五字段）。
    companion 的 Row 携 id/key/DEK/密文——截面删除之·热力学层只见余量子;
    墓碑链 tombs 与累积器 g 不入截面（执行器层构件）。 -/
structure ExeFace where
  e0 : Nat
  phi : Nat
  refl : Nat
  diss : Nat
  us : List Nat
  deriving Repr

/-- 投影: 执行器状态 → 热力学账本（截面删除墓碑链／累积器／DEK／密文面）。
    **proj 本身为字段拷贝（五字段双射·无损·round12 B7）**；分辨率下降发生在 ExeFace
    **截面选取**（墓碑链/累积器/DEK/密文不入截面）·账本不可回定位到行/墓碑
    （reflect 无行参）——守恒与单调逐字段保持（见下）。 -/
def proj (s : ExeFace) : Ledger := ⟨s.e0, s.phi, s.refl, s.diss, s.us⟩

/-- 执行器写口的热力学像（companion inject L193-194 同形: 池后置 ++ [r]·E⁰ += r.Q）。 -/
def exe_inject (s : ExeFace) (Q : Nat) : ExeFace :=
  { s with e0 := s.e0 + Q, us := s.us ++ [Q] }

/-- 执行器整行散失的热力学像（companion dissipate L199-204 的账本层像:
    整行 Q 全额入 D·行位记 0——即账本层 deposit·同 companion 一致）。
    i 为该行在截面池中的位置。 -/
def exe_dissipate (s : ExeFace) (i : Nat) : ExeFace :=
  { s with
    diss := s.diss + (if h : i < s.us.length then s.us[i] else 0),
    us := if h : i < s.us.length then s.us.set i 0 else s.us }

/-- 执行器受控读回的热力学像（companion readback L208-209 同形·
    幻肢门槛在执行器层·截面只见份额去向）。 -/
def exe_readback (s : ExeFace) (cP : Nat) : ExeFace :=
  { s with e0 := s.e0 + cP, refl := s.refl + cP }

/-- 投影保持 U: 投影后 U ＝ 截面池和（字段拷贝·U 语义无损）。 -/
theorem proj_U (s : ExeFace) : U (proj s) = s.us.sum := rfl

/-- 投影保持守恒（继承的形态级锚之一）: 截面守恒 ⇒ 投影守恒。
    companion 的 conserved_inject / conserved_dissipate / conserved_readback
    （L664-688）与本件 §3-1 **形态级同形可对读·非形式导出**（0 import·无形式桥·round12 B8）。 -/
theorem proj_conserved (s : ExeFace)
    (h : s.e0 = s.phi + s.refl + s.diss + s.us.sum) :
    Conserved (proj s) := by
  unfold Conserved proj
  exact h

/-- 写口投影对读（**仅单步·仅逐字段等值＋U 等值·列表不等·round12 B8**）:
    执行器写口的投影 ＝ 账本层写入（池形状差 append vs prepend 在池和等值意义下承接·
    us_append_one_sum）。**池序约定不同**（账本层前置 `q :: us` vs 执行器后置 `us ++ [Q]`）
    ⇒ **复合序列不交换**。反例（us=[10,20]）: `exe_inject 30; exe_dissipate 0` → U=50·
    而 `inject 30; deposit 0` → U=30（账本层 deposit 命中前置头位 30·执行器层散失原首行 10）。 -/
theorem proj_inject (s : ExeFace) (Q : Nat) :
    (proj (exe_inject s Q)).e0 = (inject (proj s) Q).e0
    ∧ (proj (exe_inject s Q)).phi = (inject (proj s) Q).phi
    ∧ (proj (exe_inject s Q)).refl = (inject (proj s) Q).refl
    ∧ (proj (exe_inject s Q)).diss = (inject (proj s) Q).diss
    ∧ U (proj (exe_inject s Q)) = U (inject (proj s) Q) := by
  refine ⟨rfl, rfl, rfl, rfl, ?_⟩
  show (s.us ++ [Q]).sum = Q + s.us.sum
  rw [us_append_one_sum]
  omega

/-- 散失投影对读: 执行器整行散失的投影 ＝ 账本层凝华结算（逐点恒等·**对本件镜像复刻
    exe_dissipate 成立**——companion 实际 dissipate 为整行删除·池长度变·非逐点对应；
    术语: 账本层「凝华」（0 项承载）vs 执行器层「散失」（整行删除）·round12 B8）。 -/
theorem proj_dissipate (s : ExeFace) (i : Nat) :
    proj (exe_dissipate s i) = deposit (proj s) i := by
  simp [proj, exe_dissipate, deposit]

/-- 读回投影对读: 执行器受控读回的投影 ＝ 账本层读回反射（逐点恒等·对 companion 同样成立
    ——readback 不动行池·无池序问题）。 -/
theorem proj_readback (s : ExeFace) (cP : Nat) :
    proj (exe_readback s cP) = reflect (proj s) cP := by
  simp [proj, exe_readback, reflect]

-- ============================================================
-- §4 公理面审计（报齐）
-- ============================================================
-- 0 新增公理。逐定理 #print axioms: 可接受集 = Lean 自带 propext / Quot.sound
-- （无 sorryAx·无 Classical.choice）; 无公理依赖＝decide 数据定理 4 条（settle 族）＋
-- rfl/构造项等值 9 条（diss_monotone 三向·refl_paid_readback·readback_no_d_refund·
-- readback_query_paid·readback_d_pos_preserved·proj_U·proj_conserved）（round12 A6）。
-- CI 沿 DeposonThermo.lean 同口径 grep 构建日志的 sorryAx（0 命中）。

#print axioms sum_set
#print axioms us_append_one_sum
#print axioms sum_all_zero
#print axioms sum_drop_zero
#print axioms conserved_inject
#print axioms conserved_dissipate
#print axioms conserved_transmit
#print axioms conserved_reflect
#print axioms conserved_deposit
#print axioms diss_monotone_inject
#print axioms diss_monotone_dissipate
#print axioms diss_monotone_transmit
#print axioms diss_monotone_reflect
#print axioms diss_monotone_deposit
#print axioms no_recover_shape
#print axioms pool_monotone
#print axioms pool_monotone_deposit
#print axioms refl_paid_readback
#print axioms readback_no_d_refund
#print axioms readback_query_paid
#print axioms readback_d_pos_preserved
#print axioms deposit_full_paid
#print axioms terminal_decomposed
#print axioms settle_close
#print axioms settle_conserved
#print axioms settle_readback
#print axioms settle_readback_conserved
#print axioms proj_U
#print axioms proj_conserved
#print axioms proj_inject
#print axioms proj_dissipate
#print axioms proj_readback

end DeposonThermoRecon
