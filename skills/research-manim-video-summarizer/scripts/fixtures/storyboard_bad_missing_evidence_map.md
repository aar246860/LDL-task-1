# Missing Evidence Map Storyboard Fixture

## Metadata

- Title: Looks visual but lacks source-derived triggers
- Source artifact: sample paper repository
- Audience: research group
- Story mode: `method`
- Target duration: 90 seconds

## Symbol Glossary

| Symbol | First-use scene | Visual object | Meaning | Unit | Transition |
| --- | --- | --- | --- | --- | --- |
| `Q_m` | Scene 4 | measured curve peak | measured capacity | kN | label appears near peak |
| `Q_p` | Scene 5 | predicted curve peak | predicted capacity | kN | label appears near peak |
| `R` | Scene 6 | ratio bracket | transformation ratio | dimensionless | equation terms form from labels |

## Scene Table

### Scene 1: Hook - why do matching designs diverge?

- Visual object: two pile silhouettes in layered soil, with curves that diverge on an axis.
- Transformation from previous scene: first geometry appears and the curves grow from the piles.
- Purposeful motion: the separation creates the question because it reveals a mismatch.
- What the viewer learns: the research object is the mismatch between measured and predicted response.
- Minimal on-screen text: "same design, different response"
- Formula: none.

### Scene 2: Measurements become geometry

- Visual object: measured cases transform into a point cloud on a shared axis.
- Transformation from previous scene: curves shrink into points, and the camera keeps the axis fixed.
- Purposeful motion: each move shows because one test becomes one observation.
- What the viewer learns: the dataset is a visible shape, not a table.
- Minimal on-screen text: "tests as points"
- Formula: none.

### Scene 3: Benchmark line

- Visual object: a benchmark line grows through the point cloud.
- Transformation from previous scene: the cloud remains while the line expands.
- Purposeful motion: the line reveals because distance from it becomes error.
- What the viewer learns: error has geometry.
- Minimal on-screen text: "benchmark"
- Formula: none.

### Scene 4: Measured peak

- Visual object: one curve expands from a cloud point and a peak dot appears.
- Transformation from previous scene: the cloud point morphs into a load-displacement curve.
- Purposeful motion: the peak label appears because the point already exists.
- What the viewer learns: `Q_m` names a visible measured value.
- Minimal on-screen text: `Q_m`
- Formula: `MathTex(r"Q_m")` after the peak appears.

### Scene 5: Predicted peak

- Visual object: a predicted curve overlays the measured curve.
- Transformation from previous scene: the benchmark line morphs into a prediction curve.
- Purposeful motion: the second peak shows because comparison needs two values.
- What the viewer learns: `Q_p` is a comparable visible capacity.
- Minimal on-screen text: `Q_p`
- Formula: `MathTex(r"Q_p")`.

### Scene 6: Ratio construction

- Visual object: a bracket spans the two peaks, then splits into an equation lane.
- Transformation from previous scene: labels move into formula terms.
- Purposeful motion: terms move because the formula summarizes the geometry.
- What the viewer learns: `R` is built from a visible comparison.
- Minimal on-screen text: `R = Q_m / Q_p`
- Formula: `MathTex(r"R")`, `MathTex(r"=")`, `MathTex(r"\frac{Q_m}{Q_p}")`.

### Scene 7: Uncertainty distribution

- Visual object: ratio values fall onto a number line and accumulate into a distribution.
- Transformation from previous scene: ratio dots move into a density curve with an interval.
- Purposeful motion: spread becomes visible because uncertainty needs shape.
- What the viewer learns: probability appears as width, density, cloud, and shaded band.
- Minimal on-screen text: "uncertainty width"
- Formula: none.

### Scene 8: Shared axis comparison

- Visual object: two distributions share one ratio axis.
- Transformation from previous scene: the first distribution remains while the second grows.
- Purposeful motion: the overlay compares because overlap reveals stable conclusions.
- What the viewer learns: competing interpretations can be compared in one geometry.
- Minimal on-screen text: "same axis"
- Formula: none.

### Scene 9: Calibration narrows the band

- Visual object: a shaded band shrinks after calibration.
- Transformation from previous scene: interval endpoints move inward.
- Purposeful motion: the band changes because the method changes uncertainty width.
- What the viewer learns: calibration is visible as a changed shape.
- Minimal on-screen text: "narrower band"
- Formula: none.

### Scene 10: Return to original pile

- Visual object: the interval returns to the original pile design diagram.
- Transformation from previous scene: the distribution compresses into a design band on the physical object.
- Purposeful motion: the abstract band moves back because the result belongs to the scientific object.
- What the viewer learns: the paper changes how pile capacity is interpreted.
- Minimal on-screen text: "capacity with uncertainty"
- Formula: none.
