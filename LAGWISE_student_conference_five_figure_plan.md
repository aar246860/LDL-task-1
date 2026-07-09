# LAGWISE 研討會五圖水文敘事版

日期：2026-07-09

這份文件取代原本偏軟體工程的五圖敘事。研討會聽眾主要是水文與地下水讀者，因此圖件順序應接近傳統抽水試驗論文的閱讀習慣：先交代場址與觀測反應，再建立 Theis / classical baseline，接著展示 lagging Darcy model 能解釋什麼水文時間效應，再把模型結果轉成水文參數與不確定性，最後說明哪些結論可以支持現場判讀或補資料決策。

## 敘事主軸

不要把論文講成：

```text
data -> algorithm -> Flow Matching -> runtime -> decision
```

應改成：

```text
aquifer-test evidence -> classical interpretation gap -> lagging response diagnosis
-> parameter and uncertainty interpretation -> field-use boundary
```

也就是說，Flow Matching、MCMC、PEST 不是圖件主角。它們是產生 uncertainty / posterior 的方法層，應放在 caption、methods inset 或補充圖，而不是用軟體流程圖佔掉主圖。

## 五張圖的新順序

| Figure | 水文讀者看到的問題 | 新圖名 |
|---|---|---|
| Fig. 1 | 這是什麼抽水試驗資料？觀測井與反應長什麼樣？ | Pumping-test records and response inventory |
| Fig. 2 | 傳統 Theis / classical baseline 哪裡解釋不足？ | Classical baseline diagnosis |
| Fig. 3 | lagging Darcy model 多解釋了什麼時間效應？ | Lagging response signature |
| Fig. 4 | 這些結果對 K、S、D 與 lag 參數代表什麼不確定性？ | Model-conditioned parameter and uncertainty atlas |
| Fig. 5 | 哪些 case 能解釋？哪些需要補資料或 reference inversion？ | Interpretation boundary and field action |

## Figure 1. Pumping-test records and response inventory

### 目的

第一張圖不要先畫 LAGWISE 流程圖。水文讀者會先想知道：資料來自哪些抽水試驗？井網或井距資訊是否存在？drawdown curve 是否合理？哪些 case 是 analysis-ready，哪些只是 candidate records？

### 建議圖面

做成 3-panel：

| Panel | 內容 |
|---|---|
| A | case inventory：Mayfield、Ambridge、Pullman、Idaho 等公開資料來源與可用 metadata |
| B | drawdown vs log time curves，依 case 或 well 分組 |
| C | data-readiness strip：Q、r、aquifer thickness、T/S source、time series 是否具備 |

### 這張圖要傳達

> The archive contains useful pumping-test responses, but only a subset has enough hydrogeologic metadata for parameter interpretation.

### 學生交付

- `figures/Fig1_pumping_test_response_inventory.pdf`
- `figures/Fig1_pumping_test_response_inventory.svg`
- `figures/Fig1_pumping_test_response_inventory.png`
- `data/processed/well_observations.csv`
- `data/processed/figure_feasibility.csv`
- `captions/Fig1_caption.md`

## Figure 2. Classical baseline diagnosis

### 目的

第二張圖才建立傳統解釋基準。水文讀者熟悉 Theis、Cooper-Jacob、late-time straight-line、residual pattern。這張圖應回答：若用 classical baseline，哪些時間段解釋得好？哪些時間段出現系統性偏差？

### 建議圖面

做成 2 或 3-panel：

| Panel | 內容 |
|---|---|
| A | representative drawdown curve with Theis / classical baseline fit |
| B | residual vs log time，標出 early、middle、late time |
| C | 多 case 的 baseline fit metric，例如 RMSE、BIC、residual autocorrelation |

### 這張圖要傳達

> Classical analysis provides the required reference point; lagging Darcy model is considered only where the baseline leaves structured time-dependent residuals.

### 不要做

- 不要直接把 lagging Darcy model 畫成永遠比較好。
- 不要用一張 algorithm flowchart 取代 baseline diagnosis。
- 不要只報 runtime。

### 學生交付

- `figures/Fig2_classical_baseline_diagnosis.pdf`
- `data/processed/model_fit_metrics.csv`
- `captions/Fig2_caption.md`

## Figure 3. Lagging response signature

### 目的

第三張圖展示 lagging Darcy model 的水文時間效應。這張圖不是「演算法比較」，而是「反應曲線診斷」：lagging terms 如何改變 early-to-middle time drawdown、殘差結構，以及相對 Theis 的偏差。

### 建議圖面

做成 3-panel：

| Panel | 內容 |
|---|---|
| A | Theis vs mild lag vs strong lag 的標準化 response signature |
| B | field case：observed drawdown、classical baseline、lagging Darcy fit |
| C | improvement diagnostic：delta RMSE、delta BIC 或 residual autocorrelation change |

若目前還沒有完整 field fitting，Panel B 可先用一個 source-supported case 的 provisional fit，但 caption 必須標成 demonstration，不可宣稱完成所有 case。

### 這張圖要傳達

> Lagging Darcy model changes the timing and shape of drawdown response; its use is warranted only when those shape changes correspond to observed residual structure.

### no-proxy 規則

- Theis curve 必須用標準 Theis well function。
- lagging Darcy curve 必須用完整 Laplace-domain model 的數值反拉普拉斯。
- 不得用平移 Theis、經驗曲線、低維 surrogate 或 proxy curve。

### 學生交付

- `figures/Fig3_lagging_response_signature.pdf`
- `data/processed/lagging_response_scenarios.csv`
- `data/processed/model_fit_metrics.csv`
- `captions/Fig3_caption.md`

## Figure 4. Model-conditioned parameter and uncertainty atlas

### 目的

第四張圖把結果拉回水文參數。水文讀者關心的是 K、S、D、T 以及 lag-related parameters 的可識別性，而不是 Flow Matching 的軟體流程。Flow Matching 可以作為產生 posterior candidates 的方法，但主圖應是參數與不確定性。

### 建議圖面

做成 3-panel：

| Panel | 內容 |
|---|---|
| A | K / T distribution，僅包含 source-supported rows |
| B | S / D distribution 或 uncertainty intervals |
| C | lag parameter identifiability：tau_q、tau_s、delay index、posterior width 或 q-s tradeoff |

若要保留 Flow Matching，請放成小 inset 或 caption：

> Posterior candidates were screened by Flow Matching and checked against selected reference inversions.

### 這張圖要傳達

> The output is a model-conditioned parameter atlas with explicit uncertainty, not a table of true aquifer constants.

### 不要做

- 不要把「FM train once / sample many / MCMC runtime」當主圖。
- 不要宣稱 tau_q、tau_s 是可跨場址轉移的材料常數。
- 不要對 metadata 不足的 case 硬算 K/S/D。

### 學生交付

- `figures/Fig4_parameter_uncertainty_atlas.pdf`
- `data/processed/mayfield_ksd_parameters.csv`
- `data/processed/posterior_summary.csv`
- `captions/Fig4_caption.md`

## Figure 5. Interpretation boundary and field action

### 目的

最後一張圖給水文讀者實務結論：哪些 case 可以解釋，哪些 case 只能保留為候選資料，哪些需要補 pumping rate、井距、含水層厚度或 reference inversion。

### 建議圖面

做成 2-panel：

| Panel | 內容 |
|---|---|
| A | interpretation class map/table：classical sufficient、lag interpretable、delay-index only、unsupported |
| B | field action：use K/S/D, recover metadata, collect early-time data, run reference inversion |

若有井位座標，Panel A 優先做井網平面圖；若沒有座標，就做 case-by-evidence matrix。

### 這張圖要傳達

> The workflow converts pumping-test evidence and parameter uncertainty into interpretation boundaries and field actions.

### 學生交付

- `figures/Fig5_interpretation_boundary_field_action.pdf`
- `data/processed/well_decision_table.csv` 或 `data/processed/figure_feasibility.csv`
- `captions/Fig5_caption.md`

## 建議的投影片順序

1. **先看資料，不先看方法。** Fig. 1 說明抽水試驗資料與 metadata 完整性。
2. **建立傳統基準。** Fig. 2 顯示 Theis / classical baseline 及其殘差。
3. **再談 lagging Darcy。** Fig. 3 說明 lagging response 的時間效應與何時值得啟用。
4. **回到水文參數。** Fig. 4 顯示 K/S/D 與 lag 參數的不確定性。
5. **收斂到現場決策。** Fig. 5 說明哪些結論可用、哪些需要補資料或 reference inversion。

## 給學生的精簡指令

目前不要再用「Flow Matching 流程圖」或「演算法 runtime 圖」當主軸。五張圖要改成水文抽水試驗論文的證據順序：

1. 抽水試驗資料與 metadata 完整性。
2. Theis / classical baseline 診斷。
3. lagging Darcy response signature 與殘差改善。
4. K/S/D 與 lag 參數的不確定性。
5. interpretation boundary 與 field action。

Flow Matching 只能作為 posterior screening 的方法說明，不能成為主圖敘事。每張圖仍必須有 script、CSV、PDF/SVG/PNG 與 caption。
