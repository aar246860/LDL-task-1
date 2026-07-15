# Skips Academic Steps Storyboard Fixture

## Metadata

- Title: Geometry-looking storyboard that jumps over academic reasoning
- Source artifact: sample paper repository
- Audience: research group
- Story mode: `method`
- Target duration: 90 seconds

## Symbol Glossary

| Symbol | First-use scene | Visual object | Meaning | Unit | Transition |
| --- | --- | --- | --- | --- | --- |
| `K_p` | Scene 4 | pumping-test curve | pumping-derived hydraulic conductivity | m/s | label next to curve |
| `K_s` | Scene 5 | slug-test curve | slug-derived hydraulic conductivity | m/s | label next to curve |

## Scene Table

### Scene 1: Hook - why does the same aquifer give two K values?

- Source-derived rules: `H01`, `H02`, `H06`.
- Storyboard trigger: the video begins with the mismatch before notation.
- Viewer question: why does the same aquifer give two apparent values?
- Visual object: one aquifer cross section with two diverging curves on axes.
- Visual antecedent: aquifer geometry and the two curves.
- Transformation from previous scene: first physical object appears.
- Motion purpose: the curves separate because the measurement mismatch creates the question.
- What the viewer learns: the research object is an apparent contradiction in the same aquifer.
- Minimal on-screen text: "same aquifer, two K values"
- Formula: none.

### Scene 2: Measurements become two curves

- Source-derived rules: `H03`, `H04`, `H13`.
- Storyboard trigger: the viewer needs to see the tests as shapes.
- Viewer question: what did the two tests measure?
- Visual object: pumping and slug data transform into two curves.
- Visual antecedent: aquifer cross section and axes.
- Transformation from previous scene: the aquifer remains while axes grow below it.
- Motion purpose: the curves grow because each test becomes an observable shape.
- What the viewer learns: data are visible curves, not table rows.
- Minimal on-screen text: "tests as curves"
- Formula: none.

### Scene 3: Support volumes are different

- Source-derived rules: `H04`, `H08`, `H13`.
- Storyboard trigger: the two curves need a physical explanation.
- Viewer question: what differs between the two measurements?
- Visual object: two support-volume circles appear inside the aquifer.
- Visual antecedent: aquifer cross section and the two curves.
- Transformation from previous scene: the curves shrink while the aquifer stays fixed.
- Motion purpose: the circles expand because scale changes the interpretation.
- What the viewer learns: the tests read different volumes.
- Minimal on-screen text: "support volumes differ"
- Formula: none.

### Scene 4: Pumping K is named

- Source-derived rules: `H05`, `H15`, `H17`.
- Storyboard trigger: the pumping curve already exists, so the symbol can be named.
- Viewer question: which curve defines `K_p`?
- Visual object: the pumping curve receives a label.
- Visual antecedent: pumping curve and support volume.
- Transformation from previous scene: the blue curve moves into a number line.
- Motion purpose: the label appears because the value is visible.
- What the viewer learns: `K_p` names the pumping interpretation.
- Minimal on-screen text: `K_p`
- Formula: `MathTex(r"K_p")`.
- Symbol handoff: the pumping curve becomes the `K_p` label.
- Formula split plan: single symbol only; no split needed.

### Scene 5: Slug K is named

- Source-derived rules: `H05`, `H15`, `H17`.
- Storyboard trigger: the slug curve already exists, so the symbol can be named.
- Viewer question: which curve defines `K_s`?
- Visual object: the slug curve receives a label.
- Visual antecedent: slug curve and support volume.
- Transformation from previous scene: the orange curve moves into the same number line.
- Motion purpose: the label appears because the value is visible.
- What the viewer learns: `K_s` names the slug interpretation.
- Minimal on-screen text: `K_s`
- Formula: `MathTex(r"K_s")`.
- Symbol handoff: the slug curve becomes the `K_s` label.
- Formula split plan: single symbol only; no split needed.

### Scene 6: Residuals become uncertainty

- Source-derived rules: `H03`, `H04`, `H17`.
- Storyboard trigger: the mismatch needs an uncertainty representation.
- Viewer question: how should residuals be used?
- Visual object: residual dots become density curves and intervals.
- Visual antecedent: two labeled K points.
- Transformation from previous scene: the two points remain while clouds grow into densities.
- Motion purpose: spread shows uncertainty because residuals become a shape.
- What the viewer learns: probability is visible as spread, density, and interval.
- Minimal on-screen text: "soft observation"
- Formula: none.
- Uncertainty shape: density curves, sample cloud, number line, shaded interval.

### Scene 7: Weighted update

- Source-derived rules: `H08`, `H10`, `H12`.
- Storyboard trigger: the two uncertainty shapes need a combined estimate.
- Viewer question: which observation should move the estimate more?
- Visual object: two pull lines move a point on a shared number line.
- Visual antecedent: density curves and K points.
- Transformation from previous scene: density centers move toward a combined point.
- Motion purpose: the point moves because weighting changes the estimate.
- What the viewer learns: the update is a visible balance of evidence.
- Minimal on-screen text: "weighted evidence"
- Formula: none.
- Uncertainty shape: pull lines, density centers, and interval width.

### Scene 8: Return to the aquifer

- Source-derived rules: `H01`, `H06`, `H08`.
- Storyboard trigger: the final estimate must return to the scientific object.
- Viewer question: what does the method change for the original aquifer?
- Visual object: the final interval returns to the aquifer cross section.
- Visual antecedent: final number-line interval and original aquifer geometry.
- Transformation from previous scene: the interval moves back onto the physical object.
- Motion purpose: the abstract estimate returns because the result belongs to the aquifer.
- What the viewer learns: the paper changes how K is interpreted for the aquifer.
- Minimal on-screen text: "K with uncertainty"
- Formula: none.
- Uncertainty shape: final interval beside the aquifer.
