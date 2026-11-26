# -*- coding: utf-8 -*-
# ============================================================================
# executor_config.py — 执行器层参数共享面（I-3b · preview.12）
# ----------------------------------------------------------------------------
# mcp_server.py 与 thermo_cli.py 同源（消 #10 不对称：CLI 执行器重放原用
# tc.load_cfg()，服务端用 _exec_cfg()——env 设执行器层键时两端口径不一）。
# 数值面沿 DEPOSON_THERMO（thermo_core.load_cfg · 冻结面白名单 0 动）＋执行器层键
# env 感知（D17/D23/D24 · env override wins）。0 新依赖（标准库 + thermo_core）。
# ============================================================================
import os

import thermo_core as tc


def exec_cfg():
    """执行器层参数：数值面沿 DEPOSON_THERMO（tc.load_cfg·冻结面）＋执行器层键沿
    DEPOSON_G_POLICY/DEPOSON_Q_REF/DEPOSON_MASS_BUCKET/DEPOSON_PHANTOM_FORM/
    DEPOSON_KIN_SCOPE/DEPOSON_ADDR_SCHEMA/DEPOSON_PRINCIPAL（D17/D23/D24·env override wins）。"""
    c = dict(tc.load_cfg())
    c["g_policy"] = os.environ.get("DEPOSON_G_POLICY", "p1")
    c["phantom_form"] = os.environ.get("DEPOSON_PHANTOM_FORM", "kout")
    c["kin_scope"] = os.environ.get("DEPOSON_KIN_SCOPE", "multi")
    c["addr_schema"] = os.environ.get("DEPOSON_ADDR_SCHEMA", "1") not in ("0", "false", "no")
    c["mass_bucket"] = os.environ.get("DEPOSON_MASS_BUCKET", "0") in ("1", "true", "yes")
    q_ref = os.environ.get("DEPOSON_Q_REF")
    if q_ref:
        c["Q_ref"] = max(1, int(q_ref))
    principal = os.environ.get("DEPOSON_PRINCIPAL")
    if principal:
        c["principal"] = principal
    return c
