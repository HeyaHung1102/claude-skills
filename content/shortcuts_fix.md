# iPhone Shortcuts 多圖片 OCR → Webhook 修復指南

## 問題診斷

從你的 JSON 可以看出：

```json
"\"text\"": "你现在是我的个人量化风控顾问..."
```

**問題根因**：`body.text` 只有一個字串，不是陣列。
當 Shortcuts 對多張圖片跑「重複」(Repeat) 動作時，
每次迭代的 OCR 結果會**互相覆蓋**，最後只剩最後一張的文字。

---

## 修復方法（不需要看 iCloud 連結）

### 方法一：用「變數累加」收集所有 OCR 結果

```
[Shortcuts 流程]

1. 設定變數 allText = ""（文字變數）

2. 重複（對每張圖片）：
   ├── 從圖片提取文字 → 存入 ocrResult
   └── 將 allText 設為：allText + "\n---\n" + ocrResult

3. 傳送 Webhook：
   └── body = { "text": allText, "timestamp": 現在時間 }
```

### 方法二：用 JSON 陣列傳送（推薦，n8n 更好解析）

```
[Shortcuts 流程]

1. 建立清單變數 results = []

2. 重複（對每張圖片）：
   ├── 從圖片提取文字 → ocrResult
   └── 將 ocrResult 加入 results 清單

3. 傳送 Webhook：
   └── body = {
         "source": "iPhone Shortcuts",
         "images": results,       ← 這裡是陣列
         "count": results 數量,
         "timestamp": 現在時間
       }
```

---

## 你的 Webhook URL（從 JSON 取得）

```
POST https://isaac-hoya-hung.zeabur.app/webhook-test/56d9c92b-b2e8-40f1-839f-29a68619b86f
```

---

## n8n 端的對應接收邏輯

```javascript
// n8n Function 節點
const images = $json.body.images || [];

return images.map((text, i) => ({
  json: {
    index: i + 1,
    text: text,
    timestamp: $json.body.timestamp
  }
}));
```

---

## 關鍵診斷問題

你在 Shortcuts 裡，重複動作是用：
- A) 「重複」(Repeat N times) — 要用方法一
- B) 「對每個項目重複」(Repeat with Each) — 可以直接建清單
- C) 「選擇照片」允許多選，然後直接對 Images 跑 — 用方法二最乾淨

如果你能截圖 Shortcuts 的流程畫面，我可以直接告訴你哪一個節點要改。
