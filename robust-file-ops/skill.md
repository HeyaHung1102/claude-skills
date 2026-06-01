\# SKILL: robust-file-ops



\## WHY（為什麼這個 Skill 存在）

長時間、高風險的檔案操作（大型上傳、備份同步、跨進程任務）

在真實環境中會遭遇網路中斷、進程崩潰、token 過期、系統強制重啟。

這個 Skill 的存在，是為了讓每一個操作都能在任何中斷點後

「重新執行同一個指令」就能繼續，不需要人工介入判斷。



\## HOW（怎麼做到）



\### 設計原則

1\. 狀態持久化優先：任何進度必須在成功的當下寫入磁碟，不依賴進程存活。

2\. PVG 驗證前置：每個主張（chunk size、retry 邏輯、token 刷新）

&nbsp;  都要能對應官方文件，不接受「應該可以」的假設。

3\. 來源標註：引用 API 行為時附 APA 格式來源。

4\. 錯誤分類明確：

&nbsp;  - 4xx → Session 失效 → 清除狀態重建

&nbsp;  - 5xx → 伺服器暫時錯誤 → exponential backoff 重試

&nbsp;  - 網路異常 → 重試，不清除狀態

5\. Windows 環境適配：

&nbsp;  - 路徑使用 Path.resolve()

&nbsp;  - token 有效期在每個 chunk 前檢查

&nbsp;  - SetThreadExecutionState 防止系統休眠，

&nbsp;    並在 docstring 明確標注其無法阻止的情境



\### 交付標準

\- 程式碼可直接複製執行，不需要額外說明

\- 參數配置集中在檔案頂部，清楚標註需要修改的地方

\- 每個函數有單一職責，失敗時不影響其他函數

\- 所有 except 必須有具體處理，不能靜默吞掉錯誤



\## WHAT（最終交付的是什麼）

一個在 VivoBook Windows 本地端，

能夠對抗網路波動、進程中斷、token 過期的

Google Drive 原生 API 斷點續傳上傳腳本，

並附帶 Prover-Verifier 審計報告說明每個設計決策的來源依據。



\## 觸發條件

使用者提到以下任一情境時啟用此 Skill：

\- 大型檔案上傳（> 1GB）

\- 長時間執行的自動化任務

\- 需要跨進程狀態保存的操作

\- 備份、同步、批次處理流程設計

\- 出現 ConnectionError、TimeoutError、token expired 錯誤



\## 禁止行為

\- 不使用 shell=True（除非有明確的技術必要性並說明）

\- 不用 grep 解析 JSON（改用 json 模組）

\- 不在函數中混入不屬於該函數職責的邏輯

\- 不宣稱「修正了 P2」但實際上沒有實作對應機制



\## 相關 corpus

\- corpus/gdrive\_resumable\_upload.md

\- corpus/windows\_sleep\_prevention.md



\## 相關 memory

\- memory/known\_patterns.md

