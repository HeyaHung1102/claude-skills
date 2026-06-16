# N8N 待辦記憶

## 下次提到 N8N 時要做的事

### 目標
把 iPhone Shortcuts OCR 結果寫回 GitHub `claude-skills/content/` 資料夾

### 現有流程狀態（2026/6/16 確認可用）
- Shortcuts → 選取照片（多選）→ 迴圈 OCR → 累積 AllText → POST webhook
- Webhook URL：`https://isaac-hoya-hung.zeabur.app/webhook-test/56d9c92b-b2e8-40f1-839f-29a68619b86f`
- n8n 已收到 `text_length: 1015`，內容是真實投資日報文字 ✅

### 下一步：n8n 加 GitHub 寫檔節點

在 Webhook 節點後加：

**節點類型**：GitHub  
**動作**：Create or Update File  

```
Repository：HeyaHung1102/claude-skills
Branch：main（或 claude/loving-planck-4hqgW）
File Path：content/ocr_{{ new Date().toISOString().slice(0,10) }}.txt
File Content：{{ $json.body.text }}
Commit Message：feat: add OCR screenshot {{ $json.body.timestamp }}
```

**Credential**：需要在 n8n 設定 GitHub Personal Access Token
- 權限需要：`repo`（contents read/write）
- 去 GitHub → Settings → Developer settings → Personal access tokens → 生成

### Shortcuts 目前流程（已確認正確）
1. 從分享表單接收（若沒輸入繼續）
2. 選取照片（多選開啟）
3. 將 AllText 設為空白（空白字元）
4. 將 Counter 設為剪貼板（暫用）
5. 重複「照片」中每個項目
   - 取得重複項目名稱
   - 從重複項目擷取文字
   - 從重複項目取得拍攝日期
   - 從重複項目取得位置
   - 文字 Block：[AllText]\n--- [名稱] ---\n[OCR文字]\n[日期]\n[位置]
   - 將 AllText 設為 文字
   - Counter + 1
6. 結束重複
7. 顯示通知：完成！Counter = [計算結果]
8. POST webhook（text: AllText, source, timestamp）
