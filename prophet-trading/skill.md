# Skill: prophet-trading

## 目的
用 Samuel-Cahn 上帝不等式設計最優停止交易系統，搭配華羅庚 0.618 定價法設定停利點。

## 使用方式
```bash
pip install yfinance numpy
python prophet_trade.py --ticker RKLB --capital 100 --risk 0.02
```

## 參數
| 參數 | 說明 | 預設值 |
|---|---|---|
| `--ticker` | 股票代號（SpaceX 私有，用 RKLB/SPXC/TSLA 代理） | `RKLB` |
| `--capital` | 投入本金（美元） | `100` |
| `--risk` | 最大可接受虧損比例 | `0.02`（2%） |

## 數學模型
- **Samuel-Cahn (1984)**：最優停止閾值 τ* 滿足 P(X > τ*) = 1/(2n)，保證 E[報酬] ≥ ½ × E[先知]
- **華羅庚 0.618**：停利 T1 = 進場價 + 0.618 × (2σ目標 - 進場價)
- **ATR 停損**：最大虧損 = capital × risk_pct，換算為 σ 倍數

## SpaceX 代理標的
| 代號 | 說明 |
|---|---|
| `RKLB` | Rocket Lab（太空發射競爭者，流動性佳） |
| `SPXC` | SpaceX 相關 ETF（如有上市） |
| `TSLA` | 馬斯克生態，與 SpaceX 消息高度相關 |

## 免責聲明
本技能僅供研究與教育用途，不構成投資建議。
