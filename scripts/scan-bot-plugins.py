#!/usr/bin/env python3
"""扫描 Yunzai / NoneBot 的插件与命令，与上次快照对比并报告变化。

用途：博客《baka86bot 娱乐功能说明》的每日巡检，发现机器人新增插件/命令时提示更新文章。

用法：
  python3 scripts/scan-bot-plugins.py            # 扫描并与快照对比，输出变化报告
  python3 scripts/scan-bot-plugins.py --save     # 扫描后保存为新快照（更新基线）
  python3 scripts/scan-bot-plugins.py --json     # 输出原始扫描 JSON

路径可用环境变量覆盖：
  YUNZAI_PLUGINS   本地 Yunzai 插件目录（默认 /root/Elia-Yunzai/plugins）
  SCAN_SNAPSHOT    快照文件（默认 /root/.cache/blog-bot-scan/snapshot.json）
  SCAN_CREDENTIALS 远端凭据文件（默认 /root/.config/blog-bot-scan/credentials）
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime

YUNZAI_PLUGINS = os.environ.get("YUNZAI_PLUGINS", "/root/Elia-Yunzai/plugins")
SNAPSHOT = os.environ.get("SCAN_SNAPSHOT", "/root/.cache/blog-bot-scan/snapshot.json")
CREDENTIALS = os.environ.get(
    "SCAN_CREDENTIALS", "/root/.config/blog-bot-scan/credentials"
)

SKIP_DIRS = {"node_modules", "data", "__pycache__", ".git", "config"}
TRIGGER_KEY = re.compile(r"\b(reg|rule)\s*:")
CONST_ASSIGN = re.compile(r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=")
IDENT_RE = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
# 正则字面量可能出现的起始位置（前一个非空白字符）
REGEX_PREV = set("=([,:!&|?{};+*%<>~^")


def _skip_string(s: str, i: int) -> int:
    """s[i] 是引号，返回字符串结束后的下标。"""
    q, j = s[i], i + 1
    while j < len(s):
        if s[j] == "\\":
            j += 2
            continue
        if s[j] == q:
            return j + 1
        j += 1
    return len(s)


def _regex_end(s: str, i: int):
    """s[i] == '/'，返回 JS 正则字面量结束位置（含 flags）；不合法返回 None。

    正确处理字符类里的 '/'（如 /[#/]/）与转义 '\\/'。
    """
    j, in_class = i + 1, False
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "\n":
            return None
        if in_class:
            if c == "]":
                in_class = False
        elif c == "[":
            in_class = True
        elif c == "/":
            j += 1
            while j < len(s) and s[j].isalpha():
                j += 1
            return j
        j += 1
    return None


def js_tokens(region: str) -> list[tuple[str, str]]:
    """扫描 JS 片段，产出 ('str'|'re'|'ident', 原文) 三类 token。"""
    out: list[tuple[str, str]] = []
    i, n = 0, len(region)
    while i < n:
        c = region[i]
        if c in "'\"":
            j = _skip_string(region, i)
            out.append(("str", region[i + 1 : j - 1]))
            i = j
        elif c == "/":
            prev = region[:i].rstrip()[-1:]
            if prev in REGEX_PREV or not prev:
                end = _regex_end(region, i)
                if end:
                    out.append(("re", region[i:end]))
                    i = end
                    continue
            i += 1
        elif c in "_$" or c.isascii() and c.isalpha():
            m = IDENT_RE.match(region, i)
            out.append(("ident", m.group(0)))
            i = m.end()
        else:
            i += 1
    return out


def _reg_value_tokens(rest: str) -> list[tuple[str, str]]:
    """取 reg:/rule: 之后的值 token：数组取整个 []，否则只取第一个 token。

    避免把同一行后续 `fnc: 'onSwitchOff'` 之类的字符串误当成触发词。
    """
    s = rest.lstrip()
    if s.startswith("["):
        depth = 0
        for i, ch in enumerate(s):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    return js_tokens(s[: i + 1])
        return js_tokens(s)
    return js_tokens(s)[:1]


# --------------------------------------------------------------------------- #
# 本地 Yunzai
# --------------------------------------------------------------------------- #
def extract_yunzai_triggers(path: str) -> list[str]:
    found: set[str] = set()
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
    except OSError:
        return []
    # 先收集 const XXX = /regex/ 或 'string'，供 reg: XXX 间接引用解析
    consts: dict[str, str] = {}
    for line in text.splitlines():
        m = CONST_ASSIGN.search(line)
        if not m:
            continue
        toks = js_tokens(line[m.end() :])
        if toks and toks[0][0] in ("re", "str"):
            consts[m.group(1)] = toks[0][1]

    for line in text.splitlines():
        key = TRIGGER_KEY.search(line)
        if not key:
            continue
        for kind, val in _reg_value_tokens(line[key.end() :]):
            if kind in ("re", "str"):
                if val.strip():
                    found.add(val.strip())
            elif kind == "ident" and val in consts:
                found.add(consts[val])
    return sorted(found)


def scan_yunzai() -> dict:
    result: dict[str, dict] = {}
    if not os.path.isdir(YUNZAI_PLUGINS):
        return result
    for entry in sorted(os.listdir(YUNZAI_PLUGINS)):
        base = os.path.join(YUNZAI_PLUGINS, entry)
        if not os.path.isdir(base) or entry in SKIP_DIRS or entry.startswith("."):
            continue
        triggers: set[str] = set()
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                if fn.endswith(".js"):
                    triggers.update(extract_yunzai_triggers(os.path.join(root, fn)))

        name = entry
        pkg = os.path.join(base, "package.json")
        if os.path.isfile(pkg):
            try:
                with open(pkg, encoding="utf-8", errors="ignore") as fh:
                    name = json.load(fh).get("name") or entry
            except (OSError, ValueError):
                pass
        result[entry] = {"name": name, "triggers": sorted(triggers)}
    return result


# --------------------------------------------------------------------------- #
# 远端 NoneBot（经 SSH）
# --------------------------------------------------------------------------- #
REMOTE_SCAN = r'''
import json, os, re, subprocess, sys

NB = "/root/nonebot"
out = {"loaded": [], "installed": [], "plugins": {}}

try:
    bot_src = open(os.path.join(NB, "bot.py"), encoding="utf-8", errors="ignore").read()
except OSError as e:
    print(json.dumps({"error": f"无法读取 bot.py: {e}"}))
    sys.exit(0)

out["loaded"] = re.findall(r"load_plugin\(\s*[\"']([^\"']+)[\"']", bot_src)
out["loaded"] = sorted(dict.fromkeys(out["loaded"]))

sp = ""
try:
    r = subprocess.run(
        ["find", NB, "-maxdepth", "4", "-name", "site-packages", "-type", "d"],
        capture_output=True, text=True, timeout=30,
    )
    sp = (r.stdout.splitlines() or [""])[0].strip()
except Exception:
    pass
out["site_packages"] = sp

if sp and os.path.isdir(sp):
    out["installed"] = sorted(
        d for d in os.listdir(sp)
        if d.startswith("nonebot_plugin_")
        and not d.endswith(".dist-info")
        and os.path.isdir(os.path.join(sp, d))
    )

CMD_PATTERNS = [
    r"on_command\(\s*[\"']([^\"']+)[\"']",
    r"on_keyword\(\s*[\"']([^\"']+)[\"']",
    r"on_fullmatch\(\s*[\"']([^\"']+)[\"']",
    r"on_startswith\(\s*[\"']([^\"']+)[\"']",
    r"Alconna\(\s*[\"']([^\"']+)[\"']",
    r"Command\(\s*[\"']([^\"']+)[\"']",
]
TS_PATTERNS = [
    r"on_startswith\(\s*(?:msg\s*=\s*)?\(([^)]*)\)",
    r"on_fullmatch\(\s*(?:msg\s*=\s*)?\(([^)]*)\)",
    r"on_keyword\(\s*(?:msg\s*=\s*)?\(([^)]*)\)",
]
LIT = re.compile(r"""['"]([^'"]+)['"]""")

def _collect(target):
    cmds = set()
    files = []
    if os.path.isdir(target):
        for root, dirs, fs in os.walk(target):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            files += [os.path.join(root, f) for f in fs if f.endswith(".py")]
    elif os.path.isfile(target):
        files = [target]
    for path in files:
        try:
            src = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for pat in CMD_PATTERNS:
            cmds.update(re.findall(pat, src))
        for pat in TS_PATTERNS:
            for grp in re.findall(pat, src):
                cmds.update(LIT.findall(grp))
    return sorted(c for c in cmds if c.strip())

out["missing"] = []
for plugin in out["loaded"]:
    alt = plugin.replace("-", "_")
    cands = []
    for base in (sp, NB):
        if not base:
            continue
        for name in (plugin, alt):
            cands += [os.path.join(base, name), os.path.join(base, name + ".py")]
    found = next((c for c in cands if os.path.exists(c)), None)
    out["plugins"][plugin] = {"triggers": _collect(found) if found else []}
    if not found:
        out["missing"].append(plugin)

out["missing"] = sorted(out["missing"])

print(json.dumps(out, ensure_ascii=False))
'''


def load_credentials() -> dict:
    creds: dict[str, str] = {}
    if os.path.isfile(CREDENTIALS):
        with open(CREDENTIALS, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip()
    for k, env in (
        ("SSH_HOST", "SCAN_SSH_HOST"),
        ("SSH_PORT", "SCAN_SSH_PORT"),
        ("SSH_USER", "SCAN_SSH_USER"),
        ("SSH_PASS", "SCAN_SSH_PASS"),
    ):
        if os.environ.get(env):
            creds[k] = os.environ[env]
    return creds


def scan_nonebot() -> dict:
    creds = load_credentials()
    if not creds.get("SSH_HOST") or not creds.get("SSH_PASS"):
        return {"error": "缺少远端凭据（SSH_HOST / SSH_PASS）"}
    env = dict(os.environ, SSHPASS=creds["SSH_PASS"])
    cmd = [
        "sshpass", "-e", "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=20",
        "-p", creds.get("SSH_PORT", "22"),
        f"{creds.get('SSH_USER', 'root')}@{creds['SSH_HOST']}",
        "python3", "-",
    ]
    try:
        proc = subprocess.run(
            cmd, input=REMOTE_SCAN, capture_output=True, text=True, timeout=120, env=env
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return {"error": f"SSH 失败: {exc}"}
    if proc.returncode != 0:
        msg = (proc.stderr or "").strip().splitlines()
        return {"error": f"SSH 返回 {proc.returncode}: {msg[-1] if msg else 'unknown'}"}
    for line in reversed(proc.stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except ValueError:
                continue
    return {"error": "远端未返回可解析的 JSON"}


# --------------------------------------------------------------------------- #
# 对比与报告
# --------------------------------------------------------------------------- #
def diff_side(old: dict, new: dict) -> dict:
    old_keys, new_keys = set(old), set(new)
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed: dict[str, dict[str, list[str]]] = {}
    for key in sorted(old_keys & new_keys):
        o = set(old[key].get("triggers") or [])
        n = set(new[key].get("triggers") or [])
        delta, gone = sorted(n - o), sorted(o - n)
        if delta or gone:
            changed[key] = {"added": delta, "removed": gone}
    return {"added": added, "removed": removed, "changed": changed}


def build_report(old: dict | None, new: dict) -> str:
    lines: list[str] = []
    meta = new.get("meta") or {}

    if not old:
        lines.append("首次运行：已建立基线快照，无对比数据。")
    else:
        for label, key in (("Yunzai", "yunzai"), ("NoneBot", "nonebot")):
            if meta.get(f"{key}_error"):
                lines.append(f"[{label}] 扫描失败，跳过对比")
                continue
            o = old.get(key) or {}
            n = new.get(key) or {}
            d = diff_side(o, n)
            lines.append(f"[{label}] 插件 {len(n)} 个")
            if d["added"]:
                lines.append(f"  + 新插件：{', '.join(d['added'])}")
            if d["removed"]:
                lines.append(f"  - 移除插件：{', '.join(d['removed'])}")
            for name, delta in d["changed"].items():
                for label_, cmds in (("新增", delta["added"]), ("移除", delta["removed"])):
                    if not cmds:
                        continue
                    shown = ", ".join(cmds[:12])
                    more = f" …(+{len(cmds) - 12})" if len(cmds) > 12 else ""
                    lines.append(f"  ~ {name} {label_}触发命令：{shown}{more}")
            if not (d["added"] or d["removed"] or d["changed"]):
                lines.append("  （无变化）")

    for label, key in (("Yunzai", "yunzai"), ("NoneBot", "nonebot")):
        err = meta.get(f"{key}_error")
        if err:
            lines.append(f"⚠️ {label} 扫描失败：{err}")

    loaded = meta.get("nonebot_loaded") or []
    installed = meta.get("nonebot_installed") or []
    missing = meta.get("nonebot_missing") or []
    if missing:
        lines.append(f"⚠️ [NoneBot] bot.py 里 load 了但找不到源码（可能加载失败）：{', '.join(missing)}")
    if installed:
        not_loaded = sorted(set(installed) - set(loaded))
        if not_loaded:
            lines.append(f"[NoneBot] 已安装但未加载（不计入变化）：{', '.join(not_loaded)}")

    return "\n".join(lines)


def scan_all() -> dict:
    nb = scan_nonebot()
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "yunzai": scan_yunzai(),
        "nonebot": nb.get("plugins") or {},
        "meta": {
            "nonebot_loaded": nb.get("loaded") or [],
            "nonebot_missing": nb.get("missing") or [],
            "nonebot_installed": nb.get("installed") or [],
            "nonebot_site_packages": nb.get("site_packages") or "",
            "nonebot_error": nb.get("error"),
        },
    }


def load_snapshot() -> dict | None:
    if not os.path.isfile(SNAPSHOT):
        return None
    try:
        with open(SNAPSHOT, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def save_snapshot(data: dict) -> None:
    os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
    tmp = SNAPSHOT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, SNAPSHOT)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--save", action="store_true", help="保存为新快照（更新基线）")
    ap.add_argument("--json", action="store_true", help="输出原始扫描 JSON")
    args = ap.parse_args()

    old = load_snapshot()
    new = scan_all()

    if args.json:
        print(json.dumps(new, ensure_ascii=False, indent=2))
    else:
        print(build_report(old, new))

    if args.save or old is None:
        save_snapshot(new)
        if not args.json:
            print(f"\n快照已保存：{SNAPSHOT}")

    # 退出码：0 = 无变化或已建基线，10 = 有变化（便于上层判断）
    if old is None:
        return 0
    meta = new.get("meta") or {}
    has_change = False
    for key in ("yunzai", "nonebot"):
        if meta.get(f"{key}_error"):
            continue
        d = diff_side(old.get(key) or {}, new.get(key) or {})
        if d["added"] or d["changed"]:
            has_change = True
    return 10 if has_change else 0


if __name__ == "__main__":
    sys.exit(main())
