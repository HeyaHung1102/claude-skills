# git-loops 巡邏報告 — hongheyas-MacBook-Pro 2026-07-19
模式：scan（未 fetch，ahead/behind 以本地快取為準）

## 總覽

| repo | 路徑 | branch | 狀態 | ahead/behind | 最後 commit |
|---|---|---|---|---|---|
| osint-purifier-mcp | /Users/hongheya/osint-purifier-mcp | main | dirty | +0/-0 | 7e241fb 2026-07-16 修正 KL 散度平滑常數尺度錯誤（首次真實資料實測發現） |
| osint-purifier-mcp | /Users/hongheya/Documents/GitHub/osint-purifier-mcp | main | dirty | +0/-138 | 9669da9 2026-06-07 Merge branch 'claude/nifty-noether-LCs0m' |
| portfolio-tracker | /Users/hongheya/portfolio-tracker | claude/optimistic-fermi-6fs51v | dirty | +0/-0 | 673aca3 2026-07-07 docs: memory.md 記錄本地未提交改動的真相——同款修法的命名衝突 |
| portfolio-tracker | /Users/hongheya/Documents/GitHub/portfolio-tracker | main | clean | +0/-0 | 8fab0b7 2026-06-06 feat: GCS FUSE 掛載持久化 DB + journal_mode=DELETE + 完整 deploy.sh |
| claude-skills | /Users/hongheya/claude-skills | main | clean | +0/-0 | 90d0a8b 2026-07-18 Sync memory.md: Dispatch desktop-asleep diagnosis |
| Faith-Hope-Love | — | — | **缺席** | — | — |
| my_knowledge_base | /Users/hongheya/my_knowledge_base | main | clean | +0/-0 | 6f047a5 2026-07-18 feat(automation): A00866 排程 wrapper — 週覆核機械警報 |

## 需要人工處理

- **osint-purifier-mcp**：發現 2 份副本（/Users/hongheya/osint-purifier-mcp, /Users/hongheya/Documents/GitHub/osint-purifier-mcp），需人工決定正本
- **osint-purifier-mcp** `/Users/hongheya/osint-purifier-mcp`：有 1 個修改 + 5 個 untracked，需人工 commit 或清理
- **osint-purifier-mcp** `/Users/hongheya/Documents/GitHub/osint-purifier-mcp`：有 1 個修改 + 0 個 untracked，需人工 commit 或清理
- **portfolio-tracker**：發現 2 份副本（/Users/hongheya/portfolio-tracker, /Users/hongheya/Documents/GitHub/portfolio-tracker），需人工決定正本
- **portfolio-tracker** `/Users/hongheya/portfolio-tracker`：有 0 個修改 + 1 個 untracked，需人工 commit 或清理
- **Faith-Hope-Love**：這台機器上找不到，需 clone 或確認只存在於其他機器
