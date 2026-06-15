# 📊 Solpump History Analysis & Strategy Improvements

> Dataset: **373 rounds** from `solpump_history_all (2).csv` — captured June 15, 2026

---

## ❌ Current System — What's Going Wrong

| Metric | Value |
|---|---|
| Total Bets Recommended | **99** |
| Wins | 37 |
| Losses | 62 |
| **Win Rate** | **37.4%** |
| **PnL (1 unit, 2.5x cashout)** | **-6.50 units** |
| **Expected Value (EV) per bet** | **-6.57%** |

> [!CAUTION]
> The current system is **losing money** on this dataset. Out of 99 bets placed, you lost 62 — a 37% win rate is far below what's needed to break even at 2.5x cashout (which requires **40% win rate** to break even).

### Breakdown of Current System

The current system is mixing **two very different categories** of bets into one:

| Type | Bets | Wins | Win Rate | PnL |
|---|---|---|---|---|
| Normal Bets (≥0.35 SOL pool) | 35 | 14 | 40.0% | **0.00 units** (break-even) |
| Skip-Low-Pool Bets (<0.35 SOL, ≥7 players) | 64 | 23 | **35.9%** | **-6.50 units (losing!)** |

> [!WARNING]
> The **Skip-Low-Pool rule is destroying PnL**. These are 64 bets triggered by small-pool rounds, and they are losing at every cashout multiplier. The normal rules without skip-low-pool are break-even at 2.5x. **Disable this rule immediately.**

---

## 📈 Baseline Probability (All 373 rounds)

This tells us the pure probability of a round crashing at or above each multiplier:

| Cashout Target | Win Probability |
|---|---|
| 1.20x | 80.97% |
| 1.30x | 75.07% |
| 1.40x | 70.78% |
| 1.50x | 65.68% |
| 1.80x | 53.62% |
| 2.00x | 49.33% |
| **2.50x** | **39.95%** |
| 3.00x | 31.37% |

> [!IMPORTANT]
> At 2.5x cashout, the **break-even win rate is 40%**, and the baseline win probability is **39.95%**. So the current system has essentially **no edge** at 2.5x — you're betting coin-flip odds. Your entry rules need to significantly filter for rounds more likely to crash high, or you need to lower your cashout target.

---

## 🚀 Top Strategy Recommendations

### 🥇 Best Strategy (Balanced — No Skip Low Pool)
**➡️ Min Players ≥ 14, Pool ≥ 0.60 SOL, Any Prev Crash, Cashout at 2.20x**

| Metric | Value |
|---|---|
| Bets | 37 |
| Win Rate | **56.8%** |
| PnL | **+9.20 units** |
| EV per bet | **+24.9%** |

### 🥈 Best High-Volume Strategy
**➡️ Min Players ≥ 6, Pool ≥ 0.40 SOL, Prev Crash ≤ 1.30x, Cashout at 2.20x**

| Metric | Value |
|---|---|
| Bets | 60 |
| Win Rate | **51.7%** |
| PnL | **+8.20 units** |
| EV per bet | **+13.7%** |

### 🥉 Best High Win-Rate Strategy (Safest)
**➡️ Min Players ≥ 14, Pool ≥ 0.40 SOL, Any Prev Crash, Cashout at 1.40x**

| Metric | Value |
|---|---|
| Bets | 41 |
| Win Rate | **82.9%** |
| PnL | **+6.60 units** |
| EV per bet | **+16.1%** |

---

## 🔑 Key Findings

### 1. Lower Your Cashout to 1.40x or 2.20x
- At **2.5x**, you need ≥40% win rate to profit, but your filtered bets only reach ~40-57% depending on rules
- At **2.20x**, you need ≥47.6% win rate — achievable with strong filters
- At **1.40x**, you need ≥50% to profit — easily achievable (82.9% win rate with Min 14 players!)

### 2. Minimum Players Filter is the Most Powerful Rule
- Rounds with **≥14 players** consistently perform much better
- The pool of money is larger, meaning more people are betting — reducing variance
- Win rates jump significantly when filtering to high-player rounds

### 3. Pool Size (SOL) Matters — But 0.80 SOL is Too High
- The current ≥0.80 SOL threshold **eliminates too many good rounds**
- Optimal pool threshold: **≥0.40 SOL** — captures more bets while maintaining quality

### 4. Disable the "Skip-Low-Pool" Rule Entirely
- This rule alone caused **-6.50 units** of loss out of the total -6.50 loss
- Essentially ALL the system's losses come from betting in tiny-pool rounds
- Remove it from both the advisor panel and the script

### 5. Prev Crash Rule Can Be Relaxed
- The ≤1.80x threshold misses many profitable rounds where prev crash was 2-5x
- The data shows Prev Crash has **less predictive power** than Players + Pool combined
- You can safely relax to ≤3.0x or even disable it entirely

---

## 🎯 Recommended New Parameters

| Parameter | Current | **Recommended** |
|---|---|---|
| Prev Crash Max | ≤ 1.80x | **Disable or ≤ 3.0x** |
| Min Players | ≥ 14 | **≥ 14** (keep) |
| Min Pool (SOL) | ≥ 0.80 SOL | **≥ 0.40 SOL** |
| Cashout Target | 2.50x | **1.40x or 2.20x** |
| Skip-Low-Pool Rule | Enabled | **❌ DISABLE** |

---

## 💡 Summary

The system has a critical flaw: the **Skip-Low-Pool feature** forces bets into low-pool, low-quality rounds that lose consistently. Disabling it and tightening the cashout to **1.40x** (safe) or **2.20x** (balanced) while keeping **≥14 players** and **≥0.40 SOL pool** produces +16% to +25% EV per bet — a massive improvement over the current -6.57% EV.
