# Memory — claude-skills 思考記憶庫

---

## Dispatch 首航成功 + git-loops 技能誕生（2026/7/18-19）

### Dispatch 端到端驗證完成
承接上面 Asleep 誤報翻案：使用者在桌面 app 按下正確 session 的資料夾授權後，
「Line 快捷鍵截圖與研究」任務順利跑完，產出
`LINE_Mac_快捷鍵完整清單.md`（8 個已知快捷鍵 + 網路補充的 5 個，分基本/好友聊天列表/聊天三類）。
**這是 Dispatch 手機遙控桌機的第一次完整成功案例**，可作為未來示範範本。

### 新建技能：git-loops（跨機多 repo 巡邏同步）
起點：Isaac 的五個 GitHub repo（HeyaHung1102 帳號：osint-purifier-mcp、
portfolio-tracker、claude-skills、Faith-Hope-Love、my_knowledge_base）散落在
MacBook Pro 與 ASUS Vivobook 上，想要一個技能能批次檢查/同步。
公司桌機 A00866 明確排除（不能裝 Claude Code）。

技能位置：`git-loops/`（SKILL.md + `scripts/git_loops.py` + `config/machines.json`）。
核心設計：**scan（唯讀盤點）永遠先做，sync 只對「乾淨且落後遠端」的 repo
自動 ff-pull，其餘一律只回報不動手**（dirty/需 push/分岔/重複副本都要人工決定）——
因為這些 repo 裡有交易筆記、公務文件草稿，自動 merge 或誤刪副本代價太高。

跨機器透過 `config/machines.json` 用 hostname 分流搜尋根目錄；Vivobook 第一次跑
scan 時腳本會印出偵測到的 hostname，供手動填入設定檔（目前该欄位是佔位符
`VIVOBOOK-PLACEHOLDER`，還沒有真實跑過）。

### 2026/7/18 首次盤點結果（MacBook Pro 單機，`content/git_loops_inventory_20260718.md`）
| repo | 發現份數 | 狀態 |
|---|---|---|
| osint-purifier-mcp | **2 份**（`~/osint-purifier-mcp`、`~/Documents/GitHub/osint-purifier-mcp`） | 兩份都 dirty |
| portfolio-tracker | **2 份**（`~/portfolio-tracker`、`~/Documents/GitHub/portfolio-tracker`） | 一份在 `claude/optimistic-fermi-6fs51v` 分支且有 untracked 檔，另一份 main 乾淨 |
| claude-skills | 1 份 | 乾淨 |
| my_knowledge_base | 1 份 | 乾淨 |
| Faith-Hope-Love | **0 份（缺席）** | 這台機器上完全找不到，需 clone 或確認是否只活在 Vivobook |

**易混淆但確認排除的假警報**：`~/osint-purifier-mcp/portfolio-tracker` 看起來像
第三份 portfolio-tracker 副本，但實際查證它**沒有自己的 `.git`**，只是
osint-purifier-mcp repo 裡一個同名資料夾（裝著量化交易筆記 .md/.html），
不是重複 clone。腳本靠「有沒有 `.git`」正確排除了它，人工複查也確認無誤——
未來看到路徑裡有 repo 名稱重複出現，先查 `.git` 是否存在，別急著當成重複副本。

### 待辦（下次接續）
1. **決定每個重複 repo 的正本路徑**（建議收斂到 `~/Documents/GitHub/<repo>`，
   跟 GitHub Desktop 預設一致），另一份要嘛刪除要嘛改名成 `-old` 標記
2. **確認 Faith-Hope-Love** 是否真的只存在於 Vivobook，若是則這台 Mac 要 clone 一份
3. **在 ASUS Vivobook 上跑第一次 `git_loops.py scan`**，把印出的真實 hostname
   填回 `git-loops/config/machines.json`（目前是佔位符），才能真正做到「跨機」而不只是單機
4. 這次為了今天交付中間清單，**跳過了 skill-creator 標準流程的 eval/benchmark 迴圈**
   （spawn 測試案例、benchmark.json、eval viewer）——這是務實工具腳本，
   用真實資料跑過一次 scan 就是最直接的驗證；若之後要精修觸發描述，
   再回頭補 description 優化那一段

---

## Premortem：Dispatch / Data Plugin 安裝卡關（2026/7/15）

### 起點
Isaac 已訂閱 Pro，`claude plugins add knowledge-work-plugins/data` 報錯
`unknown command 'add'`；懷疑是網路連線問題。

### Premortem 結論（排除網路後的死因排行）
1. **CLI 指令用錯**（機率最高）：`claude plugins add` 不是合法子指令，
   plugin marketplace 安裝要在 **`claude` 互動模式內**用 `/plugin` 系列指令：
   ```
   /plugin marketplace add anthropics/knowledge-work-plugins
   /plugin install data@knowledge-work-plugins
   ```
2. **產品面搞混**：Dispatch（手機遙控桌機）屬於 **Cowork 桌面 app**，
   不在 Claude Code / 終端機範圍內，需要桌面 app + 手機 app 同帳號配對 + beta 開關。
3. 其餘較低機率：beta 分批開放未輪到、桌機/手機帳號不一致、版本過舊、
   公司 GCB 組態封鎖（僅辦公室電腦適用，MacBook Pro 個人機不受影響）。

已產出圖表 `content/premortem_dispatch_chart.html`（色盤已跑 dataviz skill 驗證器）。

### 實測結果：指令對了，但撞到新問題——SSH host key 未信任
照建議指令下 `/plugin marketplace add anthropics/knowledge-work-plugins` 後，
錯誤變成：
```
SSH host key is not in your known_hosts file. ... Host key verification failed.
```
**根因**：Claude plugin marketplace 預設用 SSH 協定（`git@github.com:...`）clone，
但這台 MacBook Pro 從未手動連過 `github.com` 的 SSH，所以 `~/.ssh/known_hosts`
沒有 GitHub 的 host key 指紋，觸發 strict host key checking 擋下。

**這不是帳號/網路/訂閱問題，是全新的第四類死因：本機 SSH 信任鏈未建立。**
應補進 premortem 排行第 1.5 名（緊追 CLI 指令用錯之後）。

### 解法（兩選一，記錄給下次接續）
- **選項A（官方建議，較安全）**：手動連一次驗證指紋後才會寫入 known_hosts：
  ```
  ssh -T git@github.com
  ```
  出現 fingerprint 提示時比對 GitHub 官方公告的 SHA256 指紋後輸入 yes。
- **選項B（改用 HTTPS，跳過 SSH 信任鏈）**：若該 plugin marketplace 指令支援
  HTTPS URL 形式，改用 `https://github.com/anthropics/knowledge-work-plugins`
  可完全避開 SSH host key 問題，更適合不想手動維護 known_hosts 的情境。

### 選項B 確認可行（2026/7/15 web 查證）
`/plugin marketplace add` **支援完整 HTTPS URL**，關鍵是要帶 `https://` 前綴
+ `.git` 結尾才會強制走 HTTPS、跳過 SSH host key 檢查：
```
/plugin marketplace add https://github.com/anthropics/knowledge-work-plugins.git
/plugin install data@knowledge-work-plugins
```
也可用 `#branch-or-tag` 語法釘住分支/版本。
另查到 Claude Code 官方 GitHub issue #26588：marketplace clone 預設用 SSH 是已知痛點，
社群已提議改預設 HTTPS——代表 Isaac 撞到的不是個案，是產品已知問題。

### 待確認（下次接續）
1. Isaac 用 HTTPS URL 指令重試 `/plugin marketplace add` 是否成功
2. Data plugin 裝好後，Dispatch（Cowork 桌面 app）仍需獨立確認：桌面/手機 app 配對狀態

### Dispatch 手機配對檢查清單（2026/7/15，給下次接續用）
Dispatch 屬於 Cowork **桌面 app**，不是 CLI/終端機功能，跟 data plugin 是兩件獨立的事：
1. 桌面 Claude app 需登入 `bssurcn@gmail.com`，且需保持開啟（背景執行即可）
2. 桌面 app 設定裡確認 Cowork/Dispatch beta 開關已開
3. 手機 Claude app 用同一組帳號登入
4. 手機端找 Dispatch/指派任務入口，傳測試訊息驗證（例如「讀取桌面資料夾清單」）
5. **若手機端找不到 Dispatch 入口** → 判讀為「這輪 beta 尚未輪到帳號」，
   屬於 premortem 排行第 3 名（beta 分批開放），不是操作錯誤，不需要繼續除錯，
   應該的下一步是等待輪次或直接回報 Anthropic，而不是反覆重裝。

### 確認：beta 已開啟（2026/7/15 手機截圖驗證）
Isaac 手機端已看到獨立的「Dispatch」頁面（輸入框文字「Dispatch any task」），
代表 premortem 排行第 3 名（beta 分批開放未輪到）**已排除**——帳號這輪確實有拿到權限。
下一步不是繼續除錯裝置/帳號問題，而是實際發一則測試任務驗證桌機端真的會執行
（例如「讀取桌面資料夾清單」），確認 Dispatch 端到端真的打通。

### 實測結果：桌機端未連上（"Asleep" 狀態）
Isaac 送出實際任務後，Dispatch 顯示狀態 **Asleep**，並回覆：
`Can't reach your desktop. Check that your computer is online and desktop app is open.`

**確診**：beta 權限完全沒問題（帳號、配對、任務傳送都成功），問題縮小到
**桌面端連線層**，只有兩種可能：
1. MacBook Pro 桌面 Claude app 沒開啟/已被關閉或登出
2. MacBook Pro 進入睡眠或螢幕鎖定，網路連線中斷

**新增 premortem 排行第 0 名（比 SSH host key、beta 輪次都常見）**：
Dispatch 需要桌機端 app **保持在執行狀態**（背景執行可，但不能整台睡眠），
這是持續性條件，不是一次性設定——每次要用 Dispatch 前都要先確認桌機醒著、
app 開著，這點應該寫進未來任何「用手機遙控電腦」流程的標準檢查清單第一條。

### 翻案（2026/7/18 桌機端實地鑑識）：任務其實有送達，卡在權限審批，「Asleep」是誤報

在 MacBook Pro 本機直接查證後，**上面「桌機睡著/app 沒開」的診斷被證據推翻**：

**證據鏈**（全部來自本機系統紀錄，非推測）：
1. `pmset -g log`：Mac 從 7/17 21:58 醒來後**整天沒睡**，13:28 螢幕還亮起，
   13:32 測試當下機器完全清醒
2. `ps` + `pmset -g assertions`：桌面 Claude app 從 7/17 07:48 一直在跑，
   還握著 NoIdleSleepAssertion（防閒置睡眠鎖）近 30 小時
3. `~/Library/Logs/Claude/main.log` **決定性證據**：
   - `13:32:57 Writing 1 Dispatch seed message(s)` → 任務有送達桌機
   - `13:33:20 Spawned child local_49663a79 ("Line 快捷鍵截圖與研究")` → 桌機真的開了 session 執行
   - `13:33:43 Emitted tool permission request for mcp__cowork__request_cowork_directory`
     → session 卡在「存取 iCloud 桌面資料夾」的**權限審批**，等人按同意，之後就沒動靜

**修正後的結論**：
- Dispatch 端到端**其實已經打通**（手機→雲端→桌機→spawn session 全部成功）
- 手機顯示的「Asleep / Can't reach your desktop」是**狀態誤報或延遲**，
  不能當作桌機離線的可靠證據——**log 才是一手證據，手機 UI 狀態是二手轉述**
- 真正的卡點是 **Cowork 目錄存取權限**：Dispatch 派來的任務要讀
  `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop`（iCloud 桌面），
  需要在桌面 app 裡按一次同意

**premortem 排行第 0 名改寫**：不是「桌機要醒著」（那只是必要條件），
而是「**Dispatch 任務落地後的權限審批沒人按**」——手機端看不到桌機端的
permission prompt，任務就無聲卡死，手機還顯示誤導性的 Asleep。
未來檢查順序：先看桌機 `main.log` 有沒有 `Spawned child`，有就去桌面 app 找
待審批的權限卡，**不要被手機的連線狀態圖示帶著跑**。

**附帶發現**（真正的睡眠風險，供未來參考）：這台 Mac 系統睡眠計時器設 1 分鐘、
7/17 有多次 Clamshell Sleep（闔蓋睡眠）紀錄。桌面 app 開著時會自己防閒置睡眠，
但**闔蓋會強制睡眠、assertion 擋不住**——出門要用 Dispatch 前別闔蓋，
或插電接外接螢幕跑 clamshell mode。

---

## 反向幻覺案例：Gemini 誤判 Claude Cowork 為第三方軟體（2026/7/15 查核）

### 事件
Gemini 用看似嚴謹的 Prover-Verifier 報告宣稱：Claude Cowork、/schedule 排程、
7 個 Data Skills（explore-data 等）、Dispatch 手機遙控桌機「都不是 Anthropic 官方功能，
是第三方軟體被誤稱」，還附上熵計算（ΔH≈6.5 bits）與三筆參考文獻。

### 查核結果（經 web 官方來源驗證）
- ❌ 全部推翻：Cowork 是官方桌面產品（support.claude.com 有官方文件）、
  Scheduled Tasks / Data Plugin（anthropics/knowledge-work-plugins 開源）/ Dispatch（Pro/Max beta）皆為官方功能
- ✅ 唯一正確：LLM 抓的股價有延遲，不可作即時交易依據
- ⚠️ GCB 政府組態電腦確實可能用不了 → 但原因是「組態政策封鎖安裝/外連」，
  不是「功能不存在」；硬體品牌（Vivobook/MacBook Pro）完全無關；真正門檻是付費方案層級

### 關鍵教訓（防幻覺原則升級）
1. **反向幻覺**：模型訓練截止日期後的新產品，會被推理成「不存在→一定是第三方」——
   把真的當成假的，比編造假的更難察覺
2. **格式嚴謹 ≠ 內容正確**：熵計算公式、APA 文獻、Prover-Verifier 框架都可以被
   拿來包裝錯誤結論；Gemini 引用的 O'Reilly 書目查無此書（捏造文獻）
3. **查證產品功能類主張的鐵則**：必查當下的官方文件（support.claude.com / 官方 GitHub），
   不信任何模型的內部記憶
4. **一手證據優先**：本 session 自身就載有 Skill/排程工具，是最強反證——
   「我正在用的東西」比「任何模型說它存在與否」更可信

---

## 空間整理 → 數位整理同構（2026/6/16，搬家後整理）

### 起點
Isaac 搬家回來（約 4m×6m 空間隔成客廳/廁所/臥室），要用
「取出→分類→斷捨離→整理→歸位→測試」整理實體物品，
目標：縮小體積、直立式存取、容易記得的口訣，並把發現用在數位整理。

### 產出：spatial-embodiment skill（六步口訣「取分捨理位測」）
把身體整理記憶抽象成演算法，實體與數位共用同一口訣。詳見
`spatial-embodiment/skill.md`。

### 三個可遷移到數位的原則
1. **先量容器，再決定內容**：搬家先量櫃深(67cm)/檯寬(1.59m)再放東西
   → 先定 repo 結構再放檔案，不要先囤再塞。
2. **直立式存取 = 扁平可見性**：平放疊三層底層找不到
   → 避免五層巢狀，用「扁平+命名前綴」讓每檔一眼可見。
3. **動線頻率決定歸位距離**：常用靠手邊、季用上高櫃
   → 常用 skill 放根目錄，冷資料進 corpus/archive。

### 額外洞察：便宜的容器可能擴大攻擊面（呼應 §15 資安）
eSIM（Saily）比三大電信漫遊便宜，但在杜拜/緬甸/馬來西亞這類
高監控或高風險地區，虛擬營運商多一層不透明中介＝多一個攻擊面；
日韓法治成熟，此差別被稀釋，只剩成本考量。
→ 與「先量容器」同構：省錢的容器可能省了成本卻放大風險，
   選容器時要同時看「成本」與「攻擊面」兩個維度。

---

## 本職工作洞察 — 高速公路局路產組（2026/6/16 緊急任務）

### 關鍵發現：本職工作與地政背景是同一條線，不是兩件事
CLAUDE.md 寫的「Isaac：地政 × 法律背景」不是過去式的學歷描述，
是**現在進行式的職務內容**。Isaac 是交通部高速公路局**路產組**窗口（洪赫亞），
路產組業務 = 國有公用財產管理、違章建築處理、土地占用排除、產籍管理——
這正是地政專業在公部門的實戰場域。

**意涵**：claude-skills 不該只服務「下班後的創業」，
公部門的路產業務文書作業本身就是可以被技能化、自動化的對象，
而且 Isaac 在這個領域有真正的專業深度（不是外行模仿）。

### 緊急任務拆解（來源：115年6月16日綜合組企劃科辜琬淇來信）
- **deadline：115年6月24日（三）前回復**
- 任務 1：回復路產組是否有【頒獎/獻獎】需求排入 115年第6次局務會報（7月召開）
  - 若有，需檢附：背景說明 + 評定結果/得獎名單 + 局長致詞稿（200-400字）
  - 逾 6/24 未簽奉核准，會被排到下次會議
- 任務 2：規劃組要提供「專題報告」題目（輪流制，路產組不一定要交，但要確認順序）
- 任務 3：各單位視業務需要，提交「宣導/協調/處理事項」報告題目

### 範本結構分析（從 3 份歷史案例歸納）
所有「頒獎背景資料」都遵循固定骨架：

```
一、獎項背景說明
  (一) 緣由/沿革：自民國幾年開始辦理
  (二) 辦理依據：法規條文 + 內部簽核文號
  (三) 評選委員組成：人數、來源機關
  (四) 參獎數量：參賽單位/件數
  (五) 評選過程：考核期間、評分標準（含百分比權重）

二、評定結果/得獎名單/獎品內容
  表格：名次｜單位｜得獎人(姓名+職稱)｜得獎內容｜獲獎原因｜獎品內容

三、局長致詞稿（200-400字）
  固定模式：肯定全體 → 點名前幾名具體事蹟 → 期許未來 → 「謝謝大家」收尾
```

**文風特徵**：
- 數字精確到百分比、筆數（例如「達137筆，預算執行率95%以上」）
- 致詞稿避免空泛溢美，每個獲獎理由都附具體量化成果
- 結尾固定句式："期許大家持續以專業..." + "謝謝大家"

### 下一步：開發 Skill
計畫做一個 `award-writeup` skill：
- 輸入：獎項名稱、主辦單位、得獎名單（含量化成果）、評選依據
- 輸出：符合上述三段式骨架的完整 docx 草稿
- 價值：把「臨時被要求生成公文」從半天工作壓縮到 10 分鐘審核

### 已確認（2026/6/16 第二輪問答）
1. **路產組這次（115年第6次局務會報）有沒有具體要頒的獎項？**
   → 一開始的答案（115年度國有公用財產管理情形檢核第一名）後來發現
   實際 docx 寫的是排入**第7次**會報，不是第6次。
2. **第6次會報路產組究竟要回什麼？**
   → 回復「本次（6次）無頒獎需求，預計排入第7次；若第7次仍因故來不及，順延至第8次（115年8月）」。
   draft 已寫好：`award-writeup/drafts/reply_115_6th_meeting.md`
3. **得獎名單和量化成果是否已備好？**
   → 已備好（docx 內容完整：卓明君分局長/養護工程分局組第一名、
   張勝緯分局長/新建工程分局組第一名），已存入語料庫
   `award-writeup/corpus/property_management_check_115.md`
4. **規劃組的專題報告輪到路產組了嗎？**
   → 無關，路產組不需回應此項。
5. **附的招標 JSON（泰管園區建築物火災保險及地震險）跟這次頒獎任務有關嗎？**
   → 無關，是路產組另一個獨立的招標/得標紀錄任務，不要混進 award-writeup 語料庫。

### 關鍵教訓：「資料齊全」≠「可以馬上排入下一次會報」
即使獎項背景資料、得獎名單、致詞稿都已經寫好，**仍要對照評核計畫本身的時程表**
（例如：現地檢核到4月、評分5/31前核定）來判斷這次會報是否真的趕得上。
這是 award-writeup skill 目前還沒覆蓋到的檢查項，之後可以加進 skill.md 的
「評選過程」欄位旁邊，提醒使用者順便確認「評核計畫時程 vs 會報排程」是否對得上。

### Skill 完成狀態
`award-writeup` 已有 4 份語料庫範例（違章建築/國產考核、金安獎、環評追蹤考核、
115年國有公用財產管理檢核-實際案例）+ 1 份回復公文草稿範本，
可視為第一版完成，後續若有更多真實案例可持續擴充語料庫。

---

## IRR 專案 — repo 確認與待辦（2026/6/16）

### 已確認
- repo `HeyaHung1102/portfolio-tracker` **確實存在**（Private, Python, 建立於 2026/6/6）
- 預計開發分支：`claude/optimistic-fermi-6fs51v`（**尚未驗證該分支是否存在**，
  因為這個 session 的 GitHub MCP 範圍只開放 `claude-skills`，無權限列出 portfolio-tracker 的分支）

### 待辦（下次接續 IRR 工作時）
1. 把 `portfolio-tracker` 加進 session 的 repo 允許清單，
   或在新 session 直接指定要操作這個 repo
2. 確認 `claude/optimistic-fermi-6fs51v` 分支是否已存在，沒有就建立
3. 把上一輪整理好的 IRR repo 專用 CLAUDE.md 提示詞放進該 repo
   （內容：左手右手飛輪定位、XIRR 計算核心需求、74.5% 先知不等式基準、
   與 claude-skills/prophet-trading 的模型共用關係）
4. 第一個任務：XIRR 計算核心（Newton-Raphson 或 scipy.optimize），
   附「分批買入 + 中途賣出 + 全部出清」單元測試案例

### 中斷原因
Isaac 日間本職有緊急工作插入，此處中斷，留下待辦供下次接續。

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
