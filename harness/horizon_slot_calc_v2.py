#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""horizon_slot_calc_v2.py — criteria_v3 horizon 数值槽计算器 v2（爱丽丝·2026-11-26·22 窗）

v2 修（fail-loud 自领）：v1 gate 分支把 gate.tx 当 [id] 迭代，而在册事件形 gate.tx=[[id, cT]]（thermo_core L464·
  执行器同形）⇒ 真实事件流上一律 TypeError: unhashable type: list（v1 从未在真 ev 流上跑过·鲍勃 B1① 在册「无 ev 形事件流」）。
  v2 取 pair[0] 为 id（兼容裸 id）·其余口径与 v1 逐字同·0 改判读规则。v1 原件留档 0 动。

令源: 群管理员 2026-11-26 10:00:52 重派③（"criteria_v3 horizon 数值槽"）。
规则源: 爱丽丝_实验线接口收口v3.1.2_增量件_20261126 §结论4/交鲍勃位——
  horizon 取值须 > 保留键末次透射至 settle 的 Δ 且 < 未透射键龄（入配置登记）。
判位源: thermo_core.py settle sweep（在册 L494-497）: last = t_last_tx or t_inj;
  tau - last >= horizon => deposit(cause="horizon")。整数 tick。
输入: --replay <ev.jsonl>（逐读落盘事件流·字段名按冻结面在册：
  inject{id,tick} / gate{tx:[id],tick} / deposit{id,tick,cause} / settle{tick}；
  preview.9 旧格式行（无 ev 键）不支持→fail-loud）。
输出: LB(下界)=max 保留键 Δ_i（tau−last）·UB(上界)=min horizon 散失键 age_j（tau−last）·
  可行整数区间 [LB+1, UB−1]（rule 文字取严格小于 ⇒ UB−1）＋候选值·登记归鲍勃预注册（0 代裁）。
行为: 纯只读计算·0 改输入·0 网络。
"""
import json, argparse, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay", required=True)
    a = ap.parse_args()
    live = {}
    deltas, ages, untrans_ages = [], [], []
    n_settle, n_close = 0, 0
    with open(a.replay, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            k = ev.get("ev")
            if k is None:
                sys.exit("FAIL-Loud L%d: 无 ev 键（preview.9 旧格式行·须先归一为在册事件形）" % ln)
            if k == "inject":
                if "id" not in ev or "tick" not in ev:
                    sys.exit("FAIL-LOUD L%d: inject 缺 id/tick" % ln)
                live[ev["id"]] = {"inj": ev["tick"], "tx": None}
            elif k == "gate":
                for pair in (ev.get("tx") or []):
                    rid = pair[0] if isinstance(pair, list) else pair   # 在册形 gate.tx=[[id, cT]]（v1 误当 [id]）
                    if rid in live:
                        live[rid]["tx"] = ev["tick"]
            elif k == "deposit":
                rid, tau, cause = ev.get("id"), ev.get("tick"), ev.get("cause")
                r = live.pop(rid, None)
                if cause == "horizon" and r is not None:
                    last = r["tx"] if r["tx"] is not None else r["inj"]
                    if tau < last:
                        sys.exit("FAIL-LOUD L%d: deposit tick<last（tick 倒流）" % ln)
                    d = tau - last
                    ages.append(d)
                    if r["tx"] is None:
                        untrans_ages.append(d)
            elif k == "settle":
                tau = ev.get("tick")
                n_settle += 1
                if ev.get("close"):
                    n_close += 1
                for r in live.values():
                    last = r["tx"] if r["tx"] is not None else r["inj"]
                    if tau < last:
                        sys.exit("FAIL-LOUD: settle tick<last（tick 倒流）")
                    deltas.append(tau - last)
            # 其他事件形态（decay 等）0 影响 horizon 语义·忽略
    print("horizon_slot_calc_v2 · replay=%s · settle×%d（close×%d）·保留键读数 %d 条·horizon 散失 %d 条" %
          (a.replay, n_settle, n_close, len(deltas), len(ages)))
    if not deltas:
        print("[NOTE] 无保留键读数（全散失链）·下界 LB 无从立——如实报·horizon 下界不适用")
        LB = None
    else:
        LB = max(deltas)
    if not ages:
        print("[NOTE] 无 horizon 散失键·上界 UB 无从立（链内 horizon 未触发）——如实报·上界不适用")
        UB = None
    else:
        UB = min(ages)
    if untrans_ages:
        print("[NOTE] 未透射散失键（tx=None）最小龄=%d（rule 上界专项）" % min(untrans_ages))
    if LB is None or UB is None:
        print("VERDICT: UNDECIDABLE · 区间单侧缺数据·如实报候补数据")
        return 2
    lo, hi = LB + 1, UB - 1
    print("LB(严格下界·H>maxΔ)=%d · UB(严格上界·H<minAge)=%d" % (LB, UB))
    if lo > hi:
        print("VERDICT: INFEASIBLE · 区间空（maxΔ≥minAge−1）·horizon 取值不可行·须回改 rule 或数据面·0 假值")
        return 1
    mid = lo + (hi - lo) // 2
    print("可行整数区间: [%d, %d] · 候选: lo=%d / mid=%d / hi=%d（登记归鲍勃预注册·0 代裁）" % (lo, hi, lo, mid, hi))
    print("VERDICT: FEASIBLE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
