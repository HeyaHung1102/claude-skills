# Memory — claude-skills 思考記憶庫

---

## 2026/6/16 紀錄

### 自動化平台選擇：n8n vs Make.com
- 公司同部門 AI 負責人 + 聯成電腦課程都在推 n8n，主打「本地端免費部署」
- **但 Isaac 實際完成過 loop 的平台是 Make.com**，n8n 課程買很久了，作業還沒做完
- **決策**：不需要為了「別人都在用」而切換。Make.com 已驗證可用 → 繼續用它把流程跑通；
  n8n 留給「需要本地部署、零成本」的場景再切換，不要兩邊都半途
- claude-skills 的 prophet-trading / OCR webhook 已經是 n8n 架構，這部分既有投入先用完，
  但新的自動化需求可優先評估 Make.com，因為那是真正跑通過的平台

### 小聚觀察（115年6月14日）
- 觀察：政治立場與性別呈現「男性偏保守右派、女性偏自由左派」的傾向
- 來源：當天小聚的真實互動，不需要靠超級歪哲學電台或 Hahow 哲學課就能觀察到
- **這是一個未經查核的個人觀察，不是學術結論**，記錄供內容素材參考，發布時要標註是個人觀察

### 新接觸的同類人群
- 第一次見到（尚未真正認識）除客戶「樺」以外、**靠台股投資維生**的人
- 共同痛點：知道自己靠台股賺了不少錢，**但不知道如何計算 IRR 或機會成本等財產指標**
- **這是一個明確的產品機會**：可以做一個簡單的 IRR / 機會成本計算工具，
  服務「賺到錢但不會算真實報酬率」的台股全職投資人
- 對應左手右手飛輪模型：這群人本身就是右手（市場）裡的活生生案例，
  可以成為未來內容或產品的真實訪談素材

### 逐字稿事實查核結果（已套用 Prover-Verifier 模型）
查核了 6 個原子主張，4 真 1 假 1 證據不足：

| 主張 | 結論 |
|---|---|
| 先知不等式 1977 年證明，凡人至少拿到上帝視角 50%，i.i.d. 情況下最高 74.5% | ✅ 支持 |
| 商朝青銅文明高度分工，對石器部落具壓倒性優勢 | ✅ 支持 |
| 台灣證交法 157-1 條，消息受領人（非董監事）聽內線交易也違法 | ✅ 支持 |
| 巴菲特買波克夏紡織廠是「煙屁股」策略失敗案例 | ✅ 支持 |
| 夏代《連山易》本質是結繩記事系統 | ⚠️ 證據不足，個人假說 |
| Commerce 字源 = com（一起）+ merci（慈悲） | ❌ 推翻，正確字源是 com + merx（商品/交易） |

**已修正**：`content/week1_script.md` Day 7 的 Commerce 字源段落已改為正確字源（com + merx），
保留「商業本質是『一起』」的精神但去掉錯誤的「慈悲」字源宣稱。

**先知不等式精確數字更新**：之前模型用「50%」，逐字稿查核確認 i.i.d. 情況下最優單閾值
漸進上限是 **74.5%**，比 50% 更精確。`prophet_trade.py` 的說明文件可以更新這個數字。

---

## Buffett on Claude Code — 左手右手飛輪模型

### 核心比喻
- **左手 = 實體環境**（公司、顧問業務、知識服務、地政法律背景）
- **右手 = 金融市場**（股票、期貨、量化交易）
- **飛輪邏輯**：左手發生不尋常的事 → 當作「內線信號」在右手測試 → 右手用上帝不等式決定停利/停損 → 把右手的驗證結果帶回左手發行 MVP

### 完整流程（Skill 思考記錄）

```
左手信號（實體世界）
  ↓
  例：公司突然湧入大量詢問 / 某個知識主題突然被很多人問
  ↓
右手測試（金融市場代理驗證）
  ↓
  1. 找對應的金融標的（行業 ETF / 相關股票）
  2. 投入小額資金（例如 $100）作為「假設驗證單」
  3. 用 prophet_trade.py 算出：
     - 最優停利點（Samuel-Cahn 閾值 + 華羅庚 0.618）
     - 停損點（2% 風險上限）
  4. 觀察：多久到達停利？多久到達停損？
  ↓
右手結果解讀
  ↓
  停利達成 → 市場驗證左手信號有效 → 左手加速推出 MVP / 提高定價
  停損觸發 → 市場不認同 → 左手重新評估方向，或等待更多信號
  ↓
左手 MVP 發行
  ↓
  用 0.618 定價法設定測試價格
  用上帝不等式決定「觀察多少人詢問後才正式推出」（37% 法則）
```

### 關鍵數學節點

| 決策點 | 數學工具 | 參數 |
|---|---|---|
| 何時出手投資 | Samuel-Cahn 最優停止 | 觀察前 37%，之後取最優 |
| 停利點設定 | 華羅庚 0.618 | 測試價 = 下限 + 0.618×(上限-下限) |
| 停損點設定 | 風險預算 | max_loss = capital × 2% |
| MVP 定價 | 0.618 定價法 | 同上，套用在服務定價 |
| MVP 發行時機 | 上帝不等式 37% | 詢問量達目標 37% 後開始轉換 |

### 防知識蒸餾語法
這套方法的「公鑰」是：左手/右手/雪球/飛輪  
「私鑰」是：你真的同時在經營實體業務 AND 在量化驗證信號  
沒有同時持有兩把鑰匙的人，只能看到表面的投資方法論

### 技術工具對應
- `prophet_trade.py` → 右手量化驗證
- `n8n webhook` → 左手信號自動擷取（截圖 OCR）
- `claude-skills/content/` → 信號記錄與 MVP 素材庫
- `my_knowledge_base` → 長期知識沉澱

### 下一個可執行動作
1. 左手觀察到信號時，先截圖記錄（用現有 Shortcuts 流程）
2. 對應右手標的跑 `python prophet_trade.py --ticker XXX --capital 100`
3. 紀錄結果到 `content/signal_YYYYMMDD.md`
4. 停利或停損後寫覆盤，決定左手 MVP 是否推進

---

## N8N 待辦記憶

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
