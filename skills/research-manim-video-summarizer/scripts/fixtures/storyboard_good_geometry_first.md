# Geometry-First Storyboard Fixture

## Metadata

- Title: Capacity uncertainty becomes visible width
- Source artifact: sample paper repository
- Audience: research group
- Story mode: `method`
- Target duration: 90 seconds
- Rendering target: `1080p`

## Narrative Spine

- Throughline: uncertainty becomes scientifically useful only after measured and predicted capacities are made comparable as visible geometry.
- Audience starting point: the viewer understands that pile tests produce response curves but has not seen how a transformation ratio is constructed.
- Stakes: compressing the comparison into one reported value hides disagreement and uncertainty.
- Resolution: the final capacity interpretation returns to the pile as a visible interval rather than an isolated number.
- Background scope: 3 source-grounded premises are required before method exposition; verified against fixture Problem statement through Methods Sec. 3.
- Method scope: 6 irreducible operations are required; verified against fixture Methods Sec. 3.1 through Calibration Sec. 4.

## Background Ledger

| ID | Audience gap or premise | Visible evidence | Why it is needed now | Source or claim boundary | Source locator |
| --- | --- | --- | --- | --- | --- |
| `B01` | identical designs can produce different responses | paired pile silhouettes and diverging curves | creates the opening puzzle | limited to the sample source's observed mismatch | fixture source, Problem statement and Fig. 1 |
| `B02` | individual tests can be represented on common axes | curves collapsing into points | makes comparison geometric | each point retains its measured and predicted coordinates | fixture source, Methods Sec. 2 |
| `B03` | error requires a reference relation | diagonal benchmark through the cloud | gives sign and distance meaning | benchmark is a comparison device, not a causal model | fixture source, Methods Sec. 3 and Fig. 2 |

## Method Decomposition Ledger

| ID | Visible input state | One operation | Visible output state | Validity basis | Source locator |
| --- | --- | --- | --- | --- | --- |
| `M01` | one measured response curve with an unlabeled visible peak | select the measured peak | the peak becomes a measured-capacity point labeled `Q_m` | the paper defines measured capacity at that response peak | fixture source, Methods Sec. 3.1 |
| `M02` | measured and predicted response curves with only the measured peak named | select the predicted peak on the comparable curve | a second capacity point labeled `Q_p` appears beside the first | the measured and predicted values have the same unit and visual grain | fixture source, Methods Sec. 3.1 |
| `M03` | two labeled capacity points joined by a visible brace | form the dimensionless ratio from the paired values | separate `R`, equality, numerator, and denominator terms occupy the equation lane | the capacities are already defined and share the same unit | fixture source, Eq. 1 |
| `M04` | repeated ratio values shown as separate dots | aggregate the values along a common number line | a density curve and shaded confidence interval expose their spread | repeated ratio observations define an empirical distribution | fixture source, Methods Sec. 3.2 |
| `M05` | two uncertainty interpretations occupy separate temporary lanes | align both distributions on one common axis | their overlap and disagreement regions become visible | a shared axis preserves direct comparison of location and width | fixture source, Results Fig. 3 |
| `M06` | the original wide confidence interval remains visible | apply the paper's calibration to the interval endpoints | a narrower interval occupies the same axis and reference center | calibration changes uncertainty width while preserving the comparison scale | fixture source, Calibration Sec. 4 |

## Symbol Glossary

| Symbol | First-use scene | Visual object | Meaning | Unit | Transition |
| --- | --- | --- | --- | --- | --- |
| `Q_m` | Scene 4 | measured load-displacement curve | measured capacity | kN | label next to peak point |
| `Q_p` | Scene 5 | prediction curve | predicted capacity | kN | label fades in after the predicted peak appears |
| `R` | Scene 6 | ratio bracket between two peaks | transformation ratio | dimensionless | split MathTex terms appear after the brace makes the comparison visible |

## Scene Table

### Scene 1: Hook - why do two piles with the same design separate?

- Source-derived rules: `H01`, `H02`, `H06`, `H17`, `H19`.
- Narrative beat: hook.
- Background beat: `B01`.
- Background premise: identical designs can produce different responses.
- Method step: none.
- Storyboard trigger: the video begins by showing a visible mismatch before any notation.
- Viewer question: why do two piles with the same design separate?
- Visual object: two identical pile silhouettes appear beside two load-displacement response lines that diverge.
- Visual antecedent: pile silhouettes and diverging curves.
- Transformation from previous scene: first object appears as the physical anchor.
- Motion purpose: the curve separation creates the question because the viewer sees the mismatch.
- Step detail: first draw matched pile silhouettes, then grow the two response lines, then add a short caption and pause on the separation.
- Why this step is valid: because the paper's problem starts from a measured response mismatch, not from notation.
- Transition bridge: from the physical pile pair to the curve mismatch that the method must explain.
- Evidence locator: fixture source, Problem statement and Fig. 1.
- What the viewer learns: the research object is a mismatch between measured behavior and predicted behavior.
- Minimal on-screen text: "same design, different response"
- Frame zones: pile geometry in the center-left, response curves center-right, caption lane at top.
- Keep-clear pairs: caption versus piles and curves; curve labels versus both response curves.
- Transition-frame audit: inspect entry silhouettes, midpoint curve growth, and settled curve separation.
- Layout guard: `assert_scene_layout` for labels, curves, piles, and frame items.
- Formula: none.

### Scene 2: Measurements become a point cloud

- Source-derived rules: `H03`, `H04`, `H13`, `H17`, `H20`.
- Narrative beat: context.
- Background beat: `B02`.
- Background premise: individual tests can be represented on common axes.
- Method step: none.
- Storyboard trigger: the viewer needs to see the dataset as geometry after the mismatch appears.
- Viewer question: what does the paper actually measure?
- Visual object: shared axes appear, followed by four test measurements as a point cloud.
- Visual antecedent: the two curves from Scene 1.
- Transformation from previous scene: the physical comparison fades out before a shared axis system is drawn.
- Motion purpose: points appear because each test becomes one observation.
- Step detail: first draw the shared axes, then reveal the four test points, then add a short caption and hold the cloud.
- Why this step is valid: because each observation has measured and predicted coordinates that can be plotted.
- Transition bridge: from individual response curves to a shared geometric dataset.
- Evidence locator: fixture source, Methods Sec. 2 and dataset definition.
- What the viewer learns: the dataset is a shape, not a table.
- Minimal on-screen text: "tests as points"
- Frame zones: shared axes and point cloud in the center, caption lane at top.
- Keep-clear pairs: caption versus axes; point labels versus the point cloud and ticks.
- Transition-frame audit: inspect entry curves, midpoint shrinking points, and settled cloud.
- Layout guard: `assert_scene_layout` for labels, point cloud, axes, and frame items.
- Formula: none.

### Scene 3: A benchmark line gives geometry

- Source-derived rules: `H04`, `H08`, `H13`, `H17`, `H21`.
- Narrative beat: tension.
- Background beat: `B03`.
- Background premise: error requires a reference relation.
- Method step: none.
- Storyboard trigger: the cloud needs a reference before error can mean anything.
- Viewer question: how do we know which observations are surprising?
- Visual object: a diagonal benchmark line enters the point cloud, followed by two translucent signed regions.
- Visual antecedent: point cloud and fixed axes.
- Transformation from previous scene: the prior view fades out; the same axes and cloud are redrawn before the line and signed regions appear.
- Motion purpose: the line reveals over-prediction and under-prediction regions.
- Step detail: first preserve the cloud, then draw the benchmark line, then shade the two sides of the line.
- Why this step is valid: because error is only interpretable after a reference relation is visible.
- Transition bridge: from raw point geometry to signed distance from a benchmark.
- Evidence locator: fixture source, Methods Sec. 3 and Fig. 2.
- What the viewer learns: distance from the line is the method's error signal.
- Minimal on-screen text: none.
- Frame zones: axes, cloud, diagonal benchmark, and signed regions occupy the central geometry lane; the top caption lane and outer margins remain empty keep-clear zones.
- Keep-clear pairs: the line and signed regions intentionally overlap the axes and cloud; all geometry remains inside the frame.
- Transition-frame audit: inspect entry cloud, midpoint benchmark growth, and settled signed bands.
- Layout guard: `assert_within_frame` for axes, cloud, benchmark, signed regions, and declared data-data overlaps.
- Formula: none.
- Uncertainty shape: signed distance bands around the benchmark line.

### Scene 4: Measured capacity is named after the peak exists

- Source-derived rules: `H05`, `H08`, `H15`, `H17`.
- Narrative beat: mechanism.
- Background beat: none.
- Method step: `M01`.
- Input state: one measured response curve with an unlabeled visible peak.
- Operation: select the measured peak.
- Output state: the peak becomes a measured-capacity point labeled `Q_m`.
- Validity basis: the paper defines measured capacity at that response peak.
- Storyboard trigger: the symbol can be introduced only after the measured peak is visible.
- Viewer question: which visible point does `Q_m` name?
- Visual object: one curve is highlighted and its peak receives a dot.
- Visual antecedent: highlighted load-displacement curve and peak dot.
- Antecedent timing: earlier in this scene before formula.
- Transformation from previous scene: the benchmark view fades out before one measured response curve is drawn.
- Motion purpose: the peak dot appears first because `Q_m` must label an already visible value.
- Step detail: first draw one measured curve, then mark its peak, then attach `Q_m` to that already-visible point.
- Why this step is valid: because measured capacity is defined by the visible peak of the measured curve.
- Transition bridge: from a plotted observation to the physical measured-capacity point it represents.
- Evidence locator: fixture source, Methods Sec. 3.1.
- What the viewer learns: the symbol names a concrete point.
- Minimal on-screen text: `Q_m`
- Formula: `MathTex(r"Q_m")` after the peak point appears.
- Symbol handoff: the peak dot becomes the `MathTex(r"Q_m")` label.
- Formula split plan: single symbol only; no split needed.
- Formula derivation steps: the visible peak point is selected first, then the symbol `Q_m` names that already-visible point.
- Frame zones: measured curve in the central data lane and the `Q_m` explanation in the top formula lane.
- Keep-clear pairs: `Q_m` explanation versus the curve and peak dot.
- Transition-frame audit: inspect entry expanded curve, midpoint peak selection, and settled label.
- Layout guard: `assert_scene_layout` for the symbol, curve, peak, and frame items.
- QA risks: keep the label outside the curve using margin placement.

### Scene 5: Predicted capacity enters as a comparable point

- Source-derived rules: `H05`, `H13`, `H15`, `H17`.
- Narrative beat: mechanism.
- Background beat: none.
- Method step: `M02`.
- Input state: measured and predicted response curves with only the measured peak named.
- Operation: select the predicted peak on the comparable curve.
- Output state: a second capacity point labeled `Q_p` appears beside the first.
- Validity basis: the measured and predicted values have the same unit and visual grain.
- Storyboard trigger: comparison needs the predicted peak after the measured peak is named.
- Viewer question: what is the comparable predicted value?
- Visual object: prediction curve overlays the measured curve.
- Visual antecedent: measured curve with `Q_m` label.
- Antecedent timing: earlier in this scene before formula.
- Transformation from previous scene: the measured-capacity view fades out and is reconstructed with its named peak before the prediction is added.
- Motion purpose: the second peak makes comparison possible.
- Step detail: first draw the measured curve with its `Q_m` point and label, then overlay the prediction curve and peak, then attach the `Q_p` explanation.
- Why this step is valid: because comparison requires measured and predicted values at the same visual grain.
- Transition bridge: from one named capacity to a paired predicted capacity on the same geometry.
- Evidence locator: fixture source, Methods Sec. 3.1.
- What the viewer learns: `Q_p` is a second visible capacity.
- Minimal on-screen text: `Q_p`
- Formula: `MathTex(r"Q_p")` after the predicted peak appears.
- Symbol handoff: the predicted peak becomes the `MathTex(r"Q_p")` label.
- Formula split plan: single symbol only; no split needed.
- Formula derivation steps: the predicted peak is shown first, then `Q_p` is introduced as the label for that point.
- Frame zones: paired curves in the central data lane, peak labels in opposite margins, caption band below.
- Keep-clear pairs: `Q_m` versus `Q_p`; both symbols versus curves, peak dots, axes, and ticks.
- Transition-frame audit: inspect entry measured state, midpoint prediction overlay, and settled paired peaks.
- Layout guard: `assert_scene_layout` for both symbols, curves, peaks, axes, and frame items.
- QA risks: offset the two peak labels so they do not overlap.

### Scene 6: Ratio appears from geometry

- Source-derived rules: `H05`, `H08`, `H16`, `H17`, `H18`.
- Narrative beat: mechanism.
- Background beat: none.
- Method step: `M03`.
- Input state: two labeled capacity points joined by a visible brace.
- Operation: form the dimensionless ratio from the paired values.
- Output state: separate `R`, equality, numerator, and denominator terms occupy the equation lane.
- Validity basis: the capacities are already defined and share the same unit.
- Storyboard trigger: the ratio can appear after both capacities are visible.
- Viewer question: how does the visual comparison become one number?
- Visual object: a brace spans two labeled capacity points, the fraction appears above it, and `R =` completes the equation.
- Visual antecedent: two labeled peak points and the brace between them.
- Antecedent timing: prior Scene 5.
- Transformation from previous scene: the paired-curve view fades out before the two labeled values and their brace are reconstructed.
- Motion purpose: the brace constructs the ratio from the measured and predicted points.
- Step detail: first show the two labeled points joined by a brace, then reveal `Q_m/Q_p`, then add separate `R` and equality terms.
- Why this step is valid: because the ratio compares two already-defined capacities with the same unit.
- Transition bridge: from two labeled points to a dimensionless comparison formula.
- Evidence locator: fixture source, Eq. 1 and Methods Sec. 3.1.
- What the viewer learns: the formula summarizes an already visible comparison.
- Minimal on-screen text: `R = Q_m / Q_p`
- Formula: split `MathTex(r"R")`, `MathTex(r"=")`, `MathTex(r"\frac{Q_m}{Q_p}")`.
- Symbol handoff: the existing `Q_m` and `Q_p` labels establish the numerator and denominator before the fraction appears.
- Formula split plan: reveal `\frac{Q_m}{Q_p}` first, then add `R` and `=` as a separate prefix group.
- Formula derivation steps: show the brace between the defined values, reveal their fraction, then introduce `R =` as the name of that ratio.
- Frame zones: source peaks in the lower geometry lane, split equation terms in the upper formula lane.
- Keep-clear pairs: equation terms versus each other, source curves, brace, and frame edge.
- Transition-frame audit: inspect entry brace, midpoint symbol handoff, and settled ratio equation.
- Layout guard: `assert_scene_layout` for formula terms, labels, source geometry, and frame items.
- QA risks: reserve an equation lane above the axes.

### Scene 7: Uncertainty becomes a distribution

- Source-derived rules: `H03`, `H04`, `H08`, `H17`.
- Narrative beat: evidence.
- Background beat: none.
- Method step: `M04`.
- Input state: repeated ratio values shown as separate dots.
- Operation: aggregate the values along a common number line.
- Output state: a density curve and shaded confidence interval expose their spread.
- Validity basis: repeated ratio observations define an empirical distribution.
- Storyboard trigger: multiple ratios need a shape before uncertainty is discussed.
- Viewer question: how wide is the result, not just where is its center?
- Visual object: many ratio values form a density curve and shaded confidence interval.
- Visual antecedent: ratio dots from Scene 6.
- Transformation from previous scene: the ratio equation fades out before repeated ratio dots appear on a common number line.
- Motion purpose: spread shows uncertainty as shape.
- Step detail: first drop ratio values onto a number line, then build the density, then draw the confidence interval.
- Why this step is valid: because repeated ratios define a spread, and spread is the empirical uncertainty signal.
- Transition bridge: from a single ratio formula to the distribution of ratio values.
- Evidence locator: fixture source, Methods Sec. 3.2 and dataset table.
- What the viewer learns: probability is visible as width, density, and interval.
- Minimal on-screen text: "ratios become a distribution"
- Formula: none.
- Uncertainty shape: density curve, sample cloud, number line, and shaded confidence interval.
- Frame zones: number line and ratio dots below the density and interval, with a caption lane at top.
- Keep-clear pairs: top caption versus density, interval, number line, and ratio dots.
- Transition-frame audit: inspect entry ratio dots, midpoint accumulation, and settled density with interval.
- Layout guard: `assert_scene_layout` for annotations, distribution, points, interval, axis, and frame items.
- QA risks: keep text in a caption band below the distribution.

### Scene 8: Competing interpretations share one axis

- Source-derived rules: `H07`, `H08`, `H13`, `H17`.
- Narrative beat: evidence.
- Background beat: none.
- Method step: `M05`.
- Input state: two uncertainty interpretations occupy separate temporary lanes.
- Operation: align both distributions on one common axis.
- Output state: their overlap and disagreement regions become visible.
- Validity basis: a shared axis preserves direct comparison of location and width.
- Storyboard trigger: the first uncertainty shape needs a same-axis comparison.
- Viewer question: which conclusion survives a competing interpretation?
- Visual object: two density curves move from separate vertical lanes onto one common axis, then their overlap region appears.
- Visual antecedent: the first density curve and interval.
- Transformation from previous scene: the prior distribution fades out before two competing distributions appear in separate lanes.
- Motion purpose: overlap reveals where conclusions are stable.
- Step detail: first keep the original density fixed, then grow the competing density, then mark their overlap.
- Why this step is valid: because competing interpretations must be compared on a common axis.
- Transition bridge: from one uncertainty shape to a same-axis comparison of two shapes.
- Evidence locator: fixture source, Results Fig. 3.
- What the viewer learns: comparison happens in the same geometry.
- Minimal on-screen text: none.
- Formula: none.
- Uncertainty shape: overlapping density curves and shared confidence bands.
- Frame zones: separate density lanes use the upper and lower halves; the aligned comparison occupies the central axis.
- Keep-clear pairs: density-density and overlap-region intersections are intentional; all geometry remains inside the frame.
- Transition-frame audit: inspect entry separated densities, midpoint same-axis alignment, and settled overlap region.
- Layout guard: `assert_within_frame` for both density states, common axis, overlap region, and declared data-data overlaps.
- QA risks: preserve each curve's identity during alignment and keep the overlap fill subordinate to both outlines.

### Scene 9: Calibration narrows the band

- Source-derived rules: `H08`, `H10`, `H12`, `H17`.
- Narrative beat: revelation.
- Background beat: none.
- Method step: `M06`.
- Input state: the original wide confidence interval remains visible.
- Operation: apply the paper's calibration to the interval endpoints.
- Output state: a narrower interval occupies the same axis and reference center.
- Validity basis: calibration changes uncertainty width while preserving the comparison scale.
- Storyboard trigger: the method's value must appear as a changed object.
- Viewer question: what did calibration visibly improve?
- Visual object: a shaded band contracts after the calibration step.
- Visual antecedent: the wide confidence band from Scene 8.
- Transformation from previous scene: the interval endpoints move inward.
- Motion purpose: the shrinking band shows the method's value as a change in uncertainty width.
- Step detail: first show the original wide band, then move the endpoints inward, then hold on the narrowed band.
- Why this step is valid: because calibration changes the uncertainty width that the viewer already saw.
- Transition bridge: from the competing uncertainty bands to the calibrated uncertainty band.
- Evidence locator: fixture source, Calibration Sec. 4 and Results Fig. 4.
- Aha object: the interval endpoints move inward while the center remains fixed.
- What the viewer learns: the method changes a visual object, not just a number.
- Minimal on-screen text: "calibration narrows the interval"
- Formula: none.
- Uncertainty shape: shrinking shaded band and moving interval endpoints.
- Frame zones: interval and axis in the lower center, with the explanatory caption in the top lane.
- Keep-clear pairs: caption versus the narrowed interval and common axis.
- Transition-frame audit: inspect entry wide band, midpoint endpoint motion, and settled narrow band.
- Layout guard: `assert_scene_layout` for label, interval, endpoints, axis, and frame items.
- QA risks: avoid overlapping the band label with the endpoints.

### Scene 10: Return to the pile

- Source-derived rules: `H01`, `H06`, `H08`, `H17`, `H21`.
- Narrative beat: return.
- Background beat: none.
- Method step: none.
- Storyboard trigger: the final abstraction must return to the scientific object.
- Viewer question: what does the paper change for the original pile?
- Visual object: the original pile reappears, then the final interval is drawn beside it and connected to the physical object.
- Visual antecedent: calibrated interval and original pile geometry.
- Transformation from previous scene: the calibrated interval view fades out before the physical pile is reconstructed and linked to the interval.
- Motion purpose: the abstract uncertainty returns to the scientific object.
- Step detail: first draw the pile, then draw the final interval beside it with a connecting line, then add the bounded interpretation caption.
- Why this step is valid: because the paper's conclusion is about pile capacity in the original physical domain.
- Transition bridge: from abstract uncertainty geometry back to the original pile design object.
- Evidence locator: fixture source, Conclusions Sec. 5 and final design figure.
- What the viewer learns: the paper changes how capacity is interpreted for the pile.
- Minimal on-screen text: "capacity returns to the physical pile"
- Formula: none.
- Uncertainty shape: final design band beside the pile.
- Frame zones: original pile in the center-left, final interval in the center-right, claim boundary in the caption band.
- Keep-clear pairs: interval label versus pile label, interval endpoints, soil layers, and caption.
- Transition-frame audit: inspect entry abstract interval, midpoint return motion, and settled pile interpretation.
- Layout guard: `assert_scene_layout` for labels, pile, interval, soil geometry, and frame items.
- QA risks: keep the final band readable beside the pile, not on top of the pile label.
