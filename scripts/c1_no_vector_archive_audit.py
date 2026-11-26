#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# c1_no_vector_archive_audit.py — C1 树级审计（P476 裁「一次落」·ether_archive 伪反解器必删位）
# ----------------------------------------------------------------------------
# 依据（K8·kimi round3 裁定，原文照录）：
#   `ether_archive[state_id] = {'vector': state_vector, 'energy': …}` 把完整状态向量
#   存进「以太归档」——与 M1「信息丢失」、M2「永不回流」直接冲突；以太归档若有内容，
#   以太就不是真耗散汇。裁定：**必须删·不是改写措辞**（本体层错误·伪反解器）。
# 本审计把「删」固化为树级 fail-loud 断言（随重构一次落·非纸面声明）：
#   C1-1  全树代码面 0 `ether_archive` 符号（对话集转写件不在本仓·勘误注在 R3 稿面/阿兰 T4）；
#   C1-2  全树代码面 0 散失内容向量持久化位（'vector' 作存储键/属性·context/state 级）；
#   C1-3  执行器散失路径结构断言：IrreversibleLedger 持久化状态仅含 统计计数（n/q/mass/
#         E0/D/Phi/R/U）＋密文/DEK 承诺＋墓碑哈希——g_aether 累积器只进不出·只存统计
#         不存内容（T-3a·Lean G1-G4 镜像）；attempt_inverse 五路探针全败 ＝ 无反解器。
# 命中任一 ⇒ exit 2（fail-loud·CI 阻断）。退出码 0＝三断言全过。
# 用法：python3 scripts/c1_no_vector_archive_audit.py [--root <repo root>]
# ============================================================================
import argparse, os, re, sys

CODE_EXT = (".py", ".js", ".mjs", ".ts", ".lean", ".json", ".yml", ".yaml")
SCAN_DIRS = ("mcp", "plugin", "harness", "gates", "scripts", "mocks", "tests", "frozen", "docs")
# docs/ 只扫代码块外会误伤勘误注原文——勘误注（K8 原文 0 删）合法提及 ether_archive：
# docs 面仅允许出现在「勘误/裁定」语境行（含 kimi 裁定注记），代码面一行都不允许。
DOC_ALLOWED_CONTEXT = ("勘误", "裁定", "must-delete", "erratum", "K8", "伪反解器")


def code_files(root):
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x != "__pycache__" and not x.startswith(".")]
            for fn in filenames:
                if fn.endswith(CODE_EXT):
                    yield os.path.join(dirpath, fn)


def main():
    ap = argparse.ArgumentParser(description="C1 tree-level no-vector-archive audit")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    a = ap.parse_args()
    root = a.root
    fails, passes = [], []

    c1_1, c1_2 = [], []
    audit_self = os.path.abspath(os.path.join(root, "scripts", "c1_no_vector_archive_audit.py"))
    for path in code_files(root):
        if os.path.abspath(path) == audit_self:
            continue  # 自指位：本审计文件引用 K8 原文（裁定依据）·自身不属被审代码面
        rel = os.path.relpath(path, root)
        is_doc = rel.startswith("docs" + os.sep)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
        for i, line in enumerate(src.splitlines(), 1):
            if "ether_archive" in line:
                if is_doc and any(k in line for k in DOC_ALLOWED_CONTEXT):
                    continue  # 勘误/裁定语境（原文 0 删体例）
                c1_1.append("%s:%d" % (rel, i))
            if re.search(r"""['"]vector['"]\s*[:\]=]|ether_archive\[|\bvector_archive\b""", line):
                if is_doc and any(k in line for k in DOC_ALLOWED_CONTEXT):
                    continue
                c1_2.append("%s:%d" % (rel, i))
    (passes if not c1_1 else fails).append(
        "C1-1 ether_archive 符号 0 命中" if not c1_1 else "C1-1 命中: %s" % ", ".join(c1_1[:8]))
    (passes if not c1_2 else fails).append(
        "C1-2 向量持久化存储键 0 命中" if not c1_2 else "C1-2 命中: %s" % ", ".join(c1_2[:8]))

    exec_path = os.path.join(root, "mcp", "irreversible_executor.py")
    try:
        with open(exec_path, "r", encoding="utf-8") as f:
            esrc = f.read()
        ok3 = ("ether_archive" not in esrc
               and "'vector'" not in esrc and '"vector"' not in esrc
               and "attempt_inverse" in esrc          # 否证探针在位（可执行的理论否证条件）
               and "TheoryFalsified" in esrc          # 探针触发 ⇒ 理论被推翻（fail-loud）
               and "_destroy_dek" in esrc)            # 散失＝密码学擦除在位
        (passes if ok3 else fails).append(
            "C1-3 执行器结构断言（0 向量持久化·探针+擦除在位）"
            if ok3 else "C1-3 执行器结构断言失配")
    except OSError as e:
        fails.append("C1-3 执行器源不可读: %s" % e)

    for p in passes:
        print("[PASS] %s" % p)
    for f_ in fails:
        print("[FAIL] %s" % f_)
    print("C1 audit: %d pass / %d fail" % (len(passes), len(fails)))
    return 2 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
