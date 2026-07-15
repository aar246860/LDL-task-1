# 3B1B Style Contract

Use this contract before approving any storyboard or render.
For strict storyboards, also enforce
`references/3b1b-harness-evidence-map.md`.
This is an independent pedagogical contract, not an affiliation with or
endorsement by 3Blue1Brown, TED, or TEDx; do not reproduce their branding.

## Core Principles

1. Geometry before algebra.
   - Introduce points, curves, surfaces, distributions, or intervals first.
   - Add formulas only after the viewer has seen the object the formula describes.

2. Meaningful continuity before cuts.
   - Use explicit transforms only when source and target are states of the same
     scientific object or genuinely corresponding mathematical shapes.
   - Guard a positioned target copy before an explicit transform. The strict
     checker rejects `.animate` because its endpoint is not independently auditable.
   - Replace unrelated prose, captions, and CJK strings with `FadeOut` followed
     by `FadeIn`; never force unrelated glyphs through a geometric transform.
   - Use cuts only at true chapter boundaries.

3. One idea per scene.
   - Every scene should answer a simple question: what changes, what is compared, or what is inferred?
   - Remove decorative motion that does not change interpretation.

4. Data become shapes.
   - Tables become point clouds, axes, fields, curves, histograms, or number lines.
   - Uncertainty becomes distributions, intervals, clouds, or shaded bands.

5. Research language remains discipline-native.
   - For geotechnical work, prefer load-displacement curves, criterion lines, capacity intervals, pile symbols, reliability maps, and transformation-factor axes.
   - Avoid software-engineering diagrams unless the paper is about software.

6. Scene count follows scientific detail.
   - Map every background premise to one `Bxx` scene.
   - Map every atomic input-operation-output method step to one `Mxx` scene.
   - Never compress two ledger items into one frame to meet a duration target.

7. One throughline creates the story.
   - Move from concrete hook through context, tension, mechanism, evidence, and
     revelation before returning to the original scientific object.
   - Treat story as a path through evidence, not as dramatic decoration.

## Required Visual Checks

- Dark or neutral background with high-contrast geometry.
- CJK text fits within safe bounds and never overlaps axes or data.
- Text is sparse; important meaning is carried by geometry.
- Each symbol is defined before use.
- Each scene cites source-derived `Hxx` rules and a storyboard trigger.
- Each ledger row and scene cites a paper-specific evidence locator; Hxx rules
  justify visual design, not the scientific claim itself.
- Each scene owns at most one `Bxx` or `Mxx` item and names one narrative beat.
- Every scene names frame zones, keep-clear pairs, transition frames, and a
  runtime layout guard.
- Every revelation scene names one visible Aha object.
- Long formulas are split or delayed.
- Final scene returns to the physical or scientific object, not only a model output.

## Banned Patterns

- Spreadsheet-like tables as the main scene.
- Bullet-heavy slides.
- "AI pipeline" boxes as the main contribution.
- Unverified blob-only video links.
- Formula-first explanations.
- Static screenshots pretending to be animation.
- Tiny axis labels, crowded legends, or text on top of curves.
