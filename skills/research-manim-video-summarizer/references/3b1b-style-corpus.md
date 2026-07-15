# 3B1B Style Corpus

These sources justify the narrative and visual checks in this skill. They are
not copied as a house style; they are distilled into verifiable rules for
research animation.

## Source Audit Record

Core pages were re-opened on 2026-07-13. Use these page-level locators when
auditing the paraphrases below:

- 3Blue1Brown About: `About`, `What do you use to animate your videos?`, and
  `I'd like to start making math videos online, do you have any advice?`.
- How I animate 3Blue1Brown: article body describing the Manim scene workflow.
- TED storytelling guidance: the four-item story guidance and central-idea
  paragraphs.
- TEDx visual guidance: `TEDx Tips`.
- Manim Community building blocks: `Placing mobjects` and `Transforming mobjects
  into other mobjects`.

These are live, mutable pages. Re-open the relevant page and record a new access
date whenever an `Hxx` rule changes. Interview rows provide context only and are
never the sole basis for a hard rejection. The `Hxx` thresholds remain local
operational inferences, not quotations from these sources.

For the strict harness, do not stop at this summary table. Use
`references/3b1b-harness-evidence-map.md`, which maps each source to:

`source -> extracted principle -> checkable rule -> storyboard trigger condition`

| Source | Link | Useful style signal |
| --- | --- | --- |
| 3Blue1Brown About/FAQ | https://www.3blue1brown.com/about/ | The channel frames mathematics through visual explanations and notes that animations are made with Manim. The FAQ also points to visual intuition as the central value of the videos. |
| Stanford Daily interview | https://stanforddaily.com/2020/01/24/3blue1brown-creator-grant-sanderson-15-talks-engaging-with-math-using-stories-and-visuals/ | Context only: an interview about stories and visuals in mathematical engagement. |
| Dropbox interview | https://blog.dropbox.com/topics/work-culture/grant-sanderson-channels-his-passion-for-math-into-marvelously-i | Context only: a profile of animated mathematical explanation. |
| IAPS interview | https://iaps.info/2025/01/22/exploring-the-path-of-3blue1brown-a-conversation-with-grant-sanderson/ | Context only: an interview about intuition, teaching, and programmed visualization. |
| Dwarkesh Patel interview | https://www.dwarkesh.com/p/grant-sanderson | Context only: a discussion of mathematical problem solving and explanation. |
| SoME1 announcement | https://www.3blue1brown.com/blog/some1/ | The Summer of Math Exposition frames math communication as explanation that stands on its own, not merely correctness. |
| SoME1 results | https://www.3blue1brown.com/blog/some1-results/ | The results show judging values such as clarity, novelty, and explanatory craft, supporting storyboard review before animation code. |
| SoME2 | https://www.3blue1brown.com/blog/some2/ | The second contest reinforces that strong exposition can come from different media but must make ideas inspectable. |
| SoME3 begins | https://3blue1brown.substack.com/p/some3-begins | The announcement continues the emphasis on mathematical exposition as a crafted public explanation. |
| SoME3 results | https://3blue1brown.substack.com/p/some3-results | The selected work shows that excellent exposition often builds intuition before formalism. |
| SoME4 | https://3blue1brown.substack.com/p/summer-of-math-exposition-4 | The ongoing contest structure supports using a rubric for narrative clarity and visual communication. |
| How I animate 3Blue1Brown | https://3blue1brown.substack.com/p/how-i-animate-3blue1brown | Describes the animation workflow and reinforces that deliberate animation design, not merely generated visuals, is part of the explanation. |
| 3b1b/videos repository | https://github.com/3b1b/videos | The public source shows a code-first animation practice with reusable objects, transforms, and scenes. This skill targets Manim Community, but borrows the discipline of object continuity. |
| 3b1b/manim repository | https://github.com/3b1b/manim | Shows the historical open-source animation engine behind 3Blue1Brown. This skill uses the maintained Manim Community edition for reproducible research work. |
| Manim Community text guide | https://docs.manim.community/en/stable/guides/using_text.html | Confirms practical tools for text and formula rendering, including when to use LaTeX-based formula mobjects. |
| Manim Community positioning examples | https://docs.manim.community/en/stable/reference/manim.mobject.mobject.Mobject.html | Confirms positioning operations such as `next_to`, `to_edge`, and object transforms that support collision-aware scene layout. |
| TED speaking guidance | https://www.ted.com/about/conferences/speaking-at-ted | TED guidance emphasizes communicating one clear idea, which motivates this skill's explicit-throughline rule. |
| TED storytelling guidance | https://ideas.ted.com/storytelling-is-a-powerful-communication-tool-heres-how-to-use-it-from-ted/ | TED's guidance emphasizes relatable tension, appropriate detail, a central idea, and a satisfying resolution rather than disconnected anecdotes. |
| TEDx visual guidance | https://www.ted.com/participate/organize-a-local-tedx-event/tedx-organizer-guide/speakers-program/prepare-your-speaker/create-prepare-slides | TEDx recommends several simple visuals with one idea, image, or data point each instead of one crowded visual. |
| TED content guidelines | https://www.ted.com/about/our-organization/our-policies-terms/ted-content-guidelines | TED requires accurate, transparent claims and clear context for aspirational or preliminary work. |

## Strict Harness Rule Families

- Opening hook and motivation: `H01`, `H02`, `H06`, `H09`.
- Concrete representation and public intuition: `H03`, `H04`, `H07`, `H10`.
- Formula and symbol handoff: `H05`, `H15`, `H16`, `H18`.
- Motion, morph continuity, and code-generated geometry: `H08`, `H12`, `H13`,
  `H14`.
- Layout and render safety: `H17`.
- Review gate: `H11`.
- Public-talk throughline, context pacing, and claim resolution: `H19`, `H20`,
  `H21`.

The storyboard checker expects the scene table to cite these identifiers and to
state the trigger condition that made each scene necessary.
