# Story Architecture And Scene Granularity

Use this contract before writing the scene table. Scene count is derived from
the research argument; it is never chosen from a fixed-duration template.

## Build The Throughline

Write one sentence for each field:

- `Throughline`: the single idea the viewer should be able to retell.
- `Audience starting point`: what a capable non-specialist already understands.
- `Stakes`: the observable consequence of misunderstanding the problem.
- `Resolution`: what becomes newly visible or interpretable by the end.

Keep one throughline throughout the video. Background and method details must
advance it rather than becoming independent mini-lectures.

## Derive Scene Count From Evidence

Create two ledgers before the scene table:

1. `Background Ledger`: assign `B01`, `B02`, ... to every independent premise,
   historical condition, physical constraint, prior limitation, or audience
   knowledge gap needed to understand the research question.
2. `Method Decomposition Ledger`: assign `M01`, `M02`, ... to every irreducible
   operation in the method, including data preparation when it changes the
   scientific meaning.

Split background context by claim, not by topic heading. Two premises require
two `Bxx` rows and two scenes when either can be removed without making the
other false, when they need different source locators, or when they answer
different viewer questions. A historical condition, a physical constraint, and
a prior-method limitation are therefore three scenes even when the paper places
them in one paragraph. Each scene must make its premise visible through a
scientific object, comparison, boundary, or causal relation rather than a prose
slide.

State `Background scope` and `Method scope` before either ledger. Each field must
begin with an integer that equals the number of rows in its ledger. Strict
public-talk mode requires at least one source-grounded `Bxx` premise that
establishes the concrete hook or research context. Every ledger row must include
a section, equation, figure, table, dataset, appendix, or repository locator. A
nonempty cell is not proof that the claim is true; compare it with the cited
source before approving the storyboard. Record that comparison in the
hash-bound independent audit defined in `semantic-source-audit.md`; strict mode
does not treat a structural score as semantic validation.

Use one scene for one ledger item. A scene may reference one `Bxx` or one `Mxx`,
never two and never both. The minimum scene count is therefore:

`background beats + method steps + at least one result/return scene`.

There is no maximum scene count. Shorten narration or split the video into
chapters rather than compressing several scientific operations into one scene.
Keep `Bxx` scenes in ledger order before the first `Mxx` scene, then keep `Mxx`
scenes in ledger order so every visible output can become the next input.
Copy each background ledger premise exactly into its scene's `Background
premise`. Copy each method ledger input, operation, output, and validity basis
exactly into its scene. Identifier agreement without semantic agreement does
not count as coverage.

## Atomic Method-Step Test

A method step is atomic only when it has:

- one visible input state;
- one operation or inference;
- one visible output state;
- one paper-specific validity basis;
- one handoff to the next state.

Split the step when it contains two independent verbs, produces two outputs,
changes both representation and inference, introduces a formula before its
objects exist, or needs the phrase "and then" to explain the motion. Give each
new step its own `Mxx` identifier and scene.

Apply the split recursively. For each candidate step, underline the input noun,
operation verb, output noun, and validity clause. If a second operation remains,
make the first output the next scene's input and test both rows again. Scene
count is final only when every `Mxx` row survives this test with one operation.

## Public-Talk Story Arc

Use a public-talk arc without turning the animation into a speech deck:

1. `hook`: show the concrete puzzle or mismatch.
2. `context`: close one audience knowledge gap per scene.
3. `tension`: expose why the existing interpretation is insufficient.
4. `mechanism`: reveal one `Mxx` operation per scene through geometry.
5. `evidence`: test the mechanism against data, alternatives, or uncertainty.
6. `revelation`: make the central relation visibly click into place.
7. `return`: put the result back on the original scientific object and state
   its boundary.

The arc is flexible, but every scene must name exactly one narrative beat. The
first scene must be a hook or tension beat, at least one context beat must occur
before the first mechanism beat, and the last scene must be a return or
resolution beat.

Every revelation scene must name one `Aha object`, such as an alignment,
overlap, narrowing interval, conserved center, symmetry, or transformed axis.

This operationalizes official TED guidance that short talks communicate one
clear idea, stories need tension and resolution, and complex visual material is
better divided into several one-idea frames:

- https://www.ted.com/about/conferences/speaking-at-ted
- https://ideas.ted.com/storytelling-is-a-powerful-communication-tool-heres-how-to-use-it-from-ted/
- https://www.ted.com/participate/organize-a-local-tedx-event/tedx-organizer-guide/speakers-program/prepare-your-speaker/create-prepare-slides
- https://www.ted.com/about/our-organization/our-policies-terms/ted-content-guidelines

## Scene-Level Layout Plan

Every scene must specify:

- `Frame zones`: reserved regions for geometry, formulas, captions, and labels.
- `Keep-clear pairs`: text-text and text-data pairs that must not intersect.
- `Transition-frame audit`: entry, midpoint, and settled frames to inspect.
- `Layout guard`: the runtime guard used for the settled state.

Intentional data overlap, such as two density curves on one axis, is allowed and
must be named in `Keep-clear pairs` and passed to the runtime guard as an exact
`intentional_overlaps` object pair. Labels, captions, formulas, legends, and symbols may not obscure
each other or the data. Use `assert_scene_layout` when text or formulas share a
state with data geometry. Use `assert_within_frame` for a pure-geometry state;
add `assert_inside` when a scientific object contains a halo, band, interval, or
support volume.
