---
name: git-loops
description: >
  批次檢查並同步散落在多台機器（MacBook Pro、ASUS Vivobook）上的 GitHub repo
  （HeyaHung1102 帳號：osint-purifier-mcp、portfolio-tracker、claude-skills、
  Faith-Hope-Love、my_knowledge_base）。只要使用者提到「同步 repo」「更新我的
  github」「檢查所有 repo 狀態」「哪些 repo 還沒 push」「兩台電腦的程式碼對不對得上」，
  或任何涉及多個本地 git repo 的盤點、更新、推送需求——即使沒有明講 git——都應使用本技能。
compatibility: 需要 python3 與 git CLI（macOS / Windows 皆可）
---

# git-loops — 多機多 repo 巡邏同步

## 這個技能解決什麼

Isaac 的五個 GitHub repo 散落在多台機器、甚至同一台機器的多個路徑
（實測 2026/7/18：osint-purifier-mcp 在 MacBook 上有 2 份、portfolio-tracker 有 3 份，
其中一份還嵌在別的 repo 裡）。手動逐一 `git status` 又慢又容易漏。
本技能用一支腳本把「盤點 → 回報 → 安全同步」跑完一輪。

## 使用方式

### 1. 掃描（預設，唯讀，永遠先做這步）

```bash
python3 git-loops/scripts/git_loops.py scan
```

輸出每個 repo 副本的：路徑、branch、未提交變更數、untracked 數、
ahead/behind（加 `--fetch` 才會先抓遠端最新狀態）、最後 commit、重複副本警告。

加 `--out 報告路徑.md` 可同時存成 Markdown 報告（中間清單就是這樣產出的）。

### 2. 同步（保守模式）

```bash
python3 git-loops/scripts/git_loops.py sync --fetch
```

只對「乾淨且落後遠端」的 repo 執行 `git pull --ff-only`。
以下情況一律**只回報、不動手**，因為這些決策需要人：
- 有未提交變更或 untracked 檔案的 repo（絕不自動 commit / stash）
- 領先遠端需要 push 的 repo（push 由使用者確認後自己下，或明確授權後代為執行）
- fast-forward 失敗（代表分岔，需要人決定 merge/rebase）
- 同一 repo 的重複副本（需要人決定哪份是正本）

為什麼這麼保守：這些 repo 裡有交易筆記、公務文件草稿，錯誤的自動 merge
或誤刪副本的代價遠大於多按一次確認。

### 3. 跨機器

設定檔 `config/machines.json` 以 hostname 分機器記錄搜尋根目錄。
在 Vivobook 上第一次跑時：先執行 `python3 git-loops/scripts/git_loops.py scan`，
腳本找不到對應 hostname 會列出目前 hostname 並提示把它加進設定檔。
公司桌機 A00866 不納入（無法安裝 Claude Code）。

跨機器的「同步」本質上是透過 GitHub remote 中轉：每台機器各自
scan → 處理未推送的變更 → push，另一台再 pull。腳本不做機器對機器的直連。

## 產出格式

掃描報告固定用這個結構（Markdown）：

```
# git-loops 巡邏報告 — <hostname> <日期>
## 總覽表：repo | 路徑 | branch | 狀態 | ahead/behind | 最後 commit
## 需要人工處理：逐項列出（dirty / 需 push / 分岔 / 重複副本 / 缺席）
## 本次已自動處理：ff-pull 成功清單（sync 模式才有）
```

## 已知現況（2026/7/18 首次盤點，詳見 content/git_loops_inventory_20260718.md）

- MacBook Pro 上 Faith-Hope-Love **不存在**，需要 clone 或確認它只活在 Vivobook
- 重複副本問題比「沒同步」更嚴重，先收斂每個 repo 到單一正本路徑再談自動同步
- 建議正本路徑收斂到 `~/Documents/GitHub/<repo>`（GitHub Desktop 預設）或家目錄，二選一
