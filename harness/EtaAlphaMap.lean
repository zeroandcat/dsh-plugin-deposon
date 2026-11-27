/-!
# EtaAlphaMap.lean — machine-checked structure of the (η,α)→(c_T,c_A) gate-price map

Companion to the Q-6 mapping definition (查理 2026-11-27 v2, kimi round15 revised;
Python twin: 鲍勃 `eta_alpha_map.py` N5 `0e063164f06ab066`) and to the C5 candidate
claim "the executor neighbourhood ⊆ the manuscript §5 positive region" (PI 12:36
verdict: design-round). This file formalises the algebra and the two verdict-shaped
propositions WITHOUT adjudicating — 0 代裁, conclusions go to PI.

Discipline: core-only, no mathlib, no `sorry`; everything over ℕ (same discipline
as `IrreversibleDeposon.lean` — integer exergy). η ("Ratio, not magnitude", 稿面
§2.2 verbatim) is encoded as a ratio PAIR `(num, den)` over ℕ with `den > 0`;
α is the local working symbol (α ≜ g_couple per the registered declaration).
The κ anchors normalise to 1 at the reference point, so the map specialises to
`c_T = α`, `c_A = η·α` — defined on the divisibility grid `den ∣ num·α` (the sweep
grids are finite integer grids; the map is a unified account-price proxy, not a
pointwise instantiation — the pointwise gap is registered upstream).

E-series proved here:

  E1  `ref_point_reproduces`       — the arbitrary reference (η_ref, α_ref) = (1/2, 20)
                                     maps to the frozen baseline (c_T, c_A) = (20, 10)
                                     (κ_T = κ_A = 1, decide-level; the anchors carry no
                                     source-face physical assertion — the anti-claim of
                                     kimi round15 ④ is structural here).
  E2  `cT_pos` / `cA_pos`          — on the grid the map lands in the positive quadrant.
  E3  `eta_le_one_iff`             — η ≤ 1 ⟺ c_A ≤ c_T on the grid (ratio semantics via
                                     cross-multiplication with den ∣ num·α, α > 0).
  E4  `inverse_roundtrip`          — reading (c_T, c_A) back as the ratio pair
                                     (η', α') = (c_A/c_T, c_T) and re-applying the map
                                     returns the same point (grid trivial: c_T ∣ c_A·c_T).
  E5  `defaults_point`             — executor DEFAULTS (c_T, c_A) = (100, 10) read back
                                     as (η, α) = (1/10, 100), decide-level anchor.
  E6  `full_domain_not_subset`     — C5 as a GENERAL claim over the full executor
                                     parameter domain is FALSE: (c_T, c_A) = (10, 100)
                                     is in the domain yet violates η ≤ 1. Formal face of
                                     "the coverage claim does not follow from the map
                                     alone" (查理 §六.3 / kimi round15 汇总位).
  E7  `capped_neighborhood_subset` — C5 holds for any neighbourhood whose grid
                                     definition carries the ratio cap; the implication is
                                     tautological BY CONSTRUCTION of PositiveRegion —
                                     exactly the design-round decision point: whether the
                                     sweep-grid definition includes the cap is the
                                     PI-side verdict (0 代裁 here).
  E8  `kappa_anchors_normalise`    — the anchor arithmetic (20/20 = 1, 10/(1·20/2) = 1).

The two register sentences of the definition file (anti-overclaim + α local-symbol
declaration) apply here mutatis mutandis: nothing in this file measures, controls,
or asserts monotone proxies for (g_couple, g_aether), γ_aether/Γ_aether, or
|t|²/|r|²/|a|². Frozen face (c_P, phantom_ttl, phantom_k, Q_ref, g_policy) appears
nowhere below.
-/

/-- Executor-side account-price pair `(c_T, c_A)`. -/
def ExecutorPoint := Nat × Nat

/-- The manuscript §5 positive region, executor image under the κ = 1 localisation:
    η ≤ 1 (ratio cap: c_A ≤ c_T) ∧ g_aether > 0 (c_A > 0). -/
def PositiveRegion (p : ExecutorPoint) : Prop :=
  p.2 ≤ p.1 ∧ 0 < p.2

/-- The full executor parameter domain: both prices positive, nothing else. -/
def FullDomain (p : ExecutorPoint) : Prop :=
  0 < p.1 ∧ 0 < p.2

/-- The (η,α)→(c_T,c_A) map at κ_T = κ_A = 1 (arbitrary-reference normalisation):
    `c_T = α`, `c_A = num·α/den` with η = num/den; defined on the divisibility grid. -/
def execPoint (alpha num den : Nat) (_h : den ∣ num * alpha) : ExecutorPoint :=
  (alpha, num * alpha / den)

/-- Grid discipline: on the grid, the ratio denominator is positive. -/
theorem grid_den_pos {alpha num den : Nat} (hnum : 0 < num) (hα : 0 < alpha)
    (h : den ∣ num * alpha) : 0 < den := by
  rcases Nat.eq_zero_or_pos den with h0 | hp
  · exfalso
    obtain ⟨k, hk⟩ := h
    rw [h0, Nat.zero_mul] at hk
    rcases Nat.mul_eq_zero.mp hk with h' | h'
    · omega
    · omega
  · exact hp

/-- E1: the arbitrary reference point reproduces the frozen baseline. -/
theorem ref_point_reproduces :
    execPoint 20 1 2 (by decide) = (20, 10) := by
  simp [execPoint]

/-- E2a: on the grid, c_T = α > 0 whenever α > 0. -/
theorem cT_pos {alpha num den : Nat} (hα : 0 < alpha) (h : den ∣ num * alpha) :
    0 < (execPoint alpha num den h).1 := hα

/-- E2b: on the grid, c_A = num·α/den > 0 whenever num > 0 and α > 0. -/
theorem cA_pos {alpha num den : Nat} (hnum : 0 < num) (hα : 0 < alpha)
    (h : den ∣ num * alpha) : 0 < (execPoint alpha num den h).2 := by
  have hd := grid_den_pos hnum hα h
  obtain ⟨k, hk⟩ := h
  have hk0 : 0 < k := by
    rcases Nat.eq_zero_or_pos k with h0 | hp
    · rw [h0, Nat.mul_zero] at hk
      rcases Nat.mul_eq_zero.mp hk with h' | h'
      · omega
      · omega
    · exact hp
  have hdiv : num * alpha / den = k := by
    rw [hk]; exact Nat.mul_div_cancel_left _ hd
  show 0 < num * alpha / den
  rw [hdiv]; exact hk0

/-- E3: on the grid, η ≤ 1 ⟺ c_A ≤ c_T — the ratio semantics of "η ≤ 1". -/
theorem eta_le_one_iff {alpha num den : Nat} (hnum : 0 < num) (hα : 0 < alpha)
    (h : den ∣ num * alpha) :
    (execPoint alpha num den h).2 ≤ (execPoint alpha num den h).1 ↔ num ≤ den := by
  have hd := grid_den_pos hnum hα h
  obtain ⟨k, hk⟩ := h
  have hdiv : num * alpha / den = k := by
    rw [hk]; exact Nat.mul_div_cancel_left _ hd
  show num * alpha / den ≤ alpha ↔ num ≤ den
  constructor
  · intro hle
    rw [hdiv] at hle                       -- k ≤ α
    have h1 : den * k ≤ den * alpha := Nat.mul_le_mul_left _ hle
    rw [← hk] at h1                        -- num·α ≤ den·α
    rw [Nat.mul_comm num alpha, Nat.mul_comm den alpha] at h1
    exact Nat.le_of_mul_le_mul_left h1 hα
  · intro hle
    have h1 : num * alpha ≤ den * alpha := Nat.mul_le_mul_right _ hle
    rw [hk] at h1                          -- den·k ≤ den·α
    have h3 : k ≤ alpha := Nat.le_of_mul_le_mul_left h1 hd
    rw [hdiv]; exact h3

/-- E4: round trip — reading (c_T, c_A) back as (η', α') = (c_A/c_T, c_T) and
    re-applying the map returns the same point (grid-side trivially well-defined:
    c_T ∣ c_A·c_T). -/
theorem inverse_roundtrip {alpha num den : Nat} (hα : 0 < alpha)
    (_h : den ∣ num * alpha) :
    execPoint alpha (num * alpha / den) alpha
        (Nat.dvd_mul_left alpha (num * alpha / den)) =
      (alpha, num * alpha / den) := by
  have h1 : (num * alpha / den) * alpha / alpha = num * alpha / den := by
    rw [Nat.mul_comm (num * alpha / den) alpha]
    exact Nat.mul_div_cancel_left (num * alpha / den) hα
  show (alpha, (num * alpha / den) * alpha / alpha) = (alpha, num * alpha / den)
  rw [h1]

/-- E5: executor DEFAULTS (c_T, c_A) = (100, 10) read back as (η, α) = (1/10, 100). -/
theorem defaults_point :
    execPoint 100 1 10 (by decide) = (100, 10) := by
  simp [execPoint]

/-- E6: C5 as a general claim over the full executor domain is FALSE — the
    counterpoint (c_T, c_A) = (10, 100) sits in the full domain yet violates
    the positive region. Formal face of "not automatic from the map alone". -/
theorem full_domain_not_subset :
    ∃ p, FullDomain p ∧ ¬ PositiveRegion p :=
  ⟨(10, 100),
    ⟨Nat.succ_pos 9, Nat.succ_pos 99⟩,
    fun h => absurd h.1 (by decide)⟩

/-- E7: C5 holds for any neighbourhood whose grid definition carries the ratio cap —
    the implication is tautological BY CONSTRUCTION of PositiveRegion, which is exactly
    the design-round decision point (whether the sweep-grid definition includes the cap
    is the PI-side verdict; 0 代裁 here). -/
theorem capped_neighborhood_subset {S : ExecutorPoint → Prop}
    (hS : ∀ p, S p → p.2 ≤ p.1 ∧ 0 < p.2) :
    ∀ p, S p → PositiveRegion p :=
  fun p hp => hS p hp

/-- E8: the κ anchor arithmetic at the arbitrary reference. -/
theorem kappa_anchors_normalise :
    (20 : Nat) / 20 = 1 ∧ 10 / (1 * 20 / 2) = 1 := by
  exact ⟨by decide, by decide⟩

/-! Verification aids: axiom disclosure (0 sorry discipline; expected ⊆ {propext}). -/

#print axioms grid_den_pos
#print axioms ref_point_reproduces
#print axioms cT_pos
#print axioms cA_pos
#print axioms eta_le_one_iff
#print axioms inverse_roundtrip
#print axioms defaults_point
#print axioms full_domain_not_subset
#print axioms capped_neighborhood_subset
#print axioms kappa_anchors_normalise
