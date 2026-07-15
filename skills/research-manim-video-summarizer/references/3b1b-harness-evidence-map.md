# 3B1B Harness Evidence Map

This file turns the style corpus into enforceable storyboard requirements.
Each entry follows the same chain:

`source -> extracted principle -> checkable rule -> storyboard trigger condition`

The checkable rules are local design inferences, not quotations or claims that
the source authors use these exact thresholds. Source links motivate the
principles; the skill owns and must disclose its operational thresholds.
The core primary pages and their page-level locators were checked on 2026-07-13;
see `references/3b1b-style-corpus.md`. Re-open a source before changing a rule.

Use the `Hxx` identifiers in the storyboard. Strict storyboard review fails when
the scene table does not cite these identifiers and does not state trigger
conditions.

## Required Storyboard Evidence Fields

Each scene must include:

- `Source-derived rules:` one or more `Hxx` identifiers from this file.
- `Storyboard trigger:` the concrete event that makes the scene necessary now.
- `Viewer question:` the question, tension, or expectation the scene answers.
- `Visual antecedent:` the object that exists before any symbol or formula appears.
- `Antecedent timing:` for formula scenes, either `earlier in this scene before formula` or `prior Scene N` with an earlier scene number.
- `Motion purpose:` the reason the animation changes the viewer's understanding.
- `Evidence locator:` the paper section, equation, figure, table, page, dataset,
  appendix, or repository path supporting the scene's scientific content.

Formula scenes must additionally include:

- `Symbol handoff:` how the visible object becomes the `MathTex` term.
- `Formula split plan:` how long equations are broken into transformable parts.

Uncertainty scenes must additionally include:

- `Uncertainty shape:` distribution, interval, density, sample cloud, number-line
  width, residual field, or shaded band.

## Evidence Rules

### H01 - Visual Explanation Is The Core Medium

- Source: [3Blue1Brown About](https://www.3blue1brown.com/about/)
- Extracted essence: 3B1B identifies itself as explaining math visually, with
  deep understanding as the goal.
- Principle: The video should make the core idea visible before it becomes prose
  or notation.
- Checkable rule: The first scene must name a concrete visual object and cannot
  begin from a definition, formula, table, or bullet list.
- Storyboard trigger condition: When the topic is introduced, show the research
  object or data shape first, then ask the viewer what needs explaining.

### H02 - Story And Visuals Create Engagement

- Sources: [3Blue1Brown About, advice FAQ](https://www.3blue1brown.com/about/)
  and [TED storytelling guidance](https://ideas.ted.com/storytelling-is-a-powerful-communication-tool-heres-how-to-use-it-from-ted/)
- Extracted essence: Concrete examples should precede general structure, while a
  public story needs tension, resolution, and a central idea.
- Principle: A scene should answer a narrative question, not merely display a
  fact.
- Checkable rule: The opening scene must contain a `Viewer question` field with
  a concrete puzzle, mismatch, measurement problem, or prediction tension.
- Storyboard trigger condition: When a new section begins, state the viewer's
  next question before introducing the next object or formula.

### H03 - Approachability Requires Sparse Text

- Source: [TEDx create and prepare slides, TEDx Tips](https://www.ted.com/participate/organize-a-local-tedx-event/tedx-organizer-guide/speakers-program/prepare-your-speaker/create-prepare-slides)
- Extracted essence: Several simple visuals with one idea, image, or data point
  each are preferred to a crowded visual or headline-and-bullet slide.
- Principle: Text supports the visual; it does not carry the explanation alone.
- Checkable rule: Each scene must have minimal on-screen text and a visual object
  that could still communicate the main idea in a paused frame.
- Storyboard trigger condition: When a paragraph or bullet list would be used,
  replace it with an object, axis, label, brace, color cue, or transform.

### H04 - Representations Should Be Chosen For Intuition

- Source: [3Blue1Brown About, advice FAQ](https://www.3blue1brown.com/about/)
- Extracted essence: Exposition should ask what picture or visual can elucidate
  the topic and use programmatic animation only when it serves the idea.
- Principle: The chosen representation must do explanatory work.
- Checkable rule: Every major concept must be tied to an explicit visual
  representation: geometry, function transform, point cloud, curve, field,
  density, interval, or physical object.
- Storyboard trigger condition: When a method step appears, specify what
  representation changes and why that representation makes the idea easier.

### H05 - Definitions Alone Are Not Enough

- Source: [3Blue1Brown About, advice FAQ](https://www.3blue1brown.com/about/)
- Extracted essence: Definitions should not be the starting point; concrete
  examples should prepare the general structure.
- Principle: Formal statements should arrive after the viewer has something to
  notice.
- Checkable rule: No formula may appear unless the same scene or an earlier
  scene names a `Visual antecedent`, an explicit valid `Antecedent timing`, and
  a `Symbol handoff`.
- Storyboard trigger condition: When notation is introduced, first animate the
  object whose relationship the notation abbreviates.

### H06 - Motivation Must Arrive Early

- Sources: [3Blue1Brown About, advice FAQ](https://www.3blue1brown.com/about/)
  and [SoME1 announcement](https://www.3blue1brown.com/blog/some1/)
- Extracted essence: Open with the key exercise or concrete motivation rather
  than postponing it until after a general framework.
- Principle: The video should earn attention before details accumulate.
- Checkable rule: The opening sequence must include the research object, a
  visible stakes cue, and a viewer question before method exposition begins.
- Storyboard trigger condition: When planning Scene 1 or Scene 2, show why the
  paper's problem matters through a mismatch, failed prediction, surprising
  pattern, or measurable consequence.

### H07 - Explanatory Craft Needs Explicit Review

- Source: [SoME1 results](https://www.3blue1brown.com/blog/some1-results/)
- Extracted essence: Strong entries are valued for clarity, motivation,
  topic choice, and non-obvious insight.
- Principle: The storyboard should expose the intended insight before animation
  code is written.
- Checkable rule: Each scene must state `What the viewer learns` as one idea,
  and strict review rejects scenes that combine multiple unrelated ideas.
- Storyboard trigger condition: When a scene tries to introduce two ideas, split
  it or identify the single insight that survives in a paused frame.

### H08 - Inspectable Mechanisms Beat Answer-Only Output

- Source: [SoME2 results](https://www.3blue1brown.com/blog/some2/)
- Extracted essence: SoME celebrates varied explainers and actionable advice for
  math content, not just final answers.
- Principle: Research videos should reveal the mechanism, not jump from input to
  conclusion.
- Checkable rule: Method scenes must show an input object transforming into an
  intermediate object before the result is stated.
- Storyboard trigger condition: When the paper reports a result, animate the
  mechanism that makes the result plausible.

### H09 - Public Exposition Needs Broad Entry Points

- Source: [SoME3 begins](https://3blue1brown.substack.com/p/some3-begins)
- Extracted essence: The contest invites broad math exposition for public
  learning.
- Principle: A research animation should not assume the viewer already knows the
  paper's notation or stakes.
- Checkable rule: The storyboard must include audience assumptions and avoid
  first-use jargon without a visual definition.
- Storyboard trigger condition: When a field-specific term first appears, pair
  it with a simple visual object and a one-line meaning.

### H10 - Selected Explanations Build Aha Moments

- Source: [SoME3 results](https://3blue1brown.substack.com/p/some3-results)
- Extracted essence: Featured entries are selected for explainers that viewers
  may enjoy and remember.
- Principle: The storyboard needs a visible moment where structure becomes
  easier to see.
- Checkable rule: At least one middle scene must name the `Aha object`: the
  visual change that turns scattered observations into a relationship.
- Storyboard trigger condition: When the central method insight appears, mark
  the object that snaps into place: alignment, overlap, narrowing, symmetry,
  conserved shape, or transformed coordinate.

### H11 - Peer Review Should Be Built Into The Harness

- Source: [SoME4](https://3blue1brown.substack.com/p/summer-of-math-exposition-4)
- Extracted essence: SoME uses peer review and community judging, making review
  criteria part of the exposition process.
- Principle: The skill must force self-review before rendering.
- Checkable rule: Strict storyboard review must cite enough `Hxx` rules and must
  fail when source-derived trigger fields are missing.
- Storyboard trigger condition: Before Manim code is generated, run the
  storyboard checker and require a 30/30 strict pass.

### H12 - Animation Workflow Is Deliberate

- Source: [How I animate 3Blue1Brown](https://3blue1brown.substack.com/p/how-i-animate-3blue1brown)
- Extracted essence: 3B1B animation is built through Manim workflow, not static
  slide capture.
- Principle: Motion must reveal, compare, or transform a mathematical idea.
- Checkable rule: Each scene must include `Motion purpose`; decorative movement,
  hard cuts, and unexplained fades fail strict review.
- Storyboard trigger condition: When an animation action is planned, state what
  new relationship becomes visible because of the motion.

### H13 - Object Continuity Comes From Scene Code

- Source: [3b1b/videos repository](https://github.com/3b1b/videos)
- Extracted essence: The repository contains code for Manim-generated
  explanatory math scenes.
- Principle: Important objects should persist across scenes through transforms
  instead of being repeatedly redrawn as unrelated graphics.
- Checkable rule: As a local quality threshold, at least half the scenes must use
  transformation from previous objects; this proportion is the skill's design
  rule, not a threshold stated by the repository authors.
- Storyboard trigger condition: When advancing scenes, identify which mobject
  remains, moves, morphs, splits, or becomes the next representation.

### H14 - Use Programmatic Geometry, Not Static Images

- Source: [3b1b/manim repository](https://github.com/3b1b/manim)
- Extracted essence: Manim is an engine for precise programmatic animations for
  explanatory math videos.
- Principle: The animation should be reproducible from code and should expose
  mathematical structure through controllable mobjects.
- Checkable rule: Storyboards and code plans must prefer generated axes, curves,
  fields, braces, labels, and transforms over static screenshots.
- Storyboard trigger condition: When a paper figure is needed, specify whether it
  is recreated as Manim geometry or used only as a cited background reference.

### H15 - Formulas Need LaTeX Math Objects

- Source: [Manim Community text/formula guide](https://docs.manim.community/en/stable/guides/using_text.html)
- Extracted essence: Manim distinguishes simple text from LaTeX-based formula
  rendering, and LaTeX should be used for mathematical typesetting.
- Principle: Mathematical symbols should be first-class visual objects.
- Checkable rule: Formulas must use `MathTex` by default; prose uses `Text` or
  `Tex` only when appropriate.
- Storyboard trigger condition: When a mathematical symbol appears, list its
  visual antecedent and the `MathTex` expression that names it.

### H16 - Split Formula Parts For Transform Continuity

- Source: [Manim MathTex reference](https://docs.manim.community/en/stable/reference/manim.mobject.text.tex_mobject.MathTex.html)
- Extracted essence: `MathTex` pieces can become submobjects, supporting
  transformable equation parts.
- Principle: Long equations should be animated as relationships among parts, not
  displayed as one wide static line.
- Checkable rule: Any nontrivial equation must include a `Formula split plan`
  naming the parts that will transform, align, or highlight.
- Storyboard trigger condition: When an equation has more than one operation or
  relation, split it into terms before writing animation code.

### H17 - Layout Is Part Of Meaning

- Source: [Manim building blocks and positioning docs](https://docs.manim.community/en/stable/tutorials/building_blocks.html)
- Extracted essence: Manim provides mobject positioning and alignment methods
  such as `next_to`, `align_to`, and bounding-box-aware placement.
- Principle: Labels and equations must not obscure the data object they explain.
- Checkable rule: Storyboards must flag QA risks for overlap, clipping, crowded
  labels, CJK wrapping, and formula lanes.
- Storyboard trigger condition: When text, labels, or formulas share a scene
  with axes, curves, clouds, or bands, reserve a safe zone before rendering.

### H18 - Transform Matching Preserves Mathematical Identity

- Source: [Manim TransformMatchingTex reference](https://docs.manim.community/en/stable/reference/manim.animation.transform_matching_parts.TransformMatchingTex.html)
- Extracted essence: Matching LaTeX submobjects can transform across equations
  by shared tex strings.
- Principle: Symbol continuity should be visible when formulas change form.
- Checkable rule: Derivations should specify which terms persist across
  transformations; avoid replacing whole equations with unrelated new text.
- Storyboard trigger condition: When one formula becomes another, name the terms
  that stay fixed, move, cancel, or combine.

### H19 - One Throughline Holds The Talk Together

- Source: [Speaking at TED](https://www.ted.com/about/conferences/speaking-at-ted)
- Extracted essence: TED guidance emphasizes communicating one clear idea in a
  short talk.
- Principle: Background, method, and result scenes must advance one central idea.
- Checkable rule: The storyboard must state one `Throughline`, and every scene
  must name one narrative beat that advances it.
- Storyboard trigger condition: Before counting scenes, state what single idea
  the viewer should be able to retell after the final frame.

### H20 - One Visual Beat Per Frame

- Source: [TEDx create and prepare slides](https://www.ted.com/participate/organize-a-local-tedx-event/tedx-organizer-guide/speakers-program/prepare-your-speaker/create-prepare-slides)
- Extracted essence: TEDx recommends several simple visuals, each carrying one
  idea, image, or data point, instead of one crowded visual.
- Principle: Scientific detail should increase scene count, not frame density.
- Checkable rule: Each `Bxx` background premise and each `Mxx` atomic method step
  must map to exactly one scene; a scene may not own two ledger items.
- Storyboard trigger condition: When a scene needs a second independent premise,
  verb, or output, split it and preserve the shared object across the boundary.

### H21 - Context, Tension, Evidence, And Resolution Form A Story

- Sources: [TED storytelling guidance](https://ideas.ted.com/storytelling-is-a-powerful-communication-tool-heres-how-to-use-it-from-ted/)
  and [TED content guidelines](https://www.ted.com/about/our-organization/our-policies-terms/ted-content-guidelines)
- Extracted essence: A useful story builds relatable tension, includes the right
  level of detail, resolves the central idea, and remains accurate about the
  evidence and maturity of its claims.
- Principle: Background is a ladder toward the research tension, not a condensed
  literature slide; the ending resolves the puzzle while preserving claim
  boundaries.
- Checkable rule: The first scene is a hook or tension beat, at least one context
  beat precedes the first mechanism beat, and the final scene is a return or
  resolution beat with the claim boundary visible or narrated.
- Storyboard trigger condition: Add one context scene for each audience gap, then
  reveal the next scientific object only after that gap is closed.

## Minimum Strict Coverage

A strict storyboard must include at least seven distinct `Hxx` identifiers across
the whole scene table, including:

- One of `H01`, `H02`, or `H06` for the opening hook.
- One of `H05`, `H15`, `H16`, or `H18` whenever formulas or symbols appear.
- One of `H12` or `H13` for motion and continuity.
- `H17` when labels, formulas, or captions share a frame with plotted data.
- `H19` and at least one of `H20` or `H21` for throughline and scene granularity.
- An uncertainty-shape trigger whenever probability, error, confidence,
  residuals, or variance appear.
