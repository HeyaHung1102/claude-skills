#!/usr/bin/env python3
"""git-loops: 盤點並安全同步散落在多台機器上的 GitHub repo。

用法:
    python3 git_loops.py scan [--fetch] [--out report.md]
    python3 git_loops.py sync [--fetch] [--out report.md]

scan 唯讀；sync 只對「乾淨且落後遠端」的副本做 git pull --ff-only，
其餘一律回報請人處理（dirty、需 push、分岔、重複副本都不自動動手）。
"""
import argparse
import datetime
import json
import platform
import socket
import subprocess
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "machines.json"


def run_git(repo: Path, *args, timeout=30):
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"


def find_clones(repo_name: str, roots: list[Path]) -> list[Path]:
    """在各搜尋根目錄下找名字符合的 git repo（最多往下兩層，避免掃整顆硬碟）。"""
    hits = []
    for root in roots:
        if not root.exists():
            continue
        candidates = [root / repo_name]
        try:
            candidates += [d / repo_name for d in root.iterdir() if d.is_dir() and not d.name.startswith(".")]
        except PermissionError:
            continue
        for c in candidates:
            if (c / ".git").exists() and c not in hits:
                hits.append(c)
    return hits


def inspect(repo: Path, do_fetch: bool) -> dict:
    info = {"path": str(repo)}
    _, info["branch"], _ = run_git(repo, "branch", "--show-current")
    _, remote, _ = run_git(repo, "remote", "get-url", "origin")
    info["remote"] = remote or "(無 origin)"
    _, status, _ = run_git(repo, "status", "--porcelain")
    lines = [l for l in status.splitlines() if l]
    info["untracked"] = sum(1 for l in lines if l.startswith("??"))
    info["dirty"] = len(lines) - info["untracked"]
    _, last, _ = run_git(repo, "log", "-1", "--format=%h %ad %s", "--date=short")
    info["last_commit"] = last or "(無 commit)"
    if do_fetch and remote:
        code, _, err = run_git(repo, "fetch", "--quiet", timeout=60)
        info["fetched"] = (code == 0) or f"fetch 失敗: {err}"
    code, counts, _ = run_git(repo, "rev-list", "--left-right", "--count", "HEAD...@{upstream}")
    if code == 0 and counts:
        ahead, behind = counts.split()
        info["ahead"], info["behind"] = int(ahead), int(behind)
    else:
        info["ahead"] = info["behind"] = None  # 沒有 upstream
    return info


def classify(info: dict) -> tuple[str, str]:
    """回傳 (狀態標籤, 需要的人工動作)。"""
    if info["dirty"] or info["untracked"]:
        return ("dirty", f"有 {info['dirty']} 個修改 + {info['untracked']} 個 untracked，需人工 commit 或清理")
    if info["ahead"] is None:
        return ("no-upstream", "branch 沒有對應的遠端追蹤分支，需人工確認")
    if info["ahead"] and info["behind"]:
        return ("diverged", f"與遠端分岔（領先 {info['ahead']}、落後 {info['behind']}），需人工 merge/rebase")
    if info["ahead"]:
        return ("ahead", f"領先遠端 {info['ahead']} 個 commit，待 push")
    if info["behind"]:
        return ("behind", f"落後遠端 {info['behind']} 個 commit，可 ff-pull")
    return ("clean", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["scan", "sync"])
    ap.add_argument("--fetch", action="store_true", help="先 git fetch 再比 ahead/behind")
    ap.add_argument("--out", help="同時把報告寫到這個 Markdown 檔")
    args = ap.parse_args()

    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    hostname = socket.gethostname().split(".")[0]
    machine = cfg["machines"].get(hostname)
    if machine is None:
        print(f"設定檔裡沒有這台機器：hostname = {hostname}")
        print(f"請把它加進 {CONFIG_PATH}（machines 底下），並填入 search_roots。")
        sys.exit(1)

    roots = [Path(p).expanduser() for p in machine["search_roots"]]
    today = datetime.date.today().isoformat()
    lines = [f"# git-loops 巡邏報告 — {hostname} {today}",
             f"模式：{args.mode}{'（含 fetch）' if args.fetch else '（未 fetch，ahead/behind 以本地快取為準）'}",
             "", "## 總覽", "",
             "| repo | 路徑 | branch | 狀態 | ahead/behind | 最後 commit |",
             "|---|---|---|---|---|---|"]
    manual, synced = [], []

    for name in cfg["repos"]:
        clones = find_clones(name, roots)
        if not clones:
            lines.append(f"| {name} | — | — | **缺席** | — | — |")
            manual.append(f"**{name}**：這台機器上找不到，需 clone 或確認只存在於其他機器")
            continue
        if len(clones) > 1:
            manual.append(f"**{name}**：發現 {len(clones)} 份副本（{', '.join(str(c) for c in clones)}），需人工決定正本")
        for c in clones:
            info = inspect(c, args.fetch)
            tag, action = classify(info)
            ab = "—" if info["ahead"] is None else f"+{info['ahead']}/-{info['behind']}"
            lines.append(f"| {name} | {c} | {info['branch']} | {tag} | {ab} | {info['last_commit']} |")
            if action:
                manual.append(f"**{name}** `{c}`：{action}")
            if args.mode == "sync" and tag == "behind" and len(clones) == 1:
                code, out, err = run_git(c, "pull", "--ff-only", timeout=120)
                if code == 0:
                    synced.append(f"**{name}** `{c}`：ff-pull 成功（{info['behind']} 個 commit）")
                else:
                    manual.append(f"**{name}** `{c}`：ff-pull 失敗，{err}")

    lines += ["", "## 需要人工處理", ""]
    lines += [f"- {m}" for m in manual] if manual else ["- 無，全部乾淨 ✅"]
    if args.mode == "sync":
        lines += ["", "## 本次已自動處理", ""]
        lines += [f"- {s}" for s in synced] if synced else ["- 無符合安全自動同步條件的 repo"]

    report = "\n".join(lines)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"\n[報告已存至 {args.out}]", file=sys.stderr)


if __name__ == "__main__":
    main()
