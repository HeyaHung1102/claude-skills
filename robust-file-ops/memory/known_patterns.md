\# Memory: robust-file-ops 已知有效模式



> 第一次成功執行後沉澱的模式。每次有新的「踩坑 → 解法」，追加到本頁。

> 格式：\[日期] 情境 → 解法



---



\## 狀態檔設計（已驗證有效）



```python

\# 狀態檔存放在與上傳腳本同目錄的 .upload\_state.json

{

&nbsp;   "file\_path": "C:/path/to/file.zip",

&nbsp;   "file\_size": 2147483648,

&nbsp;   "session\_uri": "https://www.googleapis.com/upload/drive/v3/files?upload\_id=...",

&nbsp;   "bytes\_uploaded": 104857600,

&nbsp;   "created\_at": "2026-05-29T10:00:00",

&nbsp;   "drive\_folder\_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs"

}

