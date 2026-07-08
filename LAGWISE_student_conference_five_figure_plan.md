# LAGWISE 學生研討會五圖交付規劃

日期：2026-07-09

用途：給老師追蹤學生目前進度，並給學生作為研討會論文五張圖的最小交付標準。這份文件採用「可以在研討會防守」作為判準，不以程式是否能開圖窗作為完成。

## 目前 GitHub 狀態

學生 repo：`Fanny-Tsai/LDL-task-1`

目前最新進度：

| 項目 | 狀態 |
|---|---|
| 最新學生 commit | `8df0f18`，commit message `2026/7/5` |
| 新增內容 | `LDL model -task2` |
| PR #1 | open、clean、mergeable，但老師端帳號只有 READ 權限，不能代為 merge |
| PR comment | 已留言請 repo owner 或具 write 權限者 merge |
| 正式圖檔 | 0 張。repo 目前沒有可交付的 `PDF/SVG/PNG` figure |
| 可執行圖窗 | 至少 1 張。`LDL model -task2` 會畫 `Observed vs Fitted Drawdown` |

目前判斷：學生有進度，但還沒有完成研討會五圖。現階段只算 Fig. 2 / model-fitting demo 的初步程式雛形。

## 五張圖的研討會定位

研討會版不主張 LAGWISE 取代 PEST、DREAM、MCMC。五張圖要共同傳達：

> Lagging Darcy model interpretation needs a defensible workflow: first compare with Theis/classical baseline, then screen USGS data readiness, then use Flow Matching as fast multi-well posterior screening, and finally translate uncertainty into decision rules.

## Figure 1. LAGWISE-C workflow and evidence gate

### 目的

第一張圖用來回答 reviewer 的核心質疑：本研究不是另一個通用反算器，而是 Lagging Darcy model 是否值得啟用的 triage workflow。

### 最終呈現結果

左到右流程圖：

```text
USGS / field drawdown records
-> Theis or classical baseline
-> Lagging Darcy model
-> Lag-worthiness / data-readiness gate
-> Flow Matching screening
-> Reference inversion check: PEST / MCMC
-> Decision example
```

### 圖上必須出現

- `Lagging Darcy model`，不可寫 `dual_pathway`。
- `Reference inversion`，不可寫 `anchor/anchoring`。
- 明確註記：`not a replacement inverse solver`。

### 學生目前進度

0%。學生 repo 尚未有 workflow figure。

### 完成定義

- 輸出 `figures/Fig1_LAGWISE_C_workflow.pdf`
- 同時輸出 `SVG` 與 `PNG`
- caption 說明 LAGWISE-C 是 triage workflow，而不是 PEST/MCMC 替代品

## Figure 2. Lagging Darcy model vs Theis time-drawdown curve

### 目的

用同一組水文參數對照 Theis model 與 Lagging Darcy model，凸顯 Lagging Darcy model 的時間效應。

### 最終呈現結果

建議做 2-panel：

| Panel | 內容 |
|---|---|
| A | drawdown vs log time：Theis baseline、mild lag、strong lag |
| B | difference from Theis：Lagging Darcy minus Theis |

### 必須用完整模型

- Theis curve 用標準 Theis well function。
- Lagging Darcy curve 用完整 Laplace-domain model 的數值反拉普拉斯。
- 不得用平移 Theis、經驗曲線、低維 surrogate 或 proxy curve。

### 學生目前進度

約 30%。已有 LDL 計算與 fitting demo，但還缺：

- Theis baseline。
- mild/strong lag 情境比較。
- difference panel。
- 正式輸出圖檔。
- 單位與無因次時間說明。

### 完成定義

- 輸出 `figures/Fig2_lagging_darcy_vs_theis.pdf`
- 圖中至少有 Theis、mild lag、strong lag 三條線
- caption 明確說明時間延遲效應，不宣稱 Lagging Darcy 永遠較佳

## Figure 3. USGS drawdown records and K/S/D distribution

### 目的

展示學生能讀入公開 USGS 洩降資料，並只在 metadata 足夠時提供 K/S/D 物理參數分布。

### 最終呈現結果

建議做 3-panel：

| Panel | 內容 |
|---|---|
| A | USGS drawdown curves，依 case/well 分組 |
| B | Mayfield K distribution from reported T and aquifer thickness |
| C | Mayfield S and D distribution |

### no-proxy gate

只有具備下列資料者才能輸出 K/S/D：

- drawdown curve
- pumping rate Q
- radius or well distance r
- reported T/S or可追溯反算來源
- aquifer thickness

若缺資料，只能列在 feasibility table，不可硬算 K/S/D。

### 學生目前進度

0%。學生 repo 尚未處理 USGS Excel / PDF metadata，也沒有 K/S/D 圖。

### 完成定義

- 輸出 `figures/Fig3_usgs_drawdown_ksd.pdf`
- 輸出 `data/processed/well_observations.csv`
- 輸出 `data/processed/mayfield_ksd_parameters.csv`
- caption 說明只有 source-supported case 才做物理解釋

## Figure 4. Flow Matching screening vs reference inversion

### 目的

把 Flow Matching 定位成多井快速篩選工具，而不是取代 PEST/MCMC。

### 最終呈現結果

建議做 2-panel：

| Panel | 內容 |
|---|---|
| A | workflow schematic：many wells -> train once -> sample many -> selected reference inversion |
| B | runtime comparison：Flow Matching train once、Flow Matching sample many curves、Repeated MCMC/PEST |

### 訊息邊界

可說：

> Flow Matching supports fast screening before selected reference inversion.

不可說：

> Flow Matching replaces PEST or MCMC.

### 學生目前進度

0%。學生 repo 尚未有 Flow Matching code、runtime table 或 comparison figure。

### 完成定義

- 輸出 `figures/Fig4_flow_matching_reference_inversion.pdf`
- runtime 數字必須有來源或標示為 current manuscript timing
- caption 說明 MCMC/PEST 是 reference inversion layer

## Figure 5. Decision example

### 目的

把模型與資料不確定性轉成決策：哪些 case 可以解釋 K/S/D，哪些需要補資料或進 reference inversion。

### 最終呈現結果

建議做 2-panel：

| Panel | 內容 |
|---|---|
| A | data-readiness heatmap：curve、Q、r、thickness 是否具備 |
| B | action table：plot K/S/D、download metadata、recover pumping rate、run reference inversion |

### 學生目前進度

0%。學生 repo 尚未有 decision gate 或 data-readiness table。

### 完成定義

- 輸出 `figures/Fig5_decision_example.pdf`
- 輸出 `data/processed/figure_feasibility.csv`
- 明確列出每個 USGS case 的可用資料與下一步動作

## 最小交付順序

建議學生不要五張一起做。請按下列順序：

1. 先 merge PR #1，修正 `waterererer.py` 的無因次時間與 `kappa` 問題。
2. 完成 Fig. 2，因為它是目前最接近完成的一張。
3. 補 USGS data reader 與 metadata gate，完成 Fig. 3 和 Fig. 5。
4. 用目前 manuscript timing 先做 Fig. 4 的 defensible version。
5. 最後再畫 Fig. 1，整合整個故事。

## 目前進度總結

| Figure | 狀態 | 可否放研討會 |
|---|---:|---|
| Fig. 1 workflow | 0% | 不可 |
| Fig. 2 Lagging Darcy vs Theis | 約 30% | 不可 |
| Fig. 3 USGS K/S/D | 0% | 不可 |
| Fig. 4 Flow Matching vs reference inversion | 0% | 不可 |
| Fig. 5 decision example | 0% | 不可 |

總結：目前正式五圖是 0/5。若把 task 2 的互動式擬合圖算成「雛形」，則只有 Fig. 2 有初步基礎。
