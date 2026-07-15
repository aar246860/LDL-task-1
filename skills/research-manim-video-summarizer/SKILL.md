---
name: research-manim-video-summarizer
description: Convert research papers, LaTeX manuscripts, PDFs, reports, or paper repositories into rigorous, independently implemented geometry-first Manim Community video summaries with one-background-premise-per-scene storytelling, one-atomic-method-operation-per-scene derivations, public-talk narrative arcs, runtime overlap guards, transition-frame QA, browser-ready export, and GitHub Release playback links. Use when the user asks for research video abstracts, animated manuscript summaries, Manim teaching animations, 3Blue1Brown-inspired paper explanations, TED-inspired research storytelling, conference-method animations, or phone-downloadable research videos.
---

# Research Manim Video Summarizer

Create a research video summary that explains a paper through visual reasoning, not a slide deck. The default output is local: a Manim Community project plus a browser-ready MP4, contact sheet, HTML player, metadata JSON, QA notes, and a visual-QA manifest. Use Gemini or publish to GitHub only after the user explicitly authorizes that external action.

`3Blue1Brown-inspired` and `TED-inspired` describe independently implemented pedagogical principles: geometry-led explanation, one clear idea, context, tension, and resolution. This skill is not affiliated with, endorsed by, or presented as content from 3Blue1Brown, TED, or TEDx, and it must not copy their branding.

## Workflow

1. **Read the research artifact.**
   - Accept `.tex`, `.pdf`, Markdown reports, figure folders, benchmark CSVs, or a repo containing paper assets.
   - Extract: research question, scientific object, input data, uncertainty treatment, primary result, symbols, audience, every necessary background premise, and every irreducible method operation.
   - A paper repo may identify a possible publication target, but it is not authorization to publish. Require an explicit user request before any GitHub mutation.

2. **Read the contracts before writing.**
   - Narrative style: `references/3b1b-narrative-harness.md`
   - Source corpus: `references/3b1b-style-corpus.md`
   - Source-to-rule evidence map: `references/3b1b-harness-evidence-map.md`
   - Implementation provenance: `references/evidence-sources.md`
   - Story architecture and scene granularity: `references/story-architecture-and-scene-granularity.md`
   - Independent source-passage audit: `references/semantic-source-audit.md`
   - Symbol and layout rules: `references/math-symbol-and-layout-contract.md`
   - Storyboard fields: `references/research-storyboard-template.md`
   - Manim workflow: `references/manim-community-workflow.md`
   - Playback QA: `references/visual-qa-playback.md`

3. **Derive a geometry-first storyboard from the argument.**
   - Write a single `Throughline`, `Audience starting point`, `Stakes`, and `Resolution` before deciding scene count.
   - Declare one exact `Rendering target`: `720p`, `1080p`, or `4k`.
   - Begin `Background scope` with the exact number of required `Bxx` rows and begin `Method scope` with the exact number of required `Mxx` rows. The counts must match their ledgers.
   - Create at least one `Bxx` premise for the concrete hook or research context. Strict public-talk mode never starts with an empty background ledger.
   - Build a `Background Ledger` with one `Bxx` item for every independent premise or knowledge gap.
   - Build a `Method Decomposition Ledger` with one `Mxx` item for every atomic input-operation-output step.
   - Give every ledger row a paper section, equation, figure, table, dataset, appendix, or repository locator. Blank semantic cells fail strict review.
   - Allocate exactly one scene to each `Bxx` and each `Mxx`. Never combine two ledger items or a background beat and method step in one scene.
   - In each `Bxx` scene, copy the ledger premise exactly into `Background premise`. In each `Mxx` scene, copy the ledger's `Input state`, `Operation`, `Output state`, and `Validity basis` exactly into the corresponding scene fields. This prevents a scene label from claiming ledger coverage while showing different science.
   - Do not target a fixed number of scenes. The minimum is `B items + M items + one result/return scene`; split chapters instead of compressing scientific reasoning.
   - Start from a concrete object, not a definition.
   - Cite source-derived `Hxx` rules from `references/3b1b-harness-evidence-map.md`.
   - Include `Narrative beat`, `Storyboard trigger`, `Viewer question`, `Visual antecedent`, and `Motion purpose` in every scene.
   - Include `Step detail`, `Why this step is valid`, and `Transition bridge` in every scene; academic videos must not skip intermediate reasoning.
   - Include `Evidence locator` in every scene. The local checker validates structure and applicability of rule families; it cannot establish that a scientific claim is true, so the agent must still compare each claim with the cited source passage.
   - After drafting, assign a separate reviewer pass to create `storyboard_semantic_audit.json`. It must bind the source and storyboard hashes, quote one uniquely located, non-overlapping source passage for every `Bxx` and `Mxx`, and certify every scene against undeclared scientific content. Structural 30/30 without this audit is not a strict pass.
   - Method scenes must include `Method step`, `Input state`, `Operation`, `Output state`, and `Validity basis`.
   - Background scenes must include exactly one `Background beat` and show its evidence or scientific boundary as a visual object.
   - Include `Frame zones`, `Keep-clear pairs`, `Transition-frame audit`, and `Layout guard` in every scene.
   - Add formulas only after the geometry exists.
   - For every formula scene, include `Antecedent timing` and `Formula derivation steps`. Timing must be `earlier in this scene before formula` or `prior Scene N`, where `N` is smaller than the current scene number.
   - Include a symbol glossary before animation code.
   - Give every `revelation` scene an `Aha object`: the specific visible relation that becomes newly legible.
   - Use uncertainty shapes: distributions, intervals, sample clouds, densities, or shaded bands.
   - Check the storyboard:

```bash
uv run scripts/check_storyboard_contract.py storyboard.md --strict \
  --source-artifact paper.pdf \
  --semantic-audit storyboard_semantic_audit.json
```

4. **Run optional Gemini 3B1B style review only with consent.**
   - Send storyboard content to Gemini only when the user explicitly requests or approves that disclosure. Visual ambition or local uncertainty alone is not consent.
   - Use the user's already-open, logged-in Chrome/Gemini web session, following `gemini-iterative-manuscript-review` browser-route rules. Do not use Gemini CLI, API, Playwright Chromium, a dev Chrome profile, or local paths alone unless the user explicitly approves that exception.
   - Build the prompt from `references/gemini-3b1b-storyboard-review-prompt.md` and paste the actual storyboard content after it. The default author instruction is: `Audit this storyboard as a rigorous, independently implemented, 3Blue1Brown-inspired visual explanation. Identify scientific-story, scene-granularity, motion, and layout problems, then propose specific repairs.`
   - Save the prompt and Gemini response in a project-local folder such as `.codex-review/gemini_3b1b_storyboard/round1_prompt.md` and `.codex-review/gemini_3b1b_storyboard/round1_review.md`.
   - Classify Gemini findings as:
     - **Must fix:** workflow-presentation framing, cards/tables/dashboards as main objects, compressed background premises, multiple method operations in one scene, formula-first scenes, missing geometry-to-symbol handoff, black-box ML blocks, text-only uncertainty, weak throughline, or ending away from the scientific object.
     - **Check before fixing:** broad story restructuring, domain simplifications, wording preferences, suggestions that may change scientific meaning.
     - **Do not apply blindly:** invented facts, unsupported claims, new citations, changes that break the source evidence or local strict storyboard contract.
   - Revise the storyboard for must-fix findings and rerun the complete strict structural-plus-semantic command locally. Send a revised storyboard to Gemini only when the user requested iterative review or separately approves that second disclosure; a hard rejection never implies consent for another upload.
   - Gemini is a style reviewer, not scientific validation. Source claims, equations, citations, and result boundaries still require local evidence or primary sources.

5. **Generate Manim Community code.**
   - Use one Manim `Scene` subclass and one directly rendered helper per storyboard scene. Name each helper with both its scene number and owner, such as `scene_01_b01_*`, `scene_04_m01_*`, or `scene_10_return`; call it exactly once and in order from `construct` so code, storyboard, and reviewed frames can be matched.
   - Use `MathTex` for symbols and formulas by default.
   - Split long equations into transformable terms.
   - Never use raw `Transform` for unrelated prose labels or CJK title changes; use `FadeOut`/`FadeIn`, or `TransformMatchingShapes` only when the visible characters truly correspond.
   - Keep geometry morphs and text label swaps in separate animation calls unless the text is mathematically attached to the morphing object.
   - When switching spatial dimension or view type, such as cross-section to plan view, either use a physically meaningful camera transition or clear/fade the old view before introducing the new view. Do not morph unrelated cross-section geometry into map geometry.
   - Dim non-focal geometry before introducing a new heat path, flux direction, interval, or uncertainty object; only the active explanatory object should carry highest contrast.
   - Add `self.wait()` long enough after formulas, uncertainty intervals, and view changes for the viewer to read the geometry before the next concept enters.
   - Use `assets/research_manim_layout.py` helpers for caption bands, formula lanes, max-width fitting, margin labels, and rendered overlap guards.
   - At every settled scene state, use the guard that matches its contents. For text/data or formula/data states, call `assert_scene_layout(scene=self, pending_items=[...], labels=[...], blockers=[...], frame_items=[...])`; `frame_items` must cover every family member already in `self.mobjects` plus every object about to be added or animated. For pure geometry states, call `assert_within_frame([...], scene=self, pending_items=[...])` with every visible and pending object. One guard elsewhere in the file does not cover another scene.
   - Every item listed as a label or blocker must also belong to `self.mobjects` or `pending_items` and to `frame_items`; detached objects cannot be used to satisfy an overlap check.
   - The strict static checker rejects `.animate` because its final geometry is not independently guarded. For a spatial change, build a positioned target copy, guard the target together with the current visible state, then use an explicit transform between the same scientific object states. Continue to use fade replacement for unrelated text.
   - Use `place_label_clear` for dynamic label placement; `next_to` alone is not enough.
   - When support-volume rings, halos, intervals, or uncertainty bands belong to a physical object, call `assert_inside` to keep them within that object unless the storyboard explicitly says the object is larger than the visible crop. The runtime guard samples the actual closed boundary, including curved containers; a bounding-box-only claim is not sufficient.
   - Treat data-data overlap as intentional only when the storyboard names it and pass every allowed top-level pair through `intentional_overlaps=[(first, second), ...]`. Undeclared geometry overlap, text-text overlap, text-data overlap, and frame-edge collisions fail.
   - Check layout risk before rendering:

```bash
uv run scripts/check_manim_layout.py animation/paper_summary_scene.py
```

6. **Render and export.**
   - Render with Manim Community Edition.
   - Re-encode the MP4 as H.264, `yuv420p`, and `faststart`.
   - Generate HTML player, contact sheet, metadata JSON, and QA notes:

```bash
uv run scripts/export_manim_video.py input.mp4 output --slug paper-summary --title "Paper summary"
```

7. **Verify playback and publish.**
   - Open the HTML player or MP4 in a browser and confirm finite duration, positive dimensions, and no media error.
   - The player must expose a direct MP4 link and a user-initiated play control. Do not use a portrait contact sheet as a 16:9 video poster; the sheet is navigation evidence.
   - Extract and inspect three nonblank frame images per scene: entry, midpoint, and settled. Every image must be globally unique across all scenes, not only within its scene.
   - Record a named reviewer, timezone-aware ISO `reviewed_at`, exact `review_method: visual inspection`, exact `browser_playback: pass: finite duration, positive dimensions, no media error`, and `pass: overlap-free and within-frame` for all three states. Add each relative frame path, zero-based MP4 frame index, and image-file SHA-256. The checker decodes those exact MP4 indices with FFmpeg and requires byte-equivalent RGB pixels.
   - Record each scene's contiguous zero-based `[scene_start_frame, scene_end_frame)` range. Select entry at 10-35%, midpoint at 40-65%, and settled at 70-95% of that range; all ranges must cover the MP4 from frame zero without gaps.
   - For every scene, copy the exact storyboard `Visual object`, record the owning `Bxx`, `Mxx`, or narrative beat, write three distinct substantive `entry_content_summary`, `midpoint_content_summary`, and `settled_content_summary` values, and sign `visual_semantic_match: pass`. This is accountable human or independent-agent judgment; pixel identity alone cannot prove that an image scientifically entails the storyboard claim.
   - Record file names and SHA-256 values for the Manim source, storyboard, source artifact, semantic audit, contact sheet, reviewed MP4, HTML player, metadata JSON, and QA notes. Publication must include all four source-side artifacts and all companion artifacts; hexadecimal placeholders do not count.
   - The exported contact sheet is navigation evidence only; it cannot prove collision freedom. Rerun the layout checker with the contact sheet, QA manifest, and storyboard:

```bash
uv run scripts/check_manim_layout.py animation/paper_summary_scene.py \
  --contact-sheet output/paper-summary_contact_sheet.png \
  --qa-manifest output/paper-summary_visual_qa.json \
  --storyboard storyboard.md \
  --source-artifact paper.pdf \
  --semantic-audit storyboard_semantic_audit.json
```

   - Publish only when the user explicitly requests live GitHub publication. Preview is the default; live mutation requires both flags:
   - Publication re-runs `ffprobe`, contact-sheet inspection, global frame uniqueness, exact frame-to-MP4 decoding, visual-review completeness, and manifest-to-file matching; a corrupt MP4, duplicated frame, or missing source artifact stops both dry-run and live publication.
   - A live release must refuse an existing GitHub Release or Git tag, must not use `--clobber`, and must upload only a freshly copied package that has passed a second validation.

```bash
uv run scripts/publish_video_release.py output --github-repo OWNER/REPO --release-tag paper-summary-v1 --dry-run
uv run scripts/publish_video_release.py output --github-repo OWNER/REPO --release-tag paper-summary-v1 --publish release --live --confirm-publish
```

## Hard Gates

Reject or revise when any of these occur:

- The storyboard begins with a formula, definition, table, or bullet slide.
- The storyboard uses a fixed scene target before counting background beats and atomic method steps.
- `Rendering target` is absent or not exactly `720p`, `1080p`, or `4k`, or either scope count does not equal its ledger count.
- A `Bxx` background item is missing, reused, or combined with another background or method item in one scene.
- A `Bxx` scene's `Background premise` differs from its ledger premise.
- An `Mxx` method item is missing, reused, or combined with another operation in one scene.
- An `Mxx` scene's input, operation, output, or validity basis differs from its ledger row.
- A method scene lacks one visible input, one operation, one visible output, or a paper-specific validity basis.
- The story has no single throughline, no pre-method context beat, or no final return/resolution beat.
- Scenes omit source-derived `Hxx` rules or storyboard trigger conditions.
- A scene or ledger row has no paper-specific evidence locator, or a scientific claim has not been checked against that source.
- Strict review lacks a named, hash-bound semantic source audit, any `Bxx` or `Mxx` lacks a distinct supporting passage, or a scene contains undeclared scientific content.
- Scenes omit step-by-step academic detail, the reason a step is valid, or the bridge from the previous visible object.
- Gemini 3B1B review, when requested or run, returns hard rejections that have not been fixed or explicitly rejected with a reason.
- Probability or uncertainty is prose-only.
- Symbols appear without first-use definition, visual object, meaning, unit, and scene.
- Formula scenes omit derivation steps that show how visible objects become formula terms.
- A formula scene lacks explicit antecedent timing, or points to the same or a later scene as its antecedent.
- Formulas are written in `Text` instead of `MathTex`.
- Unrelated text labels or CJK titles are transformed with raw `Transform`, causing glyph scrambling or broken strokes.
- Cross-section geometry morphs directly into plan-view maps, charts, or unrelated panels without a camera bridge or full fade/clear transition.
- A scene introduces new arrows, heat paths, or uncertainty intervals while all background objects remain equally bright and visually competing.
- Important formulas, view changes, or uncertainty intervals have no readable pause before the next animation begins.
- Labels are placed over axes, curves, point clouds, shaded bands, or aquifer/object geometry.
- Any scene omits `Frame zones`, `Keep-clear pairs`, `Transition-frame audit`, or `Layout guard`.
- A text/data scene omits its own `assert_scene_layout` runtime call, or a pure-geometry scene omits its own `assert_within_frame` call; a guard elsewhere does not count.
- Any settled-state transition uses `.animate`; the strict checker requires a separately constructed, positioned, and guarded target copy followed by an explicit same-object transform.
- Transition entry, midpoint, and settled frames have not been reviewed and recorded in the QA manifest.
- Numbered scene helpers do not map one-to-one, in order, and by `Bxx`/`Mxx`/narrative ownership to storyboard scenes, or manifest hashes do not match the packaged Manim source, storyboard, research source, semantic audit, contact sheet, frames, and MP4.
- Axes, labels, support-volume rings, halos, or uncertainty bands cross into the wrong scientific object without an explicit `assert_inside` or equivalent boundary guard.
- The output is only a GitHub blob URL instead of a release asset or verified browser-playable file.
- The HTML player uses a portrait contact sheet as a video poster, lacks a direct MP4 link, or lacks a user-initiated play control.
- Live publication reuses an existing release/tag, uses `--clobber`, or uploads the originally validated paths without staged revalidation.
- Storyboard content is sent to Gemini or artifacts are published to GitHub without explicit user authorization.

## Scripts

- `scripts/check_storyboard_contract.py`: scored 3B1B narrative rubric.
- `scripts/storyboard_semantic_audit.py`: independent source-passage evidence validator used by strict mode.
- `scripts/storyboard_visual_audit.py`: signed scene-object and ownership comparison against the storyboard.
- `scripts/video_frame_evidence.py`: frame-file hashes, global uniqueness, and exact MP4 decoding validator.
- `scripts/check_manim_layout.py`: static Manim layout-risk checker with optional contact-sheet inspection.
- `scripts/export_manim_video.py`: browser-ready MP4 export package.
- `scripts/publish_video_release.py`: GitHub Release asset publisher with `--dry-run`.
- `references/gemini-3b1b-storyboard-review-prompt.md`: optional external Gemini prompt for 3B1B-style storyboard critique.
