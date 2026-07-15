# Math Symbol And Layout Contract

Use this contract before writing Manim code and again before approving a render.

## Formula Rendering

- Use `MathTex` for mathematical symbols and formulas by default.
- Use `Tex` only when the object is prose that contains a small amount of inline
  math.
- Do not put mathematical formulas in `Text`.
- Avoid Unicode math symbols inside `Text`; write the mathematical expression in
  LaTeX instead.
- Split long equations into transformable terms. A term should be able to move,
  fade, align, or transform independently.

## Symbol Glossary

Before animation code, write a symbol glossary. Every symbol needs:

| Field | Requirement |
| --- | --- |
| Symbol | LaTeX symbol exactly as it will appear in `MathTex`. |
| First-use scene | Scene number where the symbol first appears. |
| Visual object | The point, curve, field, interval, distribution, sample cloud, or physical object defining it. |
| Meaning | Discipline-native meaning, not only a generic label. |
| Unit | Unit, dimension, or explicit "dimensionless". |
| Transition | How the symbol enters: label, transform from geometry, bracket, brace, axis tick, color match, or legend. |

If the glossary cannot be filled, the storyboard is not ready for Manim code.

## Safe Layout Rules

- Reserve a caption band at the bottom or top; do not let data enter it.
- Put formulas in a margin, caption band, or dedicated equation lane unless the
  formula is attached to a specific object with a leader or brace.
- Position labels with `next_to`, `arrange`, `to_edge`, `to_corner`, or a safe
  helper. Avoid raw coordinates for labels unless there is a documented reason.
- Keep labels outside axes, curves, point clouds, and shaded regions.
- If labels or formulas share a frame with axes, curves, fields, aquifer blocks,
  point clouds, or shaded bands, call `assert_scene_layout` for that scene's
  settled state. It checks label-label clearance, label-data clearance, and
  frame boundaries. Use `place_label_clear` when placement must search for a
  clear side. A syntactic placement call such as `next_to` is not sufficient.
- If support-volume rings, halos, uncertainty bands, or interval markers belong
  to a physical object such as an aquifer block or specimen diagram, add
  `assert_inside` so the shape stays inside that object. If a ring intentionally
  extends beyond the crop, the storyboard must say why before the render is
  accepted.
- Containment inside circles, ellipses, polygons, and other curved containers
  must use sampled object boundaries and point-in-shape clearance. A bounding
  box comparison is insufficient because it accepts objects in empty corners
  outside the visible container.
- Keep coordinate axes outside physical object fills unless the axis is itself
  the object being explained. A y-axis crossing an aquifer block, specimen, or
  field is a layout failure.
- Put `K`, `Y`, residual, and weighted-observation labels in a lane or offset
  them away from curves, arrows, pull lines, and density peaks. Labels on top of
  data geometry fail the harness even if they are mathematically correct.
- Call the guard after the relevant mobjects have been positioned and before
  every `add` or `play` call that establishes a settled state. A guard in a
  different scene, helper, or earlier settled state does not provide coverage.
  Empty `labels`, `blockers`, or `frame_items` collections fail the contract.
- Pass `scene=self` and list every object about to appear in `pending_items`.
  `frame_items` must contain every family member already visible in the scene
  plus every pending object. For a pure-geometry state, call
  `assert_within_frame(frame_items, scene=self, pending_items=pending_items)`.
- Include every label, formula, caption, legend, and symbol in the `labels`
  argument. Include every axis, curve, point cloud, band, field, and physical
  object that text must not obscure in `blockers`. Include all visible mobjects
  in `frame_items`. Every label and blocker must also belong to the current
  scene or `pending_items`; a detached object cannot satisfy the role lists.
- The strict static check rejects `.animate` because it cannot independently
  certify the final geometry. Construct and position a role-traceable target
  copy, guard that target with the current state, and then transform the same
  scientific object. Replace unrelated text with fades rather than transforms.
- Data-data overlap is allowed only when scientifically intentional and named in
  the storyboard. Pass every allowed top-level pair explicitly through
  `intentional_overlaps=[(curve_a, curve_b), ...]`; an undeclared overlap fails
  even when both objects are data geometry. Text-text and text-data overlap are
  never accepted.
- Use max-width fitting for CJK text and long captions.
- Add rendered-frame review before final approval. The contact sheet is only a
  navigation aid and cannot prove collision freedom. The reviewer must check text
  clipping, text/text overlap, text/data overlap, crowded formulas, and the
  entry, midpoint, and settled state of every transition, then record those
  results in the visual-QA manifest.
- Every reviewed frame needs its exact MP4 frame index and image SHA-256. All
  reviewed indices and RGB pixel arrays must be globally unique, and FFmpeg must
  decode each declared MP4 frame to exactly the recorded pixels.

## Long Equation Pattern

Prefer:

```python
terms = VGroup(
    MathTex(r"R"),
    MathTex(r"="),
    MathTex(r"\\frac{Q_{measured}}{Q_{predicted}}"),
)
terms.arrange(RIGHT, buff=0.18)
```

Avoid:

```python
Text("R = Q_measured / Q_predicted")
MathTex(r"R = \\frac{Q_{measured}}{Q_{predicted}} + \\cdots")
```

The preferred form lets the animation transform, color, or isolate each term.
