\# Corpus: Google Drive Resumable Upload API



> PVG 來源文件 — 本頁摘錄官方規格，供 robust-file-ops skill 執行時驗證假設用。



---



\## 來源



Google. (n.d.). \*Perform a resumable upload\*. Google Drive API documentation.

Retrieved from https://developers.google.com/drive/api/guides/manage-uploads#resumable



---



\## 關鍵規格摘錄



\### 1. Session URI 有效期

"A resumable upload session is valid for one week from the time it is created."



意涵：session URI 存入磁碟後，7 天內都可以繼續上傳。

進程崩潰重啟後直接讀取並繼續，不需要重新建立 session。



\### 2. Chunk Size 規格

"Use a multiple of 256 KB (256 x 1024 bytes) for the chunk size."

"If you use a chunk size other than a multiple of 256 KB, the upload may fail."



意涵：chunk size 必須是 256 KB 的倍數。

建議值：8 \* 256 \* 1024 = 2 MB（穩定，網路波動容忍度高）。



\### 3. 查詢已上傳進度



PUT {session\_uri}

Content-Range: bytes \*/{total\_size}



回應：

\- 308 Resume Incomplete：Range: bytes=0-{last\_byte} → 從 last\_byte+1 繼續

\- 200 / 201：已完成

\- 404：session 失效 → 需重新建立（清除狀態）



\### 4. 錯誤處理規格



| HTTP 狀態 | 意涵 | 處理方式 |

|-----------|------|----------|

| 200 / 201 | 完成 | 結束，記錄成功 |

| 308 | 進行中 | 讀 Range header，繼續 |

| 4xx（除 429）| session 失效 | 清除 session URI，重建 |

| 429 | Rate limit | exponential backoff |

| 5xx | 伺服器錯誤 | exponential backoff，不清除狀態 |

| 網路異常 | 連線中斷 | 重試，不清除狀態 |



---



\## 實作注意事項（踩坑補充）



\- Content-Range 中的 total\_size 必須在第一個 chunk 就確定，之後不可更改

\- 最後一個 chunk 格式：bytes {start}-{end}/{total\_size}（end = total\_size - 1）

\- 若中途檔案被修改（size 改變），整個 session 需重建



---



\*最後驗證日期：2026-05-29\*

