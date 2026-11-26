/-
IrreversibleDeposon.lean — machine-checked structure of the irreversible executor
(v3 organ: write port = irreversible executor; read surface = controlled readback).

Companion to `harness/DeposonThermo.lean` (T6 `diss_monotone`, no `recover` transition in
the signature) and `mcp/thermo_core.py` (frozen preview.10 core — untouched, read-only).
Companion prototype: `irreversible_executor.py` (self-test `selftest_organ_v3.py`).

Model (core-only, no mathlib, no `sorry`; integer exergy over ℕ, axiom A5: no temperature,
no potential function — same discipline as DeposonThermo):

  A v3 state carries the thermodynamic accounts of DeposonThermo (`e0 / phi / refl / diss`;
  `e0` = CUMULATIVE injected exergy (rows + queries), not initial exergy — 阿兰 §5-v)
  plus the two objects the executor adds:
    • the in-presence pool `rows : List Row` — every live row carries its DEK;
      the key lives ONLY here, never in the append-only log;
    • the tombstone chain `tombs : List (TBody × Hash)` — append-only, hash-linked.

Executor invariants that hold BY CONSTRUCTION (the record grammar has no field for them):
    I1  an inject record carries ciphertext + a DEK commitment — no plaintext, no DEK;
    I3  a tombstone carries exergy and metadata — no text, no DEK, no ciphertext.
  These are type-level: `Cipher` and `TBody` simply have no `text` field. The executor's
  job at runtime (`irreversible_executor.py`) is to keep the *files* faithful to these
  types: the log is parsed into exactly these records and anything else fails loud (I1/I3).

v3.1 additions (kimi round5 ⑤, PI 00:05 夜间授权·kimi＋Lean 双审代裁):
  • T-3a 背景场统计残留执行器 = g_aether 累积器 `G` (n / q / mass): 只进不出·只存统计·不存内容·
    作为后续散射的偏置读数（偏置落点＝工具层·冻结 rank_key 0 动）. G1–G4.
  • T-3b 文本盲辅助条件「元数据与内容条件独立」: 文本进入 Row 只经 (length, ciphertext) [E3-aux];
    id / dek_commit 与文本无关 [阿兰前提 1·2]; mass 是唯一文本派生字段且非单射 ⇒ 墓碑不是
    内容的可逆编码 [E3′]. 部署可选项 mass_bucket（指数桶）缺省关——裁位见设计件.
  • T-1 付费只买元数据: 付费回视 readback 的状态写面只有 (e0, refl)——池/链/累积器/D 全不动
    [readback_metadata_only]; 接口面无 recover 入口（类型级：无此迁移）.
  • 池备份回灌 (A3) 不设防 = 理论边界（本件不证、不假设、只声明——见文件末「理论边界声明」）.

What needs proof:

  E1  pool_no_key_after_dissipate — after `dissipate rid`, no pooled row has id = rid
      (the DEK is gone with the row: cryptographic erasure executed).
  E3  tombstone_text_blind — the tombstone body depends on the row only through
      (id, key, mass, Q). Equal-length texts with different DEKs ⇒ byte-identical
      tombstone. This is the formal content of "controlled readback is not an inverse
      process": the read surface is a function of the tombstone, and the tombstone is
      blind to the text. An inverse would have to tell the two texts apart; it cannot.
  E4  chain_link_invariant / chain_drop_breaks — the tombstone chain is link-verifiable,
      and dropping a link is detected. Conditional on hash injectivity (a hypothesis of
      the theorem, not an axiom of the file — the real guarantee is computational).
  E5  conserved_inject / conserved_dissipate / conserved_readback and
      diss_monotone_inject / diss_monotone_dissipate / diss_monotone_readback —
      the v3 transitions keep the first law `e0 = phi + refl + diss + U` and the
      second-law direction anchor (`diss` never decreases). The executor adds structure
      and changes no thermodynamic bookkeeping: compatibility with `Conserved` and T6.

v3.1 review (kimi round6·双审代裁·PI 00:05) — 三条口径钉死：
  • 单调性口径：G1 `absorb_all_monotone` 与 E5 `diss_monotone_*` 证的是 **append-only 构造的 fold 单调性**
    （记账结构性质），不是物理第二律；本体只有三样——行·墓碑链·累积器读数；㶲/aether/耗散
    是命名与记账量纲。任何「满足热力学约束」的写法不成立。
  • 累积器「读数」→「执行器」缺的一跳已补：`phantom_budget`（回视预算 = f(G)）使 G 进入系统转移函数
    ——有 G 与无 G 的决策不同且可观测（G5–G7）；不改 rank_key·不改 Reducer。
  • 文本盲辅助条件的形式：E3′ 非单射 ⇒ **不存在内容的可逆编码**（否证确定性反解）；它**不**否证
    统计侧信道（长度分布有偏时长度携带信息）——后者是声明的接受风险·桶化只粗化不消除。

v3.1.1 (查理 R3 候位①·管理员 00:59 派·kimi＋Lean 双审)：可读表（幻肢行）边界——记录键 record_key
  （`TBody.key`·记忆地址·调用方选定）与 DEK（`Row.dek`·加密钥·散失即毁）是两个对象；R3 稿面
  「key」一词撞车（kimi R6-1）。本件把两种可读表形态都建模并证其边界：
    K-in  `ReadKin`  = (record_key, mass, cause, t)            —— 逐碑渲染·含记录键（现役 phantom_line 形态）
    K-out `ReadKout` = (mass, cause, t)                        —— 不渲染记录键·以查询前缀寻址
  两形态皆**不含 DEK／密文／明文**（类型级）。定理：K-in 暴露记录键（R-in-1）；K-out 对记录键盲（R-out-1）
  且对文本盲（R-out-2·E3 推论）；K-out 以查询寻址——渲染元组的键分量恒为查询 q 而非存储键（R-out-3）。
  可读表边界＝TBody 类型（read_* 只依赖 body·body 无内容字段）。

v3.1.1 裁（kimi round7·双审代裁）：**理论一般形＝K-out；K-in＝单写者特例（四条件缺一落回 K-out）**。
  本席草案曾把 K-in 当默认、K-out 当备选——kimi 判「主次反了」·已翻。
  E3 scope 拆分（不许合并叙述）：一般形 `kout_blind_general`（任意同 (mass,cause,t) 墓碑在可读表不可区分·
  与 id/key 无关）挂在 K-out；K-in 下只余同址推论 `kin_blind_same_address`。
  aux-CI_key（策略层·非密码学）：地址须属声明式文法 Σ（`Addr.valid`·写入口校验）·写路径无 PT→Addr 派生边
  （类型级：`row_of_addr` 以 Addr 与 text 为独立入参）·同址重写键不变（`addr_invariant_under_rewrite`）。
  Lean 只编码「key 是参数＋有效位」·Σ 封闭性靠写入口·**不写成已证性质**。
  K-in 条件 4（精确地址读）：`kin_render_guard`——仅 q = 记录键时渲染 K-in 行·前缀查询回 q 相对分量（K-out）。
  多写者结构性修法：按 principal 分区命名空间·可读表只渲染 local 分量（`kin_local_principal_blind`）。

Axiom audit: one `#print axioms` per theorem (58/58).

理论边界声明（kimi round5 ⑤(c)·显式标注·不证不假设）：
  A3「池备份回灌」(从旧池文件/快照恢复已销毁 DEK) 不在执行器敌手模型内——若 A3 可行，等价于「存在
  一个能容纳无限长历史且可回灌的存储层」（不写「以太」——那是比喻名），属另一理论，非本理论漏洞。
  本文件对此 0 定理、0 公理；
  部署层的物理残留（SSD 磨损均衡/快照/内存残影）同归此边界。 Acceptable set = Lean's own
`propext` / `Quot.sound` (no `sorryAx`, no `Classical.choice`).
-/

namespace IrreversibleDeposon

abbrev RowId := Nat
abbrev Hash := Nat

/-- Ciphertext record — what the append-only log's inject line carries. No text, no DEK. -/
structure Cipher where
  body : String
  dek_commit : Hash
  deriving Repr

/-- In-presence row: lives only in the pool; carries its DEK. -/
structure Row where
  id : RowId
  key : String
  ct : Cipher
  mass : Nat        -- len(text) at write time: exergy-scale, not content
  Q : Nat           -- remaining exergy of the row (U_row)
  dek : Nat         -- the DEK itself — ONLY in the pool
  deriving Repr

/-- Tombstone body: exergy + metadata. No text, no DEK, no ciphertext. -/
structure TBody where
  id : RowId
  key : String
  mass : Nat
  cause : String
  q : Nat           -- exergy this row sent to D over its life
  t : Nat
  prev : Hash
  deriving Repr

/-- 背景场统计残留执行器（g_aether 累积器）：只进不出·只存统计·不存内容。
    每次散失吸收一块墓碑的 (q, mass)；无任何迁移能使其减少（G1）。 -/
structure G where
  n : Nat          -- dissipated row count
  q : Nat          -- Σ exergy sent to D
  mass : Nat       -- Σ mass (characters)
  deriving Repr

/-- v3 state: DeposonThermo accounts + pool + tombstone chain + accumulator. -/
structure V3State where
  rows : List Row
  tombs : List (TBody × Hash)
  g : G
  e0 : Nat
  phi : Nat
  refl : Nat
  diss : Nat
  deriving Repr

def absorb (g : G) (b : TBody) : G := ⟨g.n + 1, g.q + b.q, g.mass + b.mass⟩

def absorb_all : G → List (TBody × Hash) → G
  | g, [] => g
  | g, (b, _) :: rest => absorb_all (absorb g b) rest

-- ---- pool arithmetic --------------------------------------------------------

def sumQ (rs : List Row) : Nat := rs.foldr (fun r acc => r.Q + acc) 0

def remove_id (rid : RowId) : List Row → List Row
  | [] => []
  | r :: rs => if r.id = rid then remove_id rid rs else r :: remove_id rid rs

def sumQ_id (rid : RowId) : List Row → Nat
  | [] => 0
  | r :: rs => (if r.id = rid then r.Q else 0) + sumQ_id rid rs

def U (s : V3State) : Nat := sumQ s.rows

/-- First law (attribution conservation), as in DeposonThermo. -/
def Conserved (s : V3State) : Prop := s.e0 = s.phi + s.refl + s.diss + U s

-- ---- tombstone chain --------------------------------------------------------

def last_hash : List (TBody × Hash) → Hash
  | [] => 0
  | [(_, h)] => h
  | _ :: xs => last_hash xs

-- Abstract hash `H` (section variable). Injectivity is a *hypothesis* where needed (E4),
-- never an axiom of this file.
variable (H : TBody → Hash)

/-- Chain check: every link must carry the previous link's hash and its own body hash. -/
def chain_ok : Hash → List (TBody × Hash) → Bool
  | _, [] => true
  | prev, (b, h) :: rest => (b.prev == prev && h == H b) && chain_ok h rest

/-- Tombstones for a batch of removed rows, hash-linked onto `prev`. -/
def tombs_for (cause : String) (t : Nat) (prev : Hash) : List Row → List (TBody × Hash)
  | [] => []
  | r :: rs =>
    let b : TBody := { id := r.id, key := r.key, mass := r.mass, cause := cause, q := r.Q, t := t, prev := prev }
    let h := H b
    (b, h) :: tombs_for cause t h rs

-- ---- transitions ------------------------------------------------------------

/-- Write port (executor): the row enters the pool with its DEK; its Q enters U. -/
def inject (s : V3State) (r : Row) : V3State :=
  { s with rows := s.rows ++ [r], e0 := s.e0 + r.Q }

/-- Irreversible executor: every pooled row with id = rid is deposited (U → D), its
    tombstone is appended to the chain, and — in the Python executor — its DEK is
    destroyed after the commit. No transition ever re-adds a deposited row. -/
def dissipate (s : V3State) (rid : RowId) (cause : String) (t : Nat) : V3State :=
  { s with
    rows := remove_id rid s.rows
    tombs := s.tombs ++ tombs_for H cause t (last_hash s.tombs) (s.rows.filter (fun r => r.id = rid))
    g := absorb_all s.g (tombs_for H cause t (last_hash s.tombs) (s.rows.filter (fun r => r.id = rid)))
    diss := s.diss + sumQ_id rid s.rows }

/-- Controlled readback (phantom line): paid from query exergy into R; only reachable
    for a row that has a tombstone. Touches no row, no DEK, no ciphertext. -/
def readback (s : V3State) (rid : RowId) (cP : Nat) : V3State :=
  if s.tombs.any (fun p => p.1.id = rid) then { s with e0 := s.e0 + cP, refl := s.refl + cP } else s

-- ==== E1 =====================================================================

theorem remove_id_excludes (rid : RowId) : ∀ (rs : List Row) (r : Row),
    r ∈ remove_id rid rs → r.id ≠ rid := by
  intro rs
  induction rs with
  | nil => intro r h; exact absurd h (List.not_mem_nil _)
  | cons x xs ih =>
    intro r h
    simp only [remove_id] at h
    by_cases hx : x.id = rid
    · rw [if_pos hx] at h; exact ih r h
    · rw [if_neg hx] at h
      rcases List.mem_cons.mp h with rfl | h'
      · exact hx
      · exact ih r h'

theorem pool_no_key_after_dissipate (s : V3State) (rid : RowId) (cause : String) (t : Nat)
    (r : Row) (h : r ∈ (dissipate H s rid cause t).rows) : r.id ≠ rid :=
  remove_id_excludes rid _ r h

-- ==== E3 =====================================================================

/-- A row as produced by the write port from a plaintext: text enters only through
    `mass = text.length` and through the ciphertext under its (private) DEK. -/
def row_of (enc : Nat → String → String) (hsh : Nat → Hash) (id : RowId) (key : String)
    (text : String) (Q dek : Nat) : Row :=
  { id := id, key := key, ct := { body := enc dek text, dek_commit := hsh dek },
    mass := text.length, Q := Q, dek := dek }

theorem tomb_body_indep_of_cipher (cause : String) (t : Nat) (prev : Hash) (r r' : Row)
    (hid : r.id = r'.id) (hk : r.key = r'.key) (hm : r.mass = r'.mass) (hq : r.Q = r'.Q) :
    tombs_for H cause t prev [r] = tombs_for H cause t prev [r'] := by
  simp only [tombs_for, hid, hk, hm, hq]

theorem tombstone_text_blind (enc : Nat → String → String) (hsh : Nat → Hash)
    (id : RowId) (key : String) (t₁ t₂ : String) (Q dek dek' : Nat)
    (cause : String) (t : Nat) (prev : Hash) (h : t₁.length = t₂.length) :
    tombs_for H cause t prev [row_of enc hsh id key t₁ Q dek]
      = tombs_for H cause t prev [row_of enc hsh id key t₂ Q dek'] :=
  tomb_body_indep_of_cipher H cause t prev _ _ rfl rfl h rfl

-- ==== E3-aux / E3′ (T-3b 文本盲辅助条件·阿兰三前提) ==========================

/-- 文本进入 Row 只经两个量：length 与 (在钥下的) ciphertext。给定二者相等则 Row 相等——
    即 Row ⊥ text | (length, ct)：这是「元数据与内容条件独立」的形式读法（mass 除外·见下）。 -/
theorem row_text_derived_fields (enc : Nat → String → String) (hsh : Nat → Hash)
    (id : RowId) (key : String) (t₁ t₂ : String) (Q dek : Nat)
    (hm : t₁.length = t₂.length) (hct : enc dek t₁ = enc dek t₂) :
    row_of enc hsh id key t₁ Q dek = row_of enc hsh id key t₂ Q dek := by
  simp [row_of, hm, hct]

/-- 阿兰前提 1：id 不得由明文派生——row_of 的 id 恒为参数 id，与 text 无关。 -/
theorem row_id_indep_of_text (enc : Nat → String → String) (hsh : Nat → Hash)
    (id : RowId) (key : String) (t₁ t₂ : String) (Q dek : Nat) :
    (row_of enc hsh id key t₁ Q dek).id = id ∧ (row_of enc hsh id key t₂ Q dek).id = id :=
  ⟨rfl, rfl⟩

/-- 阿兰前提 2：dek_commit 只承诺钥、不承诺文——与 text 无关。 -/
theorem dek_commit_indep_of_text (enc : Nat → String → String) (hsh : Nat → Hash)
    (id : RowId) (key : String) (t₁ t₂ : String) (Q dek : Nat) :
    (row_of enc hsh id key t₁ Q dek).ct.dek_commit = (row_of enc hsh id key t₂ Q dek).ct.dek_commit :=
  rfl

/-- 阿兰前提 3（声明位）：mass 是唯一文本派生字段（＝ |text|）。 -/
theorem mass_is_text_length (enc : Nat → String → String) (hsh : Nat → Hash)
    (id : RowId) (key : String) (text : String) (Q dek : Nat) :
    (row_of enc hsh id key text Q dek).mass = text.length :=
  rfl

/-- E3′：墓碑不是内容的可逆编码——存在两个不同文本给出同一墓碑（"a" 与 "b"）。
    元数据 → 内容 的映射非单射，故不可能从墓碑反推文本（kimi round5 ②(b)/⑤(b) 的「可逆编码」排除）。 -/
theorem tomb_not_injective_on_text (enc : Nat → String → String) (hsh : Nat → Hash)
    (id : RowId) (key : String) (Q dek : Nat) (cause : String) (t : Nat) (prev : Hash) :
    ("a" : String) ≠ ("b" : String) ∧
    tombs_for H cause t prev [row_of enc hsh id key "a" Q dek]
      = tombs_for H cause t prev [row_of enc hsh id key "b" Q dek] := by
  refine ⟨by decide, ?_⟩
  exact tombstone_text_blind H enc hsh id key "a" "b" Q dek dek cause t prev rfl

/-- K15（阿兰 00:48 试编·采·出处：阿兰 Lean 审读件 §4）：长度不是文本的可逆编码——
    不存在 g : Nat → String 使 g (t.length) = t 对一切 t 成立。与 E3′ 同义（非单射 ⇔ 无左逆），
    此形更直接：元数据中唯一的文本派生字段 mass 不可能被反推回文本。 -/
theorem length_not_invertible : ¬ ∃ g : Nat → String, ∀ t : String, g t.length = t := by
  intro ⟨g, hg⟩
  have h1 : g (String.length "a") = "a" := hg "a"
  have h2 : g (String.length "b") = "b" := hg "b"
  have e : String.length "a" = String.length "b" := by decide
  have hne : ("a" : String) ≠ "b" := by decide
  exact hne (by rw [← h1, e, h2])

-- ==== G1–G4 (T-3a g_aether 累积器) ============================================

theorem absorb_monotone (g : G) (b : TBody) :
    g.n ≤ (absorb g b).n ∧ g.q ≤ (absorb g b).q ∧ g.mass ≤ (absorb g b).mass := by
  simp [absorb]

/-- G1 只进不出：吸收任意墓碑序列后三分量皆单调不降。 -/
theorem absorb_all_monotone (g : G) (l : List (TBody × Hash)) :
    g.n ≤ (absorb_all g l).n ∧ g.q ≤ (absorb_all g l).q ∧ g.mass ≤ (absorb_all g l).mass := by
  induction l generalizing g with
  | nil => simp [absorb_all]
  | cons x xs ih =>
    obtain ⟨b, h⟩ := x
    simp only [absorb_all]
    obtain ⟨h1, h2, h3⟩ := absorb_monotone g b
    obtain ⟨i1, i2, i3⟩ := ih (absorb g b)
    exact ⟨Nat.le_trans h1 i1, Nat.le_trans h2 i2, Nat.le_trans h3 i3⟩

theorem absorb_content_blind (g : G) (b b' : TBody) (hq : b.q = b'.q) (hm : b.mass = b'.mass) :
    absorb g b = absorb g b' := by
  simp [absorb, hq, hm]

/-- G2/G3 只存统计·内容盲：累积器只依赖墓碑的 (q, mass) 序列——与 id/key/cause/t/prev/h 全无关。 -/
theorem absorb_all_eq_of_stat_eq (g : G) : ∀ (l l' : List (TBody × Hash)),
    List.map (fun p : TBody × Hash => (p.1.q, p.1.mass)) l
      = List.map (fun p : TBody × Hash => (p.1.q, p.1.mass)) l' →
    absorb_all g l = absorb_all g l' := by
  intro l
  induction l generalizing g with
  | nil =>
    intro l' h
    simp only [List.map_nil] at h
    cases l' with
    | nil => rfl
    | cons x xs => simp at h
  | cons x xs ih =>
    intro l' h
    cases l' with
    | nil => simp at h
    | cons y ys =>
      simp only [List.map_cons, List.cons.injEq, Prod.mk.injEq] at h
      obtain ⟨⟨hq, hm⟩, htail⟩ := h
      simp only [absorb_all, absorb_content_blind g x.1 y.1 hq hm]
      exact ih (absorb g y.1) ys htail

/-- G4 计数：吸收 k 块墓碑后 n 恰增 k（只进·且每碑恰计一次）。 -/
theorem absorb_all_count (g : G) (l : List (TBody × Hash)) : (absorb_all g l).n = g.n + l.length := by
  induction l generalizing g with
  | nil => simp [absorb_all]
  | cons x xs ih =>
    simp only [absorb_all, List.length_cons]
    rw [ih (absorb g x.1)]
    simp only [absorb]
    omega

theorem g_monotone_dissipate (s : V3State) (rid : RowId) (cause : String) (t : Nat) :
    s.g.n ≤ (dissipate H s rid cause t).g.n ∧ s.g.q ≤ (dissipate H s rid cause t).g.q
      ∧ s.g.mass ≤ (dissipate H s rid cause t).g.mass :=
  absorb_all_monotone _ _

theorem g_unchanged_inject (s : V3State) (r : Row) : (inject s r).g = s.g := rfl

-- ==== G5–G7 回视预算执行器（kimi round6 Q2「缺的一跳」）=======================

/-- 回视预算策略 p1：单读至多回射的幻肢条数 = clamp(1 + log2(1 + G.q / Q_ref), 1, phantomK)。
    这是「累积器读数」成为「累积器执行器」的那一跳：G 进入系统转移函数（门事件的 ph 列表长度），
    有 G 与无 G 的决策不同且可观测（R 账随之变）；记账规则不变（冻结 Reducer 处理门事件）。
    策略**形式**系建模选择（场吸收越多·后续散射分给 R 的份额越多）·候裁；p1 的存在性与可证伪性是定理。 -/
def phantom_budget (phantomK qRef : Nat) (g : G) : Nat :=
  max 1 (min phantomK (1 + Nat.log2 (1 + g.q / qRef)))

theorem nat_div_mono_left (a b k : Nat) (h : a ≤ b) : a / k ≤ b / k := by
  by_cases hk : k = 0
  · simp [hk]
  · rw [Nat.le_div_iff_mul_le (by omega)]
    exact Nat.le_trans (Nat.div_mul_le_self a k) h

theorem nat_log2_mono (a b : Nat) (h : a ≤ b) (hb : b ≠ 0) : Nat.log2 a ≤ Nat.log2 b := by
  have hb2 : b < 2 ^ (Nat.log2 b + 1) := (Nat.log2_lt hb).mp (Nat.lt_succ_self _)
  by_cases ha : a = 0
  · simp [ha]
  · have h1 : a < 2 ^ (Nat.log2 b + 1) := Nat.lt_of_le_of_lt h hb2
    have h2 := (Nat.log2_lt ha).mpr h1
    omega

theorem nat_max_mono {a b a' b' : Nat} (ha : a ≤ a') (hb : b ≤ b') : max a b ≤ max a' b' :=
  (Nat.max_le).2 ⟨Nat.le_trans ha (Nat.le_max_left _ _), Nat.le_trans hb (Nat.le_max_right _ _)⟩

theorem nat_min_mono {a b a' b' : Nat} (ha : a ≤ a') (hb : b ≤ b') : min a b ≤ min a' b' :=
  (Nat.le_min).2 ⟨Nat.le_trans (Nat.min_le_left _ _) ha, Nat.le_trans (Nat.min_le_right _ _) hb⟩

/-- G5 有界：1 ≤ 预算 ≤ phantomK。 -/
theorem phantom_budget_bounds (phantomK qRef : Nat) (hk : 1 ≤ phantomK) (g : G) :
    1 ≤ phantom_budget phantomK qRef g ∧ phantom_budget phantomK qRef g ≤ phantomK := by
  refine ⟨?_, ?_⟩ <;> simp only [phantom_budget]
  · exact Nat.le_max_left _ _
  · exact (Nat.max_le).2 ⟨hk, Nat.min_le_left phantomK (1 + Nat.log2 (1 + g.q / qRef))⟩

/-- G6 单调：场吸收越多（g.q 越大）·回视预算越大。 -/
theorem phantom_budget_mono (phantomK qRef : Nat) (g g' : G) (h : g.q ≤ g'.q) :
    phantom_budget phantomK qRef g ≤ phantom_budget phantomK qRef g' := by
  simp only [phantom_budget]
  have hb : (1 + g'.q / qRef) ≠ 0 := by simp
  have hdiv : g.q / qRef ≤ g'.q / qRef := nat_div_mono_left _ _ _ h
  have hpre : 1 + g.q / qRef ≤ 1 + g'.q / qRef := Nat.add_le_add_left hdiv 1
  have hlog := nat_log2_mono (1 + g.q / qRef) (1 + g'.q / qRef) hpre hb
  have hlog' : 1 + Nat.log2 (1 + g.q / qRef) ≤ 1 + Nat.log2 (1 + g'.q / qRef) := Nat.add_le_add_left hlog 1
  exact nat_max_mono (Nat.le_refl _) (nat_min_mono (Nat.le_refl _) hlog')

/-- G7 决策可异：空场 (G = 0) 下预算恰为 1，严格小于 phantomK（≥ 2）——
    「有 G」与「无 G（恒 phantomK）」的决策不同且可观测（on/off 对照可证伪）。 -/
theorem phantom_budget_zero_eq_one (phantomK qRef : Nat) (hk : 2 ≤ phantomK) :
    phantom_budget phantomK qRef ⟨0, 0, 0⟩ = 1 := by
  have h1 : Nat.log2 1 = 0 := by
    have h := (Nat.log2_lt (by decide : (1 : Nat) ≠ 0)).mpr (by decide : (1 : Nat) < 2 ^ 1)
    omega
  simp only [phantom_budget, Nat.zero_div, h1]
  rw [Nat.min_eq_right (by omega : (1 : Nat) ≤ phantomK), Nat.max_self]

/-- 阿兰 §5-i：自追加不破链——tombs_for 把一批墓碑接到链头 prev 上后链核仍通过。 -/
theorem chain_ok_tombs_for (cause : String) (t : Nat) : ∀ (prev : Hash) (rs : List Row),
    chain_ok H prev (tombs_for H cause t prev rs) = true := by
  intro prev rs
  induction rs generalizing prev with
  | nil => simp [tombs_for, chain_ok]
  | cons r rest ih =>
    simp only [tombs_for, chain_ok]
    rw [ih (H { id := r.id, key := r.key, mass := r.mass, cause := cause, q := r.Q, t := t, prev := prev })]
    simp

/-- 阿兰 §5-iii：读出面建模——回视读到的只是墓碑元数据（Option TBody·无内容字段可出）。 -/
def read_surface (s : V3State) (rid : RowId) : Option TBody :=
  match s.tombs.find? (fun p => p.1.id = rid) with
  | some (b, _) => some b
  | none => none

theorem read_surface_depends_only_on_tombs (s s' : V3State) (rid : RowId) (h : s.tombs = s'.tombs) :
    read_surface s rid = read_surface s' rid := by
  simp [read_surface, h]

theorem read_surface_unchanged_by_inject (s : V3State) (r : Row) (rid : RowId) :
    read_surface (inject s r) rid = read_surface s rid :=
  read_surface_depends_only_on_tombs _ _ _ (by simp [inject])

theorem read_surface_unchanged_by_readback (s : V3State) (rid c : RowId) (cP : Nat) :
    read_surface (readback s rid cP) c = read_surface s c :=
  read_surface_depends_only_on_tombs _ _ _ (by simp [readback]; split <;> rfl)

-- ==== 可读表边界（v3.1.1·记录键候位①）=========================================

/-- 可读表形态 K-in：逐碑渲染·含记录键（现役 `phantom_line` 形态：key／mass／cause／t_dep）。 -/
structure ReadKin where
  key : String        -- record key（记忆地址·调用方选定）——**不是 DEK**
  mass : Nat
  cause : String
  t : Nat
  deriving Repr

/-- 可读表形态 K-out：不渲染记录键·只出 (mass, cause, t)；寻址靠查询前缀（见 render_q）。 -/
structure ReadKout where
  mass : Nat
  cause : String
  t : Nat
  deriving Repr

def read_kin (b : TBody) : ReadKin := ⟨b.key, b.mass, b.cause, b.t⟩
def read_kout (b : TBody) : ReadKout := ⟨b.mass, b.cause, b.t⟩

/-- 可读表边界：两形态都只是墓碑体的函数——而 TBody 无明文/DEK/密文字段（类型级）。
    故「可读表 ⊆ 墓碑元数据」是结构事实·不是约定。 -/
theorem read_depends_only_on_body (b b' : TBody) (h : b = b') :
    read_kin b = read_kin b' ∧ read_kout b = read_kout b' := by
  subst h; exact ⟨rfl, rfl⟩

/-- R-in-1：K-in **暴露记录键**——仅记录键不同的两碑·可读表不同（形态事实·非缺陷声明）。 -/
theorem kin_exposes_record_key (b : TBody) (k k' : String) (hne : k ≠ k') :
    read_kin { b with key := k } ≠ read_kin { b with key := k' } := by
  intro h
  have : k = k' := by
    have := congrArg ReadKin.key h
    simpa using this
  exact hne this

/-- R-out-1：K-out **对记录键盲**——仅记录键不同的两碑·可读表逐位相等。 -/
theorem kout_record_key_blind (b : TBody) (k k' : String) :
    read_kout { b with key := k } = read_kout { b with key := k' } := by
  simp [read_kout]

/-- R-out-2：K-out 对文本盲（E3 推论）：等长异文·异 DEK ⇒ 可读表逐位相等。 -/
theorem kout_text_blind (H : TBody → Hash) (enc : Nat → String → String) (hsh : Nat → Hash)
    (id : RowId) (key : String) (t₁ t₂ : String) (Q dek dek' : Nat)
    (cause : String) (t : Nat) (prev : Hash) (h : t₁.length = t₂.length) :
    (tombs_for H cause t prev [row_of enc hsh id key t₁ Q dek]).map (fun p => read_kout p.1)
      = (tombs_for H cause t prev [row_of enc hsh id key t₂ Q dek']).map (fun p => read_kout p.1) := by
  rw [tombstone_text_blind H enc hsh id key t₁ t₂ Q dek dek' cause t prev h]

/-- K-out 以查询寻址：服务端仍用存储键做前缀匹配（`starts_with q`·存储键不出服务端），
    渲染给调用方的元组键分量**恒为查询 q**（调用方已知）·统计分量为 K-out。 -/
def starts_with (q : String) (b : TBody) : Bool := String.startsWith b.key q
def render_q (q : String) (b : TBody) : String × ReadKout := (q, read_kout b)

/-- R-out-3：渲染元组与存储键无关（给定皆匹配 q）——调用方从渲染面学不到 q 之外的存储键信息。 -/
theorem render_q_indep_of_stored_key (q : String) (b : TBody) (k k' : String) :
    render_q q { b with key := k } = render_q q { b with key := k' } := by
  simp [render_q, read_kout]

/-- R-out-4（边界如实·kimi round7 Q4 修正）：前缀匹配**不是**「1 比特/查询」——是键集合枚举 oracle
    （O(|K|·d) 次查询可重建存储键集合·不含内容）。首段匹配只是部分缓解；结构性修法＝按 principal 分区命名空间
    （见下）。本定理只记录「匹配谓词是布尔回执」这一事实·边界按 round7 原文声明。 -/
theorem starts_with_is_bool (q : String) (b : TBody) :
    starts_with q b = true ∨ starts_with q b = false := by
  cases starts_with q b <;> simp

/-- **E3 一般形（K-out）**：任意两条 (mass, cause, t) 相同的墓碑——**无论 id／record_key**——可读表逐位相等。
    这是「任意同元数据墓碑不可区分」的正确 scope；K-in 下不成立（R-in-1）。 -/
theorem kout_blind_general (b b' : TBody) (hm : b.mass = b'.mass) (hc : b.cause = b'.cause)
    (ht : b.t = b'.t) : read_kout b = read_kout b' := by
  simp only [read_kout, hm, hc, ht]

/-- **E3 同址推论（K-in）**：仅当 id 与 record_key 皆同（同址重写）时·等长异文 ⇒ 可读表相等。
    比 `kout_blind_general` 窄——稿面须单列·不得套一般形话术。 -/
theorem kin_blind_same_address (H : TBody → Hash) (enc : Nat → String → String) (hsh : Nat → Hash)
    (id : RowId) (key : String) (t₁ t₂ : String) (Q dek dek' : Nat)
    (cause : String) (t : Nat) (prev : Hash) (h : t₁.length = t₂.length) :
    (tombs_for H cause t prev [row_of enc hsh id key t₁ Q dek]).map (fun p => read_kin p.1)
      = (tombs_for H cause t prev [row_of enc hsh id key t₂ Q dek']).map (fun p => read_kin p.1) := by
  rw [tombstone_text_blind H enc hsh id key t₁ t₂ Q dek dek' cause t prev h]

/-- 地址类型（aux-CI_key·策略层）：`valid` 由写入口按声明式文法 Σ 校验；Lean 只编码「地址是带有效位的参数」。 -/
structure Addr where
  name : String
  valid : Bool
  deriving Repr

/-- 写 API 形态：`write : Addr × PT → Row`——Addr 与 text 为**独立入参**（类型级无 PT→Addr 派生边）。 -/
def row_of_addr (enc : Nat → String → String) (hsh : Nat → Hash) (id : RowId) (a : Addr)
    (text : String) (Q dek : Nat) : Row :=
  row_of enc hsh id a.name text Q dek

/-- aux-CI_key(3)：同址重写键不变。 -/
theorem addr_invariant_under_rewrite (enc : Nat → String → String) (hsh : Nat → Hash)
    (id : RowId) (a : Addr) (t₁ t₂ : String) (Q dek : Nat) :
    (row_of_addr enc hsh id a t₁ Q dek).key = (row_of_addr enc hsh id a t₂ Q dek).key := rfl

/-- aux-CI_key(2)：写路径无 PT→Addr 派生边——给定同一 Addr·Row 的键分量与 text 无关（text 只经 length/ct 入 Row）。
    注意：这只编码「Addr 是参数」·**不保证调用点传进来的 Addr.name 不是 text 的函数**——后者是策略层约束。 -/
theorem row_key_indep_of_text_via_addr (enc : Nat → String → String) (hsh : Nat → Hash)
    (id : RowId) (a : Addr) (t₁ t₂ : String) (Q dek : Nat)
    (hm : t₁.length = t₂.length) (hct : enc dek t₁ = enc dek t₂) :
    row_of_addr enc hsh id a t₁ Q dek = row_of_addr enc hsh id a t₂ Q dek := by
  simp [row_of_addr, row_of, hm, hct]

/-- K-in 条件 4（精确地址读）：仅当查询 q 恰等于记录键时渲染 K-in 行；前缀查询不渲染 K-in
    （调用方得 K-out 的 q 相对分量）——关闭前缀枚举 oracle 对 K-in 的作用。 -/
def kin_render_guard (q : String) (b : TBody) : Option ReadKin :=
  if b.key = q then some (read_kin b) else none

theorem kin_exact_no_partial_leak (q : String) (b : TBody) (hne : q ≠ b.key) :
    kin_render_guard q b = none := by
  simp [kin_render_guard, Ne.symm hne]

theorem kin_exact_renders (q : String) (b : TBody) (he : q = b.key) :
    kin_render_guard q b = some (read_kin b) := by
  simp [kin_render_guard, he]

/-- 多写者结构性修法：地址＝⟨principal, local⟩·可读表只渲染 local 分量（匹配在 principal 分区内）。 -/
structure PAddr where
  principal : String
  loc : String          -- local 分量（`local` 系 Lean 修饰关键字·字段名用 loc）
  deriving Repr

def read_kin_local (b : TBody) (a : PAddr) (_hp : b.key = a.principal ++ "/" ++ a.loc) : ReadKin :=
  ⟨a.loc, b.mass, b.cause, b.t⟩

/-- 分区下可读表对 principal 盲：同一 local·不同 principal ⇒ 渲染逐位相等——oracle 只能枚举自己分区的键。 -/
theorem kin_local_principal_blind (b : TBody) (p p' l : String)
    (hp : b.key = p ++ "/" ++ l) (hp' : b.key = p' ++ "/" ++ l) :
    read_kin_local b ⟨p, l⟩ hp = read_kin_local b ⟨p', l⟩ hp' := by
  simp [read_kin_local]

-- ==== T-1 付费只买元数据 ======================================================

theorem readback_rows_unchanged (s : V3State) (rid : RowId) (cP : Nat) :
    (readback s rid cP).rows = s.rows := by simp [readback]; split <;> rfl

theorem readback_tombs_unchanged (s : V3State) (rid : RowId) (cP : Nat) :
    (readback s rid cP).tombs = s.tombs := by simp [readback]; split <;> rfl

theorem readback_g_unchanged (s : V3State) (rid : RowId) (cP : Nat) :
    (readback s rid cP).g = s.g := by simp [readback]; split <;> rfl

/-- T-1（kimi round5 ①(c)）：付费只能买到元数据——付费回视对状态的写面恰为 (e0, refl)
    （询㶲入 R）；池 (rows)、链 (tombs)、累积器 (g)、D (diss) 全部不动。
    故不存在「用 R 预算换 D 内容」的迁移；接口面亦无 recover 入口（签名级·类型级）。 -/
theorem readback_metadata_only (s : V3State) (rid : RowId) (cP : Nat) :
    (readback s rid cP).rows = s.rows ∧ (readback s rid cP).tombs = s.tombs
      ∧ (readback s rid cP).g = s.g ∧ (readback s rid cP).diss = s.diss
      ∧ (readback s rid cP).phi = s.phi
      ∧ ∃ c, (readback s rid cP).e0 = s.e0 + c ∧ (readback s rid cP).refl = s.refl + c := by
  refine ⟨readback_rows_unchanged s rid cP, readback_tombs_unchanged s rid cP,
          readback_g_unchanged s rid cP, ?_, ?_, ?_⟩
  · simp [readback]; split <;> rfl
  · simp [readback]; split <;> rfl
  · by_cases hb : s.tombs.any (fun p => p.1.id = rid) = true
    · simp only [readback, if_pos hb]; exact ⟨cP, rfl, rfl⟩
    · simp only [readback, if_neg hb]; exact ⟨0, rfl, rfl⟩

-- ==== E4 =====================================================================

theorem chain_link_invariant (prev : Hash) (b : TBody) (h : Hash) (rest : List (TBody × Hash))
    (hok : chain_ok H prev ((b, h) :: rest) = true) :
    b.prev = prev ∧ h = H b ∧ chain_ok H h rest = true := by
  simp only [chain_ok, Bool.and_eq_true, beq_iff_eq] at hok
  exact ⟨hok.1.1, hok.1.2, hok.2⟩

theorem chain_drop_breaks (hinj : ∀ a b, H a = H b → a = b)
    (b₀ b₁ b₂ : TBody) (h₀ h₁ h₂ : Hash)
    (hchain : chain_ok H 0 [(b₀, h₀), (b₁, h₁), (b₂, h₂)] = true)
    (hne0 : b₁ ≠ b₀) :
    chain_ok H 0 [(b₀, h₀), (b₂, h₂)] = false := by
  obtain ⟨h0, h0h, hchain⟩ := chain_link_invariant H 0 b₀ h₀ _ hchain
  obtain ⟨h1, h1h, hchain⟩ := chain_link_invariant H h₀ b₁ h₁ _ hchain
  obtain ⟨h2, h2h, _⟩ := chain_link_invariant H h₁ b₂ h₂ _ hchain
  -- dropping b₁ breaks the link b₀ → b₂: b₂.prev = h₁ = H b₁ ≠ H b₀ = h₀
  have hne : H b₁ ≠ H b₀ := fun he => hne0 (hinj _ _ he)
  have hne' : b₂.prev ≠ h₀ := by rw [h2, h1h, h0h]; exact hne
  have hfalse : (b₂.prev == h₀) = false := by simp [hne']
  have e1 : (b₀.prev == 0) = true := by rw [h0]; exact beq_self_eq_true _
  have e2 : (h₀ == H b₀) = true := by rw [h0h]; exact beq_self_eq_true _
  simp only [chain_ok, e1, e2, hfalse, Bool.true_and, Bool.false_and, Bool.and_false]

-- ==== E5 =====================================================================

theorem sumQ_remove_add (rid : RowId) : ∀ rs : List Row,
    sumQ (remove_id rid rs) + sumQ_id rid rs = sumQ rs := by
  intro rs
  induction rs with
  | nil => simp [remove_id, sumQ_id, sumQ]
  | cons x xs ih =>
    simp only [remove_id, sumQ_id, sumQ, List.foldr_cons] at ih ⊢
    by_cases hx : x.id = rid
    · rw [if_pos hx, if_pos hx]; omega
    · rw [if_neg hx, if_neg hx]; simp only [List.foldr_cons]; omega

theorem sumQ_add (a : Nat) : ∀ l : List Row,
    List.foldr (fun r acc => r.Q + acc) a l = a + sumQ l := by
  intro l
  induction l with
  | nil => simp [sumQ]
  | cons x xs ih => simp only [List.foldr_cons, sumQ, ih]; omega

theorem U_inject (s : V3State) (r : Row) : U (inject s r) = U s + r.Q := by
  show sumQ (s.rows ++ [r]) = sumQ s.rows + r.Q
  simp only [sumQ, List.foldr_append, List.foldr_cons, List.foldr_nil]
  rw [sumQ_add]
  show (r.Q + 0) + sumQ s.rows = sumQ s.rows + r.Q
  omega

theorem U_dissipate (s : V3State) (rid : RowId) (cause : String) (t : Nat) :
    U (dissipate H s rid cause t) = sumQ (remove_id rid s.rows) := by
  simp [U, dissipate]

theorem conserved_inject (s : V3State) (r : Row) (h : Conserved s) : Conserved (inject s r) := by
  show (inject s r).e0 = (inject s r).phi + (inject s r).refl + (inject s r).diss + U (inject s r)
  rw [U_inject]
  show s.e0 + r.Q = s.phi + s.refl + s.diss + (U s + r.Q)
  rw [Conserved] at h
  omega

theorem conserved_dissipate (s : V3State) (rid : RowId) (cause : String) (t : Nat)
    (h : Conserved s) : Conserved (dissipate H s rid cause t) := by
  show (dissipate H s rid cause t).e0 = (dissipate H s rid cause t).phi
      + (dissipate H s rid cause t).refl + (dissipate H s rid cause t).diss + U (dissipate H s rid cause t)
  rw [U_dissipate]
  show s.e0 = s.phi + s.refl + (s.diss + sumQ_id rid s.rows) + sumQ (remove_id rid s.rows)
  rw [Conserved] at h
  simp only [U] at h
  have := sumQ_remove_add rid s.rows
  omega

theorem conserved_readback (s : V3State) (rid : RowId) (cP : Nat) (h : Conserved s) :
    Conserved (readback s rid cP) := by
  by_cases hb : s.tombs.any (fun p => p.1.id = rid) = true
  · simp only [readback, if_pos hb]
    show s.e0 + cP = s.phi + (s.refl + cP) + s.diss + U s
    rw [Conserved] at h; omega
  · simp only [readback, if_neg hb]; exact h

theorem diss_monotone_inject (s : V3State) (r : Row) : (inject s r).diss ≥ s.diss := by
  simp [inject]

theorem diss_monotone_dissipate (s : V3State) (rid : RowId) (cause : String) (t : Nat) :
    (dissipate H s rid cause t).diss ≥ s.diss := by
  simp [dissipate]

theorem diss_monotone_readback (s : V3State) (rid : RowId) (cP : Nat) :
    (readback s rid cP).diss ≥ s.diss := by
  simp only [readback]; split <;> simp

/-- No v3 transition decreases `diss`: the second-law direction anchor of DeposonThermo
    (T6) survives the executor. Together with E1 (no deposited row returns to the pool)
    this is the algorithmic reading of "no `recover` transition". -/
theorem no_recover_shape (s s' : V3State)
    (h : (∃ r, s' = inject s r) ∨ (∃ rid c t, s' = dissipate H s rid c t)
          ∨ (∃ rid c, s' = readback s rid c)) : s'.diss ≥ s.diss := by
  rcases h with ⟨r, rfl⟩ | ⟨rid, c, t, rfl⟩ | ⟨rid, c, rfl⟩
  · exact diss_monotone_inject s r
  · exact diss_monotone_dissipate H s rid c t
  · exact diss_monotone_readback s rid c

-- ---- axiom audit ------------------------------------------------------------

#print axioms remove_id_excludes
#print axioms pool_no_key_after_dissipate
#print axioms tomb_body_indep_of_cipher
#print axioms tombstone_text_blind
#print axioms row_text_derived_fields
#print axioms row_id_indep_of_text
#print axioms dek_commit_indep_of_text
#print axioms mass_is_text_length
#print axioms tomb_not_injective_on_text
#print axioms absorb_monotone
#print axioms absorb_all_monotone
#print axioms absorb_content_blind
#print axioms absorb_all_eq_of_stat_eq
#print axioms absorb_all_count
#print axioms g_monotone_dissipate
#print axioms g_unchanged_inject
#print axioms readback_rows_unchanged
#print axioms readback_tombs_unchanged
#print axioms readback_g_unchanged
#print axioms readback_metadata_only
#print axioms nat_div_mono_left
#print axioms nat_log2_mono
#print axioms nat_max_mono
#print axioms nat_min_mono
#print axioms phantom_budget_bounds
#print axioms phantom_budget_mono
#print axioms phantom_budget_zero_eq_one
#print axioms length_not_invertible
#print axioms chain_ok_tombs_for
#print axioms read_surface_depends_only_on_tombs
#print axioms read_surface_unchanged_by_inject
#print axioms read_surface_unchanged_by_readback
#print axioms read_depends_only_on_body
#print axioms kin_exposes_record_key
#print axioms kout_record_key_blind
#print axioms kout_text_blind
#print axioms render_q_indep_of_stored_key
#print axioms starts_with_is_bool
#print axioms kout_blind_general
#print axioms kin_blind_same_address
#print axioms addr_invariant_under_rewrite
#print axioms row_key_indep_of_text_via_addr
#print axioms kin_exact_no_partial_leak
#print axioms kin_exact_renders
#print axioms kin_local_principal_blind
#print axioms chain_link_invariant
#print axioms chain_drop_breaks
#print axioms sumQ_remove_add
#print axioms sumQ_add
#print axioms U_inject
#print axioms U_dissipate
#print axioms conserved_inject
#print axioms conserved_dissipate
#print axioms conserved_readback
#print axioms diss_monotone_inject
#print axioms diss_monotone_dissipate
#print axioms diss_monotone_readback
#print axioms no_recover_shape

end IrreversibleDeposon
