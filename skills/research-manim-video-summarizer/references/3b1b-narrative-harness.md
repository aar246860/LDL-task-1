# 3B1B Narrative Harness

Use this harness before code generation. The goal is not to imitate surface
effects; the goal is to make the explanation feel like visual reasoning.

The strict harness is evidence-driven. Before approving a storyboard, read
`references/3b1b-harness-evidence-map.md` and require scene-level `Hxx` rule
citations plus trigger fields.

## Scored Rubric

Each storyboard must pass all fifteen checks. Strict mode requires 30 of 30
points and no hard failure; it does not treat a `revise` finding as approval.

| Check | Full-credit evidence | Evidence rules |
| --- | --- | --- |
| Storyboard schema integrity | Metadata, spine, ledgers, glossary, scenes, source locators, and unique nonblank fields parse into one unambiguous contract. | `H11`, `H20`, `H21` |
| Narrative hook | Opens with a concrete puzzle, tension, mismatch, or measurement question instead of a definition. | `H01`, `H02`, `H06`, `H09` |
| Concrete visual anchor | The first scene gives the viewer a physical object, plotted object, geometric object, or data shape to watch. | `H01`, `H03`, `H04` |
| Geometry before formula | Symbols appear only after the object they describe has already appeared on screen. | `H05`, `H15`, `H16`, `H18` |
| One idea per scene | Each scene has one purpose: reveal a change, compare two alternatives, or make an inference. | `H07`, `H08`, `H10` |
| Academic step detail | Each scene states the ordered micro-steps, why the step is valid, and how the previous visual object bridges to the next claim. | `H05`, `H08`, `H11`, `H16`, `H18` |
| Morph continuity | Important concepts reuse existing mobjects through transforms, movement, or camera continuity. | `H12`, `H13`, `H18` |
| Purposeful motion | Every animation changes what the viewer can understand; decorative movement is removed. | `H08`, `H12`, `H13` |
| Uncertainty as shape | Probability, error, confidence, or uncertainty becomes a distribution, interval, density, sample cloud, or shaded band. | `H03`, `H04`, `H17` |
| Return to scientific object | The ending returns from abstractions to the original physical, empirical, or scientific object. | `H01`, `H06`, `H08` |
| Source-derived trigger coverage | Each scene cites `Hxx` rules and states what event makes the scene necessary now. | `H11` |
| Public-talk throughline | One central idea links hook, context, tension, mechanism, evidence, revelation, and return. | `H19`, `H21` |
| Background-beat coverage | Every `Bxx` premise receives one scene before the dependent mechanism; no scene carries two premises. | `H20`, `H21` |
| Atomic method coverage | Every `Mxx` input-operation-output step receives one scene; no method scene performs two independent operations. | `H07`, `H08`, `H20` |
| Scene layout contract | Every scene reserves zones, lists keep-clear pairs, audits transition frames, and names a runtime guard. | `H17`, `H20` |

## Required Strict Fields

Every strict storyboard scene must include:

1. `Source-derived rules:` one or more `Hxx` identifiers.
2. `Storyboard trigger:` the concrete event that makes the scene necessary now.
3. `Viewer question:` what the viewer is trying to resolve in this scene.
4. `Visual antecedent:` the visible object that exists before symbols or formulas.
5. `Motion purpose:` why the movement reveals, compares, or transforms meaning.
6. `Step detail:` the ordered academic micro-steps shown in the scene.
7. `Why this step is valid:` the paper-specific reason, assumption, data relation, or evidence.
8. `Transition bridge:` how the previous visible object becomes the next visible object or claim.
9. `Narrative beat:` one story function only.
10. `Background beat:` one `Bxx` or `none`; the complete storyboard must contain at least one `Bxx`.
11. `Background premise:` for a `Bxx` scene, exactly matching its ledger premise.
12. `Method step:` one `Mxx` or `none`.
13. `Frame zones:`, `Keep-clear pairs:`, `Transition-frame audit:`, and
    `Layout guard:`.
14. `Evidence locator:` a specific source section, equation, figure, table,
    page, dataset, appendix, or repository path.

Formula scenes must also include `Antecedent timing:`, `Symbol handoff:`,
`Formula split plan:`, and `Formula derivation steps:`. `Antecedent timing` is
either `earlier in this scene before formula` or a valid earlier scene number.
Uncertainty scenes must also include `Uncertainty shape:`.
Method scenes must also include `Input state:`, `Operation:`, `Output state:`,
and `Validity basis:` copied exactly from the owning `Mxx` ledger row.
Revelation scenes must also include `Aha object:`.

## Hard Rejections

Reject the storyboard immediately when any of these patterns dominate:

- The first scene begins with a definition, formula, or list of variables.
- Scene-level `Source-derived rules` or `Storyboard trigger` fields are missing.
- Step detail, validity reason, or transition bridge fields are missing from any scene.
- The storyboard is written to a fixed scene count before background and method ledgers are complete.
- The declared background or method scope count differs from its ledger count.
- A scene combines two `Bxx` items, two `Mxx` items, or a background item and a method item.
- A background premise or method semantic field differs from its owning ledger row.
- A ledger item has no unique scene, or a method scene lacks an input-operation-output chain.
- A ledger row or scene has a blank, unsupported, or missing source locator.
- A field is duplicated, blank, negated, or uses an invalid enum value.
- The story has no single throughline, no context before mechanism, or no return/resolution ending.
- A table, spreadsheet, software flowchart, or bullet slide is the main visual.
- Probability is described only in prose.
- Equations are shown as wide static text instead of transformable terms.
- Formulas appear without derivation steps that map visible objects into formula terms.
- Motion exists only to decorate the scene.
- The final scene ends at a black-box model output without returning to the
  paper's scientific object.
- A scene omits its frame zones, keep-clear pairs, transition-frame audit, or
  runtime layout guard.
- A revelation scene has no visible Aha object.

## Scene-Level Contract

Every scene must answer these questions:

1. What object is already on screen?
2. What changes visually?
3. Why does the motion happen now?
4. What single idea should remain if the frame is paused?
5. Which exact academic step is being shown, and why is it valid?
6. Which visible object from the previous scene bridges into this step?
7. Which symbol or formula appears, and what visual object defines it?
8. Which single `Bxx` or `Mxx` item does the scene own?
9. Which objects must remain clear at entry, midpoint, and settled frames?

## Research-Specific Guidance

- Start with the paper's measurable object: specimen, aquifer, pile, field,
  curve, distribution, map, or data cloud.
- Convert method steps into transformations of that object.
- Convert uncertainty into visible width, spread, density, or shading.
- Let formulas summarize the visual scene after the viewer has seen the
  quantities.
- End by showing the result back on the original scientific object.
