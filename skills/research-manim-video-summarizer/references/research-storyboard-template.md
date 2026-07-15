# Research Storyboard Template

Use this structure for a variable-length research video whose duration follows the evidence and method decomposition.

## Metadata

- Title:
- Source artifact:
- Audience:
- Story mode: `concept`, `method`, `result`, or `review-response`
- Target duration:
- Rendering target: `720p`, `1080p`, or `4k`

## Research Extraction

- Core research question:
- Physical or scientific system:
- Input data:
- Main method:
- Reference or benchmark:
- Uncertainty or error treatment:
- Main conclusion:

## Narrative Spine

- Throughline:
- Audience starting point:
- Stakes:
- Resolution:
- Background scope: begin with the exact number of source-grounded `Bxx` premises, for example `3 premises needed to establish ...`; strict public-talk mode requires at least one.
- Method scope: begin with the exact number of irreducible `Mxx` operations, for example `6 operations needed to derive ...`.

## Background Ledger

Create one row for every independent premise or audience knowledge gap. Do not
merge rows to shorten the video.

| ID | Audience gap or premise | Visible evidence | Why it is needed now | Source or claim boundary | Source locator |
| --- | --- | --- | --- | --- | --- |
| `B01` |  |  |  |  |  |

## Method Decomposition Ledger

Create one row for every irreducible scientific operation. Split a row when it
contains two independent verbs, two outputs, or both a representation change
and an inference.

| ID | Visible input state | One operation | Visible output state | Validity basis | Source locator |
| --- | --- | --- | --- | --- | --- |
| `M01` |  |  |  |  |  |

## Symbol Glossary

Complete this table before code generation. Use one row for every symbol that appears in `MathTex`.

| Symbol | First-use scene | Visual object | Meaning | Unit | Transition |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Scene Table

For each scene, include these fields:

1. Scene number and title.
2. Source-derived rules: cite `Hxx` rules from
   `references/3b1b-harness-evidence-map.md`.
3. Narrative beat: exactly one of `hook`, `context`, `tension`, `mechanism`,
   `evidence`, `revelation`, `return`, or `resolution`.
4. Background beat: exactly one `Bxx`, or `none`.
5. Background premise: when a `Bxx` appears, copy its `Audience gap or premise`
   ledger cell exactly; omit this field when `Background beat` is `none`.
6. Method step: exactly one `Mxx`, or `none`; a scene cannot have both a
   background beat and method step.
7. Storyboard trigger: the concrete event that makes this scene necessary now.
8. Viewer question: the question or tension the scene resolves.
9. Visual object.
10. Visual antecedent: the object already visible before symbols or formulas.
11. Antecedent timing, when formulas appear: exactly `earlier in this scene before formula` or `prior Scene N`, with `N` smaller than the current scene.
12. Transformation from the previous scene.
13. Motion purpose: why the motion changes understanding.
14. Step detail: the ordered micro-steps shown in this scene; do not compress a multi-step inference into one sentence.
15. Why this step is valid: the paper-specific reason, assumption, measurement relation, or evidence that justifies the step.
16. Transition bridge: how the previous visible object becomes the next visible object or claim.
17. Evidence locator: exact section, equation, figure, table, page, dataset, appendix, or repository path supporting this scene.
18. Input state, operation, output state, and validity basis when an `Mxx` appears. Copy all four ledger cells exactly and use one recognized operation verb. The strict grammar rejects multiple recognized verbs and sentence periods, colons, commas, semicolons, ampersands, slashes, `and`, `then`, `also`, `followed by`, `while`, `after`, `before`, `plus`, or `simultaneously` because each can conceal another action; decimal points remain valid.
19. Aha object when the narrative beat is `revelation`.
20. What the viewer learns.
21. Minimal on-screen text.
22. Narration draft.
23. Formula, if any, and the prior visual definition that makes it understandable.
24. Symbol handoff and formula split plan, when formulas appear.
25. Formula derivation steps, when formulas appear: show how visible objects become formula terms.
26. Uncertainty shape, when probability, confidence, error, residuals, or variance appear.
27. Frame zones: reserve non-overlapping regions for geometry, labels, captions, and formulas.
28. Keep-clear pairs: list every text-text and text-data pair that must not intersect; name intentional data-data overlap separately.
29. Transition-frame audit: affirmatively identify entry, midpoint, and settled frames for visual inspection.
30. Layout guard: use `assert_scene_layout(scene=self, pending_items=[...], labels=[...], blockers=[...], frame_items=[...])` for text/data or formula/data states; use `assert_within_frame([...], scene=self, pending_items=[...])` for pure geometry; use `assert_inside` for contained physical shapes.
31. QA risks: label size, CJK wrapping, overlap, visual ambiguity, or playback risk.

## Variable-Length Story Structure

Derive scene count from the ledgers. Use one scene per `Bxx`, one scene per
`Mxx`, and at least one final result/return scene. A typical order is:

1. Concrete hook.
2. One context scene per `Bxx`, arranged as a ladder toward the research gap.
3. Tension or failed interpretation.
4. One mechanism scene per `Mxx`, preserving object continuity.
5. Evidence, alternatives, and uncertainty as visible shapes.
6. Revelation or central visual relation.
7. Return to the original scientific object and state the claim boundary.

## Acceptance Criteria

- The storyboard can be understood from still frames.
- Every scene cites source-derived `Hxx` rules and a storyboard trigger.
- Every `Bxx` and `Mxx` is mapped to exactly one scene; no scene combines ledger items.
- `Background scope` and `Method scope` start with counts that equal their ledger row counts.
- Every background premise and all four method semantics match their owning ledger row exactly.
- The first scene is a hook or tension, context precedes mechanism, and the final scene is a return.
- Every scene includes step detail, a validity reason, and a transition bridge from the previous visible object.
- Every ledger row and scene cites a concrete source locator; the source passage has been checked, not merely named.
- A named independent reviewer has completed the hash-bound JSON contract in `references/semantic-source-audit.md`; every ledger item has a distinct source excerpt and every scene records no undeclared scientific content.
- Every method scene has one visible input, one operation, one visible output, and one validity basis.
- Every formula scene states an antecedent timing that proves geometry appears first.
- Every scene declares frame zones, keep-clear pairs, a transition-frame audit, and a runtime layout guard.
- At least half of the scenes use transformations from existing objects.
- Every revelation scene names one visible Aha object.
- No scene depends primarily on prose.
- No method, formula, or result appears as a black box; intermediate academic reasoning is explicit.
- The last scene shows the scientific result in the original domain.
